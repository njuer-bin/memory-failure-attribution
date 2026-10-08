"""Run an end-to-end lifecycle probe on LongMemEval records.

This is intentionally a diagnostic runner, not the final benchmark harness.
It establishes a reproducible Real-Memory trace before adding oracle controls.

Usage:
    python -m experiments.run_lifecycle_probe --dataset longmemeval_s_sample10 --limit 3
"""
from __future__ import annotations

import argparse
import json
import re
import uuid
from pathlib import Path
from typing import Any

from datasets.loader import iter_normalized
from memory_engine.engine import MemoryEngine
from memory_engine.models import AddMessage, AddRequest, SearchRequest
from tracing.dataset_trace import record_to_trace
from tracing.failure_attribution import attribute_failure


ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "results" / "traces" / "real_memory.jsonl"


def _message_parts(message: Any) -> tuple[str, str, int | None]:
    if isinstance(message, dict):
        role = str(message.get("role") or message.get("speaker") or "user")
        text = str(message.get("content") or message.get("text") or message.get("message") or "")
        ts = message.get("timestamp")
        if isinstance(ts, str) and ts.isdigit():
            ts = int(ts)
        return role, text, ts if isinstance(ts, int) else None
    return "user", str(message), None


def _sessions(record: dict[str, Any]) -> list[dict[str, Any]]:
    conversation = record.get("conversation") or []
    result = []
    for i, session in enumerate(conversation):
        if isinstance(session, dict):
            sid = str(session.get("session_id") or session.get("id") or f"session_{i}")
            messages = session.get("messages") or session.get("turns") or []
        else:
            sid, messages = f"session_{i}", session
        if isinstance(messages, dict):
            messages = [messages]
        result.append({"session_id": sid, "messages": list(messages or [])})
    return result


def _stage_observed(gold: list[dict[str, Any]], artifacts: list[dict[str, Any]]) -> dict[str, Any]:
    gold_ids = {str(x.get("evidence_id")): str(x.get("source_id") or "") for x in gold}
    found = []
    for gid, source in gold_ids.items():
        if source and any(str(a.get("source_id") or "") == source for a in artifacts):
            found.append(gid)
    return {
        "found": sorted(found),
        "missing": sorted(set(gold_ids) - set(found)),
        "observed_count": len(artifacts),
    }


def run_record(engine: MemoryEngine, record: dict[str, Any], user_id: str) -> dict[str, Any]:
    trace = record_to_trace(record)
    sessions = _sessions(record)

    # Formation: inspect what the analyzer actually extracts from each source session.
    formation_artifacts = []
    for session in sessions:
        for msg in session["messages"]:
            role, text, ts = _message_parts(msg)
            if not text:
                continue
            analyzed = engine.analyzer.analyze(user_id, text, ts or 0, source=role)
            for key in ("facts", "relations", "events", "rules", "profiles"):
                for item in analyzed.get(key, []):
                    formation_artifacts.append({
                        "source_id": session["session_id"],
                        "content": getattr(item, "content", str(item)),
                        "memory_type": key,
                    })
    trace.formation = type(trace.formation)(**_stage_observed(trace.to_dict()["gold_evidence"], formation_artifacts))

    # Storage: raw session memories are the authoritative persisted source.
    stored = engine.store.all_raw(user_id)
    storage_artifacts = [
        {"source_id": row.get("session_id"), "content": row.get("content"), "id": row.get("id")}
        for row in stored
    ]
    trace.storage = type(trace.storage)(**_stage_observed(trace.to_dict()["gold_evidence"], storage_artifacts))

    # Evolution: active structured facts/events are retained; this stage is kept
    # explicit so future temporal/conflict experiments can distinguish stale loss.
    evolved = engine.store.active_facts(user_id, include_history=True) + engine.store.events(user_id)
    evolution_artifacts = [
        {"source_id": row.get("session_id") or row.get("source"), "content": row.get("content")}
        for row in evolved
    ]
    trace.evolution = type(trace.evolution)(**_stage_observed(trace.to_dict()["gold_evidence"], evolution_artifacts))

    results = engine.search(
        SearchRequest(
            query=record["question"],
            user_id=user_id,
            top_k=10,
            multi_hop=True,
        )
    )
    retrieval_artifacts = [
        {
            "source_id": row.get("session_id") or row.get("source"),
            "content": row.get("content"),
            "id": row.get("id"),
        }
        for row in results
    ]
    trace.retrieval = type(trace.retrieval)(**_stage_observed(trace.to_dict()["gold_evidence"], retrieval_artifacts))
    trace.rerank = trace.retrieval
    trace.context = trace.retrieval
    trace.answer = {
        "correct": None,
        "answer": None,
        "mode": "search-only-diagnostic",
    }
    trace.failure_type = attribute_failure(trace.to_dict())
    return trace.to_dict()


def run(dataset: str, limit: int) -> list[dict[str, Any]]:
    OUT.parent.mkdir(parents=True, exist_ok=True)
    rows = []
    for idx, record in enumerate(iter_normalized(dataset, limit=limit)):
        user_id = f"probe_{uuid.uuid4().hex}"
        engine = MemoryEngine(f"data/probe_{idx}_{uuid.uuid4().hex}.db")
        for session in _sessions(record):
            messages = []
            for msg in session["messages"]:
                role, text, ts = _message_parts(msg)
                if text:
                    messages.append(AddMessage(role=role, content=text, timestamp=ts))
            if not messages:
                continue
            engine.add(
                AddRequest(
                    request_id=f"{user_id}:{session['session_id']}",
                    messages=messages,
                    user_id=user_id,
                    session_id=session["session_id"],
                )
            )
        rows.append(run_record(engine, record, user_id))
    with OUT.open("w", encoding="utf-8") as f:
        for row in rows:
            f.write(json.dumps(row, ensure_ascii=False) + "\n")
    return rows


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--dataset", default="longmemeval_s_sample10")
    parser.add_argument("--limit", type=int, default=3)
    args = parser.parse_args()
    rows = run(args.dataset, args.limit)
    counts = {}
    for row in rows:
        counts[row.get("failure_type")] = counts.get(row.get("failure_type"), 0) + 1
    print(json.dumps({"records": len(rows), "failure_distribution": counts, "output": str(OUT)}, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
