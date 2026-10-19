"""Run evidence-boundary control experiments with an explicit E0 gate."""
from __future__ import annotations

import argparse
import json
import time
import traceback
import uuid
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from datasets.loader import iter_normalized
from evaluation import attribution
from evaluation.answer_generation import generate_and_score
from evaluation.answer_semantic_eval import evaluate_answer
from evaluation.lifecycle_metrics import MEASURED_STAGES, stage_recall, summarize_traces
from memory_engine.engine import MemoryEngine
from memory_engine.models import AddMessage, AddRequest, SearchRequest
from tracing.dataset_trace import record_to_trace
from tracing.engine_trace import artifacts_from_store, retrieval_artifacts, stage_match
from tracing.lifecycle import match_evidence

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "results" / "oracle_experiments"


def log(message: str) -> None:
    print(message, flush=True)


def _sessions(record: dict[str, Any]) -> list[dict[str, Any]]:
    conversation = record.get("conversation") or []
    result: list[dict[str, Any]] = []
    for i, session in enumerate(conversation):
        if isinstance(session, dict):
            sid = str(session.get("session_id") or session.get("id") or f"session_{i}")
            messages = session.get("messages") or session.get("turns") or []
            session_date = session.get("date") or session.get("timestamp") or session.get("date_time")
        else:
            sid, messages = f"session_{i}", session
            session_date = None
        if isinstance(messages, dict):
            messages = [messages]
        result.append({"session_id": sid, "date": session_date, "messages": list(messages or [])})
    return result


def _timestamp_ms(value: Any) -> int | None:
    """Normalize benchmark timestamps to the engine's Unix-millisecond format."""
    if isinstance(value, bool):
        return None
    if isinstance(value, int):
        # Engine timestamps are milliseconds; tolerate epoch seconds in external data.
        return value * 1000 if 0 < value < 100_000_000_000 else value
    if not isinstance(value, str) or not value.strip():
        return None

    raw = value.strip()
    formats = (
        "%I:%M %p on %d %B, %Y",
        "%I:%M %p on %d %b, %Y",
        "%I:%M %p on %B %d, %Y",
        "%I:%M %p on %b %d, %Y",
        "%d %B, %Y",
        "%d %b, %Y",
        "%B %d, %Y",
        "%b %d, %Y",
        "%Y-%m-%d",
    )
    parsed = None
    for fmt in formats:
        try:
            parsed = datetime.strptime(raw, fmt)
            break
        except ValueError:
            continue
    if parsed is None:
        try:
            parsed = datetime.fromisoformat(raw.replace("Z", "+00:00"))
        except ValueError:
            return None
    if parsed.tzinfo is None:
        parsed = parsed.replace(tzinfo=timezone.utc)
    return int(parsed.timestamp() * 1000)


def _msg(m: Any) -> tuple[str, str, int | None]:
    if isinstance(m, dict):
        role = str(m.get("role") or m.get("speaker") or "user")
        text = str(m.get("content") or m.get("text") or m.get("message") or "")
        ts = _timestamp_ms(m.get("timestamp") or m.get("session_date_time") or m.get("date"))
        return role, text, ts
    return "user", str(m), None


def _gold_artifacts(record: dict[str, Any]) -> list[dict[str, Any]]:
    return [
        {
            "id": str(e["evidence_id"]),
            "content": str(e.get("text") or ""),
            "source_id": e.get("source_id"),
            "turn_id": e.get("turn_id"),
            "role": e.get("role", ""),
            "timestamp": e.get("timestamp"),
            "memory_type": "oracle",
        }
        for e in record.get("gold_evidence", [])
        if e.get("evidence_id") and e.get("text")
    ]


def _stage(gold: list[dict[str, Any]], artifacts: list[dict[str, Any]], mode: str) -> dict[str, Any]:
    match = stage_match(gold, artifacts)
    return {
        "found": match["found"],
        "missing": match["missing"],
        "details": {
            "mode": mode,
            "observed_count": match["observed_count"],
            "match_types": match.get("match_types", {}),
            "match_scores": match.get("match_scores", {}),
            "provenance_only": match.get("provenance_only", []),
            "unverified_provenance": match.get("unverified_provenance", []),
            "matches": match["matches"],
        },
    }


