"""Run evidence-boundary control experiments with observable progress.

Modes:
1. Real Memory: ingest the benchmark conversation and retrieve with MemoryEngine.
2. Oracle Memory: expose gold evidence at the memory boundary.
3. Oracle Context: expose gold evidence directly at the context boundary.

This is an evidence-availability experiment. It deliberately does not fabricate
answer accuracy until a benchmark-aligned answer-generation/scoring path exists.
Each completed record is checkpointed immediately so long runs are observable
and resumable from the output files.
"""
from __future__ import annotations

import argparse
import json
import time
import traceback
import uuid
from pathlib import Path
from typing import Any

from datasets.loader import iter_normalized
from evaluation.lifecycle_metrics import summarize_traces
from memory_engine.engine import MemoryEngine
from memory_engine.models import AddMessage, AddRequest, SearchRequest
from tracing.dataset_trace import record_to_trace
from tracing.engine_trace import retrieval_artifacts, stage_match
from tracing.failure_attribution import attribute_failure


ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "results" / "oracle_experiments"


def log(message: str) -> None:
    print(message, flush=True)


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


def _msg(m: Any) -> tuple[str, str, int | None]:
    if isinstance(m, dict):
        role = str(m.get("role") or m.get("speaker") or "user")
        text = str(m.get("content") or m.get("text") or m.get("message") or "")
        ts = m.get("timestamp")
        return role, text, ts if isinstance(ts, int) else None
    return "user", str(m), None


def _gold_artifacts(record: dict[str, Any]) -> list[dict[str, Any]]:
    return [
        {
            "id": str(e["evidence_id"]),
            "content": str(e.get("text") or ""),
            "source_id": e.get("source_id"),
            "timestamp": e.get("timestamp"),
            "memory_type": "oracle",
        }
        for e in record.get("gold_evidence", [])
        if e.get("evidence_id") and e.get("text")
    ]


