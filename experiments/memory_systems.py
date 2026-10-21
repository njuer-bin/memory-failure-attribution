"""Comparable memory systems for the cross-system Failure Fingerprint study.

Every system exposes the same three operations, so the same questions, judge,
gate and tracer can be applied:

- ``ingest(record)`` — consume the benchmark conversation;
- ``search(question)`` — return retrieval candidates, reranked items and the
  final context;
- ``stages(gold)`` — artifact lists for formation/storage/retrieval/rerank/
  context, plus an evolution stage that is explicitly unmeasured.

Systems included:

- ``semantic`` — the project engine (semantic facts + provenance + governance);
- ``verbatim`` — raw turns only (a classic windowed RAG baseline);
- ``summary`` — one LLM summary per session (no provenance, lossy by design).

The point is not to compete with the engine, but to ask whether systems with
similar QA accuracy fail in different lifecycle stages.
"""
from __future__ import annotations

import math
from typing import Any

from evaluation.answer_generation import ANSWER_API_STYLE, BASE_URL, MODEL, TIMEOUT
from evaluation.llm_api import completion
from memory_engine.vector import EmbeddingProvider
from tracing.engine_trace import stage_match


def _sessions(record: dict[str, Any]) -> list[dict[str, Any]]:
    result = []
    for i, session in enumerate(record.get("conversation") or []):
        if not isinstance(session, dict):
            continue
        sid = str(session.get("session_id") or session.get("id") or f"session_{i}")
        date = session.get("date") or session.get("timestamp")
        messages = session.get("messages") or session.get("turns") or []
        result.append({"session_id": sid, "date": date, "messages": list(messages)})
    return result


def _text(message: Any) -> str:
    if isinstance(message, dict):
        return str(message.get("content") or message.get("text") or "").strip()
    return str(message or "").strip()


def _role(message: Any) -> str:
    return str(message.get("role") or message.get("speaker") or "user") if isinstance(message, dict) else "user"


def _cosine(a: list[float], b: list[float]) -> float:
    dot = sum(x * y for x, y in zip(a, b))
    na = math.sqrt(sum(x * x for x in a))
    nb = math.sqrt(sum(y * y for y in b))
    return dot / (na * nb) if na and nb else 0.0


class _EmbeddingSystem:
    def __init__(self) -> None:
        self.embedder = EmbeddingProvider()
        self.items: list[dict[str, Any]] = []

    def _add(self, *, content: str, session_id: str, turn_id: str | None,
             timestamp: Any, memory_type: str) -> None:
        if not content:
            return
        self.items.append({
            "id": f"{memory_type}_{len(self.items)}",
            "content": content,
            "session_id": session_id,
            "source_session_id": session_id,
            "source_turn_id": turn_id,
            "timestamp": timestamp,
            "memory_type": memory_type,
            "vector": self.embedder.embed(content),
        })

    def search(self, question: str, *, candidate_k: int = 20, top_k: int = 10) -> dict[str, Any]:
        qv = self.embedder.embed(question)
        ranked = sorted(self.items, key=lambda item: _cosine(qv, item["vector"]), reverse=True)
        clean = [{k: v for k, v in item.items() if k != "vector"} for item in ranked]
        return {
            "retrieval": clean[:candidate_k],
            "rerank": clean[:top_k],
            "context": clean[:top_k],
        }

    def stages(self, gold: list[dict[str, Any]], search: dict[str, Any]) -> dict[str, Any]:
        raise NotImplementedError


class VerbatimSystem(_EmbeddingSystem):
    name = "verbatim"

    def ingest(self, record: dict[str, Any]) -> None:
        for session in _sessions(record):
            for j, message in enumerate(session["messages"]):
                self._add(
                    content=_text(message),
                    session_id=session["session_id"],
                    turn_id=f"{session['session_id']}:turn_{j}",
                    timestamp=session.get("date"),
                    memory_type="raw",
                )

    def stages(self, gold: list[dict[str, Any]], search: dict[str, Any]) -> dict[str, Any]:
        formation = self.items
        return {
            "formation": formation,
            "storage": formation,
            "evolution": [],
            "retrieval": search["retrieval"],
            "rerank": search["rerank"],
            "context": search["context"],
        }


SUMMARY_PROMPT = (
    "Summarize the factual content of this conversation session. Preserve every "
    "name, date, number, preference and change of state exactly; do not infer. "
    "Output only the summary.\n\n"
)