def _real_engine(record: dict[str, Any], idx: int) -> tuple[MemoryEngine, str]:
    user_id = f"oracle_{idx}_{uuid.uuid4().hex}"
    data_dir = ROOT / "data"
    data_dir.mkdir(parents=True, exist_ok=True)
    db_path = data_dir / f"oracle_{idx}_{uuid.uuid4().hex}.db"

    log(f"    [engine] initializing MemoryEngine: {db_path.name}")
    t0 = time.perf_counter()
    engine = MemoryEngine(str(db_path))
    log(f"    [engine] initialized in {time.perf_counter() - t0:.2f}s")

    sessions = _sessions(record)
    log(f"    [ingest] {len(sessions)} sessions")
    t0 = time.perf_counter()
    message_count = 0
    for session in sessions:
        messages = []
        for raw in session["messages"]:
            # LoCoMo often stores the event date on the session rather than on each message.
            if isinstance(raw, dict) and not (raw.get("timestamp") or raw.get("session_date_time") or raw.get("date")):
                raw = dict(raw)
                raw["timestamp"] = session.get("date")
            role, text, ts = _msg(raw)
            if text:
                messages.append(AddMessage(role=role, content=text, timestamp=ts))
        if messages:
            message_count += len(messages)
            engine.add(AddRequest(
                request_id=f"{user_id}:{session['session_id']}",
                messages=messages,
                user_id=user_id,
                session_id=session["session_id"],
            ))
    log(f"    [ingest] {message_count} messages in {time.perf_counter() - t0:.2f}s")
    return engine, user_id


def _content_match(evidence: dict[str, Any], artifacts: list[dict[str, Any]]) -> dict[str, Any]:
    """Match evidence by content only, ignoring provenance for diagnostic classification."""
    content_only = dict(evidence)
    for key in ("source_id", "source", "turn_id", "source_turn_id", "source_raw_id", "raw_id"):
        content_only.pop(key, None)
    result = match_evidence([content_only], artifacts)
    evidence_id = str(content_only.get("evidence_id") or "")
    return {
        "matched": evidence_id in result["found"],
        "match_type": result.get("match_types", {}).get(evidence_id),
        "match_score": result.get("match_scores", {}).get(evidence_id, 0.0),
        "artifact": result.get("matches", {}).get(evidence_id),
    }