def _stage(
    gold: list[dict[str, Any]],
    artifacts: list[dict[str, Any]],
    mode: str,
) -> dict[str, Any]:
    match = stage_match(gold, artifacts)
    return {
        "found": match["found"],
        "missing": match["missing"],
        "details": {
            "mode": mode,
            "observed_count": match["observed_count"],
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
    log(
        f"    [ingest] {message_count} messages in "
        f"{time.perf_counter() - t0:.2f}s"
    )
    return engine, user_id


def run_record(record: dict[str, Any], idx: int) -> dict[str, Any]:
    trace = record_to_trace(record)
    gold = [e.__dict__ for e in trace.gold_evidence]
    oracle = _gold_artifacts(record)

    log("    [real] building memory")
    engine, user_id = _real_engine(record, idx)

    log("    [real] retrieval")
    t0 = time.perf_counter()
    results = engine.search(SearchRequest(
        query=record["question"],
        user_id=user_id,
        top_k=10,
        multi_hop=True,
    ))
    real = retrieval_artifacts(results)
    log(
        f"    [real] retrieval done in {time.perf_counter() - t0:.2f}s; "
        f"artifacts={len(real)}"
    )

    # Real Memory: actual end-to-end memory retrieval.
    trace.retrieval = type(trace.retrieval)(
        **_stage(gold, real, "real_memory")
    )

    # Oracle Memory: pretend all gold evidence survived formation/storage/
    # evolution, then expose it at the rerank boundary. This is an evidence
    # control, not a claim that the real reranker processed these artifacts.
    trace.storage = type(trace.storage)(
        **_stage(gold, oracle, "oracle_memory")
    )
    trace.evolution = type(trace.evolution)(
        **_stage(gold, oracle, "oracle_memory")
    )
    trace.rerank = type(trace.rerank)(
        **_stage(gold, oracle, "oracle_memory")
    )

    # Oracle Context: gold evidence is placed directly at the final boundary.
    trace.context = type(trace.context)(
        **_stage(gold, oracle, "oracle_context")
    )

    trace.answer = {
        "correct": None,
        "answer": None,
        "mode": "evidence-only-control",
        "answer_scoring": "not_run",
    }
    trace.failure_type = attribute_failure(trace.to_dict())

    return {
        "question_id": trace.question_id,
        "question": trace.question,
        "modes": {
            "real_memory": {
                "retrieval": trace.retrieval.to_dict(),
                "failure_type": trace.failure_type,
            },
            "oracle_memory": {
                "storage": trace.storage.to_dict(),
                "evolution": trace.evolution.to_dict(),
                "rerank": trace.rerank.to_dict(),
            },
            "oracle_context": {
                "context": trace.context.to_dict(),
            },
        },
        "gold_evidence_count": len(gold),
        "gold_evidence": gold,
    }


def _write_jsonl(path: Path, row: dict[str, Any]) -> None:
    with path.open("a", encoding="utf-8") as f:
        f.write(json.dumps(row, ensure_ascii=False) + "\n")
        f.flush()


def _write_progress(path: Path, payload: dict[str, Any]) -> None:
    path.write_text(
        json.dumps(payload, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )


def _build_summary(
    dataset: str,
    limit: int,
    rows: list[dict[str, Any]],
    errors: int,
) -> dict[str, Any]:
    real_traces = []
    oracle_traces = []
    context_traces = []
    for row in rows:
        gold = row.get("gold_evidence", [])
        real_traces.append({
            "gold_evidence": gold,
            "retrieval": row["modes"]["real_memory"]["retrieval"],
        })
        oracle_traces.append({
            "gold_evidence": gold,
            "context": row["modes"]["oracle_memory"]["rerank"],
        })
        context_traces.append({
            "gold_evidence": gold,
            "context": row["modes"]["oracle_context"]["context"],
        })

    return {
        "dataset": dataset,
        "limit": limit,
        "records": len(rows),
        "errors": errors,
        "real_memory": summarize_traces(real_traces) if rows else {},
        "oracle_memory": summarize_traces(oracle_traces) if rows else {},
        "oracle_context": summarize_traces(context_traces) if rows else {},
        "answer_scoring": "not_run",
        "note": (
            "Evidence availability control only; no answer accuracy is "
            "claimed. Oracle Memory currently bypasses formation/storage/"
            "evolution and exposes gold evidence at the rerank accounting "
            "boundary rather than running the real reranker."
        ),
    }


def run(dataset: str, limit: int) -> dict[str, Any]:
    OUT.mkdir(parents=True, exist_ok=True)
    jsonl = OUT / "comparison.jsonl"
    progress_path = OUT / "progress.json"
    summary_path = OUT / "summary.json"

    # Start a fresh checkpoint file for this invocation.
    jsonl.write_text("", encoding="utf-8")
    rows: list[dict[str, Any]] = []
    errors = 0
    started = time.perf_counter()

    log("=" * 72)
    log(f"Oracle experiment started: dataset={dataset}, limit={limit}")
    log(f"Output: {OUT}")
    log("=" * 72)

    _write_progress(progress_path, {
        "status": "running",
        "dataset": dataset,
        "limit": limit,
        "completed": 0,
        "errors": 0,
        "elapsed_seconds": 0.0,
    })

    for idx, record in enumerate(iter_normalized(dataset, limit=limit)):
        number = idx + 1
        question_id = str(record.get("question_id") or record.get("example_id") or f"row_{idx}")
        log(f"\n[{number}/{limit}] START question_id={question_id}")
        t0 = time.perf_counter()

        try:
            row = run_record(record, idx)
            row["_status"] = "ok"
            row["_elapsed_seconds"] = round(time.perf_counter() - t0, 3)
            rows.append(row)
            _write_jsonl(jsonl, row)

            failure = row["modes"]["real_memory"].get("failure_type")
            log(
                f"[{number}/{limit}] DONE "
                f"{row['_elapsed_seconds']:.2f}s "
                f"failure={failure}"
            )
        except Exception as exc:
            errors += 1
            elapsed = round(time.perf_counter() - t0, 3)
            error_row = {
                "question_id": question_id,
                "question": record.get("question"),
                "_status": "error",
                "_elapsed_seconds": elapsed,
                "error": f"{type(exc).__name__}: {exc}",
            }
            _write_jsonl(jsonl, error_row)
            log(f"[{number}/{limit}] ERROR after {elapsed:.2f}s: {exc}")
            traceback.print_exc()

        _write_progress(progress_path, {
            "status": "running",
            "dataset": dataset,
            "limit": limit,
            "completed": number,
            "successful": len(rows),
            "errors": errors,
            "last_question_id": question_id,
            "elapsed_seconds": round(time.perf_counter() - started, 3),
        })

    summary = _build_summary(dataset, limit, rows, errors)
    summary_path.write_text(
        json.dumps(summary, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )
    _write_progress(progress_path, {
        "status": "completed",
        "dataset": dataset,
        "limit": limit,
        "completed": len(rows) + errors,
        "successful": len(rows),
        "errors": errors,
        "elapsed_seconds": round(time.perf_counter() - started, 3),
    })

    log("\n" + "=" * 72)
    log(
        f"EXPERIMENT FINISHED: successful={len(rows)}, "
        f"errors={errors}, elapsed={time.perf_counter() - started:.2f}s"
    )
    log(f"Results: {jsonl}")
    log(f"Summary: {summary_path}")
    log("=" * 72)
    return summary


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--dataset", default="longmemeval_s_sample10")
    parser.add_argument("--limit", type=int, default=10)
    args = parser.parse_args()
    summary = run(args.dataset, args.limit)
    print(json.dumps(summary, ensure_ascii=False, indent=2), flush=True)


if __name__ == "__main__":
    main()