class SummarySystem(_EmbeddingSystem):
    name = "summary"

    def ingest(self, record: dict[str, Any]) -> None:
        for session in _sessions(record):
            lines = []
            for message in session["messages"]:
                text = _text(message)
                if text:
                    lines.append(f"{_role(message)}: {text}")
            if not lines:
                continue
            body = "\n".join(lines)
            try:
                summary = completion(
                    SUMMARY_PROMPT + body, MODEL,
                    base_url=BASE_URL, style=ANSWER_API_STYLE, timeout=TIMEOUT,
                    origin_hint="summary memory",
                ).strip()
            except Exception:
                summary = body
            self._add(
                content=summary or body,
                session_id=session["session_id"],
                turn_id=None,
                timestamp=session.get("date"),
                memory_type="summary",
            )

    def stages(self, gold: list[dict[str, Any]], search: dict[str, Any]) -> dict[str, Any]:
        summaries = self.items
        return {
            "formation": summaries,
            "storage": summaries,
            "evolution": [],
            "retrieval": search["retrieval"],
            "rerank": search["rerank"],
            "context": search["context"],
        }


def stage_dict(
    system_stages: dict[str, Any],
    gold: list[dict[str, Any]],
    *,
    mode: str,
    evolution_measured: bool = False,
) -> dict[str, Any]:
    """Turn artifact lists into the trace shape ``evaluate`` consumes."""
    output: dict[str, Any] = {}
    for stage in ("formation", "storage", "evolution", "retrieval", "rerank", "context"):
        match = stage_match(gold, system_stages.get(stage) or [])
        details = {
            "mode": mode,
            "observed_count": match["observed_count"],
            "match_types": match.get("match_types", {}),
            "provenance_only": match.get("provenance_only", []),
            "unverified_provenance": match.get("unverified_provenance", []),
        }
        if stage == "evolution":
            details["measured"] = evolution_measured
        output[stage] = {"found": match["found"], "missing": match["missing"], "details": details}
    return output


SYSTEMS = {"verbatim": VerbatimSystem, "summary": SummarySystem}


class SemanticSystem:
    """The project engine, wrapped so it can run inside the cross-system runner.

    Running it here (rather than reusing an older oracle run) is required for a
    fair fingerprint: separate runs of the same questions differ by more than
    the system effects at n=50.
    """

    name = "semantic"

    def __init__(self) -> None:
        from pathlib import Path

        from memory_engine.engine import MemoryEngine
        import uuid

        self.root = Path(__file__).resolve().parents[1]
        data_dir = self.root / "data"
        data_dir.mkdir(parents=True, exist_ok=True)
        self.user_id = f"sys_{uuid.uuid4().hex}"
        self.engine = MemoryEngine(str(data_dir / f"system_{uuid.uuid4().hex}.db"))

    def ingest(self, record: dict[str, Any]) -> None:
        from memory_engine.models import AddMessage, AddRequest
        from experiments.run_oracle_experiments import _timestamp_ms

        for session in _sessions(record):
            messages = []
            for message in session["messages"]:
                content = _text(message)
                if not content:
                    continue
                messages.append(AddMessage(
                    role=_role(message), content=content,
                    timestamp=_timestamp_ms(session.get("date")),
                ))
            if messages:
                self.engine.add(AddRequest(
                    request_id=f"{self.user_id}:{session['session_id']}",
                    messages=messages, user_id=self.user_id,
                    session_id=session["session_id"],
                ))

    def search(self, question: str) -> dict[str, Any]:
        from memory_engine.models import SearchRequest
        from tracing.engine_trace import retrieval_artifacts

        results = self.engine.search(SearchRequest(
            query=question, user_id=self.user_id, top_k=10, multi_hop=True,
        ))
        trace = self.engine.last_search_trace or {}
        return {
            "retrieval": trace.get("retrieval_candidates") or retrieval_artifacts(results),
            "rerank": trace.get("reranked") or retrieval_artifacts(results),
            "context": trace.get("context") or retrieval_artifacts(results),
        }

    def stages(self, gold: list[dict[str, Any]], search: dict[str, Any]) -> dict[str, Any]:
        from tracing.engine_trace import artifacts_from_store, active_fact_artifacts

        stored = artifacts_from_store(self.engine, self.user_id)
        formation = (stored["facts"] + stored["relations"] + stored["events"]
                     + stored["rules"] + stored["profiles"])
        return {
            "formation": formation,
            "storage": stored["raw"] + formation,
            "evolution": active_fact_artifacts(self.engine, self.user_id),
            "retrieval": search["retrieval"],
            "rerank": search["rerank"],
            "context": search["context"],
        }


SYSTEMS["semantic"] = SemanticSystem