def _formation_diagnostics(gold: list[dict[str, Any]], stored: dict[str, list[dict[str, Any]]]) -> list[dict[str, Any]]:
    """Diagnose target-evidence formation using turn provenance and content.

    A memory elsewhere in the session is not sufficient evidence of a
    representation mismatch: its content must match the gold evidence.
    """
    semantic = stored["facts"] + stored["relations"] + stored["events"] + stored["rules"] + stored["profiles"]
    raw = stored["raw"]
    diagnostics = []
    for evidence in gold:
        source_id = str(evidence.get("source_id") or evidence.get("source") or "")
        turn_id = str(evidence.get("turn_id") or evidence.get("turn") or "")

        # If the benchmark supplies a turn id, require that exact turn.
        # Never fall back to another message from the same session.
        if turn_id:
            raw_matches = [
                item for item in raw
                if str(item.get("source_turn_id") or item.get("turn_id") or "") == turn_id
            ]
        elif source_id:
            raw_matches = [
                item for item in raw
                if str(item.get("source_id") or item.get("session_id") or "") == source_id
            ]
        else:
            raw_matches = []

        turn_semantic = [
            item for item in semantic
            if turn_id and str(item.get("source_turn_id") or item.get("turn_id") or "") == turn_id
        ]
        session_semantic = [
            item for item in semantic
            if source_id and str(item.get("source_session_id") or item.get("source_id") or item.get("session_id") or "") == source_id
        ]

        turn_content_match = _content_match(evidence, turn_semantic)
        session_content_match = _content_match(evidence, session_semantic)

        if not raw_matches:
            classification = "F1d_UNKNOWN"
        elif turn_content_match["matched"]:
            classification = "FORMATION_OK"
        elif session_content_match["matched"]:
            # The target content exists in this session, but not at its source turn.
            classification = "F1c_REPRESENTATION_MISMATCH"
        else:
            # Unrelated semantic memories in the same session do not prove a
            # representation mismatch; treat this as a candidate extractor miss.
            classification = "F1a_EXTRACTOR_MISS"

        diagnostics.append({
            "gold_evidence_id": evidence.get("evidence_id"),
            "source_session_id": source_id or None,
            "source_turn_id": turn_id or None,
            "source_message_found": bool(raw_matches),
            "source_message_count": len(raw_matches),
            "semantic_memory_count_same_turn": len(turn_semantic),
            "semantic_memory_count_same_session": len(session_semantic),
            "semantic_memory_ids_same_turn": [str(x.get("id")) for x in turn_semantic if x.get("id")],
            "semantic_memory_types_same_turn": [str(x.get("memory_type") or "") for x in turn_semantic],
            "semantic_memory_match_same_turn": {
                "matched": turn_content_match["matched"],
                "match_type": turn_content_match["match_type"],
                "match_score": turn_content_match["match_score"],
                "memory_id": (turn_content_match["artifact"] or {}).get("id"),
            },
            "semantic_memory_match_same_session": {
                "matched": session_content_match["matched"],
                "match_type": session_content_match["match_type"],
                "match_score": session_content_match["match_score"],
                "memory_id": (session_content_match["artifact"] or {}).get("id"),
            },
            "semantic_memory_candidates_same_session": [
                {
                    "id": str(x.get("id")) if x.get("id") else None,
                    "memory_type": str(x.get("memory_type") or ""),
                    "source_turn_id": x.get("source_turn_id") or x.get("turn_id"),
                    "content": str(x.get("content") or "")[:240],
                }
                for x in session_semantic[:20]
            ],
            "classification": classification,
        })
    return diagnostics

def _real_trace_stages(trace: Any, gold: list[dict[str, Any]], engine: MemoryEngine, user_id: str, real: list[dict[str, Any]], search_trace: dict[str, Any]) -> None:
    stored = artifacts_from_store(engine, user_id)
    formation = stored["facts"] + stored["relations"] + stored["events"] + stored["rules"] + stored["profiles"]
    storage = stored["raw"] + formation
    evolution = formation
    trace.formation = type(trace.formation)(**_stage(gold, formation, "real_memory"))
    trace.formation.details["diagnostics"] = _formation_diagnostics(gold, stored)
    trace.formation.details["semantic_memory_counts"] = {
        "total": len(formation),
        "by_type": {
            "fact": len(stored["facts"]), "relation": len(stored["relations"]),
            "event": len(stored["events"]), "rule": len(stored["rules"]),
            "profile": len(stored["profiles"]),
        },
    }
    trace.storage = type(trace.storage)(**_stage(gold, storage, "real_memory"))
    # Audit C4: no evolution operations are applied by the tracing layer, so
    # the evolution stage is a copy of formation and F3 cannot fire. It is
    # kept for structure only and explicitly marked unmeasured.
    trace.evolution = type(trace.evolution)(**_stage(gold, evolution, "real_memory"))
    trace.evolution.details["measured"] = False
    retrieval = search_trace.get("retrieval_candidates") or real
    rerank = search_trace.get("reranked") or real
    context = search_trace.get("context") or real
    trace.retrieval = type(trace.retrieval)(**_stage(gold, retrieval, "real_memory_retrieval_candidates"))
    trace.rerank = type(trace.rerank)(**_stage(gold, rerank, "real_memory_reranked"))
    trace.context = type(trace.context)(**_stage(gold, context, "real_memory_context"))


def _oracle_memory_engine(gold: list[dict[str, Any]], record: dict[str, Any], idx: int, question: str) -> tuple[dict[str, Any], list[dict[str, Any]]]:
    """Oracle Memory: gold evidence is stored directly, then retrieved by the
    real search pipeline.

    Unlike Oracle Context, this condition still exercises retrieval, reranking,
    and context assembly, so it isolates downstream memory-path failures
    (audit C6). Extraction is bypassed by inserting the gold turns as raw
    memories; the direct-write path is intentional and is reported as a
    controlled (unmeasured) formation/storage condition.
    """
    user_id = f"oracle_mem_{idx}_{uuid.uuid4().hex}"
    data_dir = ROOT / "data"
    data_dir.mkdir(parents=True, exist_ok=True)
    engine = MemoryEngine(str(data_dir / f"oracle_mem_{idx}_{uuid.uuid4().hex}.db"))
    default_ts = _timestamp_ms(record.get("question_date")) or 0
    request_id = f"{user_id}:gold_evidence"
    for pos, evidence in enumerate(gold):
        text = str(evidence.get("text") or "")
        if not text:
            continue
        evidence_id = str(evidence.get("evidence_id") or pos)
        engine.store.insert_raw({
            "id": f"{user_id}:{evidence_id}",
            "request_id": request_id,
            "user_id": user_id,
            "session_id": str(evidence.get("source_id") or evidence.get("source") or f"{user_id}:gold"),
            "role": str(evidence.get("role") or "user"),
            "content": text,
            "timestamp": _timestamp_ms(evidence.get("timestamp")) or default_ts,
            "chunk_index": 0,
            "source_turn_id": evidence.get("turn_id"),
        })

    stored = artifacts_from_store(engine, user_id)
    formation_artifacts = stored["raw"]
    formation = _stage(gold, formation_artifacts, "oracle_memory_direct_write")
    formation["details"]["measured"] = False
    storage = _stage(gold, formation_artifacts, "oracle_memory_direct_write")
    storage["details"]["measured"] = False
    evolution = _stage(gold, formation_artifacts, "oracle_memory_direct_write")
    evolution["details"]["measured"] = False

    results = engine.search(SearchRequest(query=question, user_id=user_id, top_k=10, multi_hop=True))
    artifacts = retrieval_artifacts(results)
    search_trace = engine.last_search_trace
    stages = {
        "formation": formation,
        "storage": storage,
        "evolution": evolution,
        "retrieval": _stage(gold, search_trace.get("retrieval_candidates") or artifacts, "oracle_memory"),
        "rerank": _stage(gold, search_trace.get("reranked") or artifacts, "oracle_memory"),
        "context": _stage(gold, search_trace.get("context") or artifacts, "oracle_memory_context"),
    }
    context = search_trace.get("context") or artifacts
    return stages, context


def _oracle_context_trace(gold: list[dict[str, Any]], oracle: list[dict[str, Any]]) -> dict[str, Any]:
    result = {}
    for stage in ("formation", "storage", "evolution", "retrieval", "rerank"):
        result[stage] = _stage(gold, [], "oracle_context_not_measured")
        result[stage]["details"]["measured"] = False
    result["context"] = _stage(gold, oracle, "oracle_context")
    return result


def _evidence_sufficiency(question: str, benchmark_answer: str, gold: list[dict[str, Any]]) -> dict[str, Any]:
    """Unified non-circular gate: judged against the benchmark reference answer."""
    return attribution.evidence_sufficiency_gate(question, benchmark_answer, gold)


def _score_mode_answer(question: str, reference: str, context: list[dict[str, Any]]) -> dict[str, Any]:
    try:
        return generate_and_score(question, reference, context)
    except Exception as exc:
        return {"answer": None, "correct": None, "exact_match": None, "token_f1": None, "threshold": None, "model_error": f"{type(exc).__name__}: {exc}"}


def _lexical_skip_is_safe(answer: dict[str, Any]) -> bool:
    """Whether lexical correctness is strong enough to skip the judge (audit C5).

    A token-F1 at the 0.5 threshold is not correctness: "Six weeks" scored 0.5
    against the reference "Four weeks" and was recorded as a non-failure. Only an
    exact match, or a near-exact overlap, may bypass the judge.
    """
    if answer.get("exact_match") == 1.0:
        return True
    f1 = answer.get("token_f1")
    return isinstance(f1, (int, float)) and f1 >= 0.8


def _semantic_fields(verdict: dict[str, Any]) -> dict[str, Any]:
    """Map an evaluator verdict onto the field names a stored answer carries."""
    return {
        "semantic_correct": verdict.get("correct"),
        "semantic_judge_correct": verdict.get("judge_correct"),
        "semantic_evidence_sufficient": verdict.get("evidence_sufficient"),
        "semantic_confidence": verdict.get("confidence"),
        "semantic_reason": verdict.get("reason"),
        "semantic_adjudication": verdict.get("adjudication"),
        "semantic_adjudication_anchor": verdict.get("adjudication_anchor"),
        "semantic_judge_model": verdict.get("model"),
    }


def _semantic_eval(
    question: str,
    answer: dict[str, Any],
    gold: list[dict[str, Any]],
    gold_answer: str | None = None,
) -> dict[str, Any]:
    """Attach the semantic verdict to an already-scored answer.

    Answers whose lexical correctness is beyond token-overlap doubt skip the judge
    (correct is correct); everything else gets the semantic verdict that the
    attribution protocol consumes.
    """
    if answer.get("correct") is True and _lexical_skip_is_safe(answer):
        return answer
    candidate = str(answer.get("answer") or "").strip()
    if answer.get("model_error") or not candidate:
        answer["semantic_correct"] = None
        answer["semantic_error"] = answer.get("model_error") or "empty answer"
        return answer
    try:
        verdict = evaluate_answer(
            question, candidate, gold, reference_answer=gold_answer,
        )
    except Exception as exc:
        answer["semantic_correct"] = None
        answer["semantic_error"] = f"{type(exc).__name__}: {exc}"
        return answer
    answer.update(_semantic_fields(verdict))
    return answer


def _answer_summary(rows: list[dict[str, Any]], mode: str) -> dict[str, Any]:
    answers = [(r.get("modes", {}).get(mode, {}).get("answer") or {}) for r in rows]
    scored = [a for a in answers if a.get("correct") is not None]
    correct = sum(1 for a in scored if a.get("correct") is True)
    semantic = [a for a in answers if a.get("semantic_correct") is not None]
    semantic_correct = sum(1 for a in semantic if a.get("semantic_correct") is True)
    adjudications: dict[str, int] = {}
    for a in semantic:
        key = str(a.get("semantic_adjudication") or "unknown")
        adjudications[key] = adjudications.get(key, 0) + 1
    return {
        "count": len(answers), "scored": len(scored), "correct": correct,
        "accuracy": correct / len(scored) if scored else None,
        "exact_match": sum(float(a.get("exact_match", 0.0)) for a in scored) / len(scored) if scored else None,
        "token_f1": sum(float(a.get("token_f1", 0.0)) for a in scored) / len(scored) if scored else None,
        "semantic_evaluated": len(semantic),
        "semantic_correct": semantic_correct,
        "semantic_accuracy": semantic_correct / len(semantic) if semantic else None,
        "semantic_adjudications": adjudications,
        "model_errors": sum(1 for a in answers if a.get("model_error")),
        "semantic_errors": sum(1 for a in answers if a.get("semantic_error")),
    }


def _answer_failure_distribution(rows: list[dict[str, Any]], mode: str) -> dict[str, int]:
    counts: dict[str, int] = {}
    for row in rows:
        failure = row.get("modes", {}).get(mode, {}).get("answer_failure_type")
        if failure:
            counts[failure] = counts.get(failure, 0) + 1
    return counts


def _first_answer_failure_distribution(rows: list[dict[str, Any]]) -> dict[str, int]:
    return _answer_failure_distribution(rows, "real_memory")


def run_record(record: dict[str, Any], idx: int) -> dict[str, Any]:
    trace = record_to_trace(record)
    gold = [e.__dict__ for e in trace.gold_evidence]
    oracle = _gold_artifacts(record)

    log("    [real] building memory")
    engine, user_id = _real_engine(record, idx)
    log("    [real] reading lifecycle artifacts")
    t0 = time.perf_counter()
    log("    [real] retrieval")
    results = engine.search(SearchRequest(query=record["question"], user_id=user_id, top_k=10, multi_hop=True))
    real = retrieval_artifacts(results)
    log(f"    [real] retrieval done in {time.perf_counter() - t0:.2f}s; artifacts={len(real)}")

    _real_trace_stages(trace, gold, engine, user_id, real, engine.last_search_trace)
    search_trace = engine.last_search_trace
    real_context = search_trace.get("context") or real
    real_answer = _score_mode_answer(record["question"], record.get("answer", ""), real_context)
    oracle_memory_stages, oracle_memory_context = _oracle_memory_engine(gold, record, idx, record["question"])
    oracle_memory_answer = _score_mode_answer(record["question"], record.get("answer", ""), oracle_memory_context)
    oracle_context_answer = _score_mode_answer(record["question"], record.get("answer", ""), oracle)

    gate = _evidence_sufficiency(record["question"], record.get("answer", ""), gold)
    real_answer = _semantic_eval(record["question"], real_answer, gold, record.get("answer", ""))
    oracle_memory_answer = _semantic_eval(record["question"], oracle_memory_answer, gold, record.get("answer", ""))
    oracle_context_answer = _semantic_eval(record["question"], oracle_context_answer, gold, record.get("answer", ""))
    trace.answer = {**real_answer, "mode": "real_memory", "answer_scoring": "token_f1_plus_temporal_phrase_rules"}
    trace.failure_type = attribution.attribute_failure(
        trace.answer, gate, trace.to_dict(), gold, mode="real_memory",
    )

    real_mode = {
        "formation": trace.formation.to_dict(), "storage": trace.storage.to_dict(),
        "evolution": trace.evolution.to_dict(), "retrieval": trace.retrieval.to_dict(),
        "rerank": trace.rerank.to_dict(), "context": trace.context.to_dict(),
        "failure_type": trace.failure_type, "answer": real_answer,
        "evidence_sufficiency": gate,
    }
    oracle_memory = oracle_memory_stages
    oracle_memory.update({
        "answer": {**oracle_memory_answer, "mode": "oracle_memory", "answer_scoring": "token_f1_plus_temporal_phrase_rules"},
        "evidence_sufficiency": gate,
    })
    oracle_context = _oracle_context_trace(gold, oracle)
    oracle_context.update({
        "answer": {**oracle_context_answer, "mode": "oracle_context", "answer_scoring": "token_f1_plus_temporal_phrase_rules"},
        "evidence_sufficiency": gate,
    })

    row = {
        "question_id": trace.question_id, "question": trace.question,
        "gold_answer": record.get("answer", ""),
        "modes": {"real_memory": real_mode, "oracle_memory": oracle_memory, "oracle_context": oracle_context},
        "gold_evidence_count": len(gold), "gold_evidence": gold,
    }
    for mode in ("real_memory", "oracle_memory", "oracle_context"):
        mode_data = row["modes"][mode]
        row["modes"][mode]["answer_failure_type"] = attribution.attribute_failure(
            mode_data["answer"], gate, mode_data, gold, mode=mode,
        )
    return row


def _write_jsonl(path: Path, row: dict[str, Any]) -> None:
    with path.open("a", encoding="utf-8") as f:
        f.write(json.dumps(row, ensure_ascii=False) + "\n")
        f.flush()


def _write_progress(path: Path, payload: dict[str, Any]) -> None:
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")


def _mode_trace(row: dict[str, Any], mode: str) -> dict[str, Any]:
    return {"gold_evidence": row.get("gold_evidence", []), **row["modes"][mode]}


def _context_only_summary(rows: list[dict[str, Any]]) -> dict[str, Any]:
    count = len(rows)
    if not count:
        return {"count": 0, "stage_recall": {}, "first_loss_distribution": {"not_applicable": 0}}
    traces = [_mode_trace(row, "oracle_context") for row in rows]
    stage_recall_out: dict[str, float | None] = {}
    for stage in MEASURED_STAGES:
        values = [stage_recall(trace, stage) for trace in traces]
        measured = [v for v in values if v is not None]
        stage_recall_out[stage] = sum(measured) / len(measured) if measured else None
    stage_recall_out["evolution"] = None
    return {
        "count": count,
        "stage_recall": stage_recall_out,
        "unmeasured_stages": ["evolution"],
        "first_loss_distribution": {"not_applicable": count},
    }


def _dataset_digest(dataset: str) -> dict[str, Any]:
    """Digest of the benchmark source file so a run can be tied to exact data."""
    import hashlib
    try:
        from datasets.loader import ROOT as DATASETS_ROOT, dataset_info
        info = dataset_info(dataset)
        source = DATASETS_ROOT / info["source"]
        digest = hashlib.sha256(source.read_bytes()).hexdigest()[:16]
        return {"dataset_id": dataset, "source": str(info["source"]), "sha256_16": digest}
    except Exception as exc:
        return {"dataset_id": dataset, "error": f"{type(exc).__name__}: {exc}"}


def _git_revision() -> dict[str, Any]:
    import subprocess
    result: dict[str, Any] = {}
    for key, args in (("commit", ["rev-parse", "HEAD"]), ("branch", ["rev-parse", "--abbrev-ref", "HEAD"])):
        try:
            result[key] = subprocess.run(
                ["git", *args], cwd=ROOT, capture_output=True, text=True, timeout=10,
            ).stdout.strip() or None
        except Exception:
            result[key] = None
    try:
        dirty = subprocess.run(
            ["git", "status", "--porcelain"], cwd=ROOT, capture_output=True, text=True, timeout=10,
        ).stdout.strip()
        result["dirty"] = bool(dirty)
    except Exception:
        result["dirty"] = None
    return result


def _run_metadata(dataset: str, limit: int) -> dict[str, Any]:
    import sys
    from evaluation.answer_generation import MODEL as ANSWER_MODEL
    from evaluation.answer_semantic_eval import MODEL as JUDGE_MODEL, TEMPERATURE as JUDGE_TEMPERATURE
    return {
        "timestamp_utc": datetime.now(timezone.utc).isoformat(),
        "dataset": _dataset_digest(dataset),
        "limit": limit,
        "answer_model": ANSWER_MODEL,
        "judge_model": JUDGE_MODEL,
        "judge_temperature": JUDGE_TEMPERATURE,
        "python": sys.version.split()[0],
        "git": _git_revision(),
    }


def _build_summary(dataset: str, limit: int, rows: list[dict[str, Any]], errors: int) -> dict[str, Any]:
    gate_counts: dict[str, int] = {}
    for row in rows:
        status = str(row.get("modes", {}).get("real_memory", {}).get("evidence_sufficiency", {}).get("status") or "unknown")
        gate_counts[status] = gate_counts.get(status, 0) + 1
    return {
        "run_metadata": _run_metadata(dataset, limit),
        "dataset": dataset, "limit": limit, "records": len(rows), "errors": errors,
        "real_memory": summarize_traces([_mode_trace(r, "real_memory") for r in rows]) if rows else {},
        "oracle_memory": summarize_traces([_mode_trace(r, "oracle_memory") for r in rows]) if rows else {},
        "oracle_context": _context_only_summary(rows),
        "evidence_sufficiency": {"status_distribution": gate_counts, "gate": "E0 before F1-F6; uncertain/error cases are EVAL"},
        "answer_scoring": {
            "method": "local_ollama_token_f1_plus_temporal_phrase_rules",
            "real_memory": _answer_summary(rows, "real_memory"),
            "oracle_memory": _answer_summary(rows, "oracle_memory"),
            "oracle_context": _answer_summary(rows, "oracle_context"),
            "answer_failure_distribution": {
                mode: _answer_failure_distribution(rows, mode)
                for mode in ("real_memory", "oracle_memory", "oracle_context")
            },
        },
        "note": (
            "Evidence lifecycle and answer scoring are reported separately. "
            "Before F1-F6 attribution, Gold Evidence is checked for question-answer sufficiency "
            "using the benchmark reference answer rather than the model prediction. "
            "Insufficient evidence is E0; uncertain or judge-error cases are EVAL. "
            "F6 is assigned only when the gate is sufficient, all gold evidence reaches final context, "
            "the semantic judge marks the answer incorrect with medium/high confidence. "
            "Evolution recall is not measured (audit C4). Oracle Context remains "
            "a reasoning control and its own wrong answer is RC_REASONING_CONTROL_FAILURE."
        ),
    }


def _load_done_rows(jsonl: Path) -> list[dict[str, Any]]:
    """Read rows already written by an interrupted run, ignoring partial lines."""
    if not jsonl.exists():
        return []
    rows: list[dict[str, Any]] = []
    for line in jsonl.read_text(encoding="utf-8").splitlines():
        if not line.strip():
            continue
        try:
            row = json.loads(line)
        except json.JSONDecodeError:
            continue
        if isinstance(row, dict) and row.get("question_id"):
            rows.append(row)
    return rows


def run(
    dataset: str,
    limit: int,
    out: Path | None = None,
    resume: bool = False,
) -> dict[str, Any]:
    out = out or OUT
    out.mkdir(parents=True, exist_ok=True)
    jsonl = out / "comparison.jsonl"
    progress_path = out / "progress.json"
    summary_path = out / "summary.json"
    rows = _load_done_rows(jsonl) if resume else []
    # Rewrite from the parsed rows so a line truncated by the interrupted process
    # cannot survive into the completed output.
    jsonl.write_text(
        "".join(json.dumps(row, ensure_ascii=False) + "\n" for row in rows),
        encoding="utf-8",
    )
    done = {str(row.get("question_id")) for row in rows}
    errors = 0
    started = time.perf_counter()

    log("=" * 72)
    log(f"Oracle experiment started: dataset={dataset}, limit={limit}")
    log(f"Output: {out}")
    if resume:
        log(f"Resume: {len(rows)} rows already present, {len(done)} question_ids skipped")
    log("=" * 72)
    _write_progress(progress_path, {"status": "running", "dataset": dataset, "limit": limit, "completed": len(rows), "errors": 0, "elapsed_seconds": 0.0})

    for idx, record in enumerate(iter_normalized(dataset, limit=limit)):
        number = idx + 1
        if str(record.get("question_id")) in done:
            log(f"[{number}/{limit}] SKIP already completed question_id={record.get('question_id')}")
            continue
        log(f"\n[{number}/{limit}] START question_id={record.get('question_id')}")
        t0 = time.perf_counter()
        try:
            row = run_record(record, idx)
            rows.append(row)
            _write_jsonl(jsonl, row)
            failure = row["modes"]["real_memory"].get("answer_failure_type")
            log(f"[{number}/{limit}] DONE {time.perf_counter() - t0:.2f}s failure={failure}")
        except Exception as exc:
            errors += 1
            log(f"[{number}/{limit}] ERROR {type(exc).__name__}: {exc}")
            traceback.print_exc()
        _write_progress(progress_path, {
            "status": "running", "dataset": dataset, "limit": limit,
            "completed": len(rows), "errors": errors,
            "elapsed_seconds": time.perf_counter() - started,
        })

    summary = _build_summary(dataset, limit, rows, errors)
    summary["resumed_records"] = len(done)
    summary_path.write_text(json.dumps(summary, ensure_ascii=False, indent=2), encoding="utf-8")
    _write_progress(progress_path, {
        "status": "completed", "dataset": dataset, "limit": limit,
        "completed": len(rows), "errors": errors,
        "elapsed_seconds": time.perf_counter() - started,
    })
    print(json.dumps(summary, ensure_ascii=False, indent=2))
    return summary


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--dataset", default="locomo_refined_public")
    parser.add_argument("--limit", type=int, default=10)
    parser.add_argument(
        "--out-dir",
        default=None,
        help="Output directory. Defaults to results/oracle_experiments; pass a "
             "dataset-specific directory so a cross-benchmark run cannot truncate "
             "an existing run's comparison.jsonl.",
    )
    parser.add_argument(
        "--resume",
        action="store_true",
        help="Keep rows already written to the output directory and skip their "
             "question_ids, so an interrupted run can be completed incrementally.",
    )
    args = parser.parse_args()
    run(
        args.dataset,
        args.limit,
        Path(args.out_dir) if args.out_dir else None,
        resume=args.resume,
    )


if __name__ == "__main__":
    main()
