"""Run Real/Oracle Memory/Oracle Context evidence experiments.

This first control experiment is retrieval-focused because the repository does
not yet contain a benchmark-aligned answer-generation model. It therefore does
not fabricate answer scores. Instead it measures the information ceiling at
three boundaries:

1. Real Memory: query the actual MemoryEngine.
2. Oracle Memory: bypass memory formation/storage/evolution and expose gold
   evidence as memory artifacts, then apply the same trace/evidence accounting.
3. Oracle Context: directly expose gold evidence as the final context.

Oracle Context is an upper bound for evidence availability, not an answer
accuracy claim. Answer-generation experiments can consume the emitted JSONL
later without changing the dataset or memory layer.
"""
from __future__ import annotations

import argparse
import json
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


def _stage(found: list[str], gold: list[dict[str, Any]], artifacts: list[dict[str, Any]], mode: str) -> dict[str, Any]:
    m = stage_match(gold, artifacts)
    return {
        "found": m["found"],
        "missing": m["missing"],
        "details": {
            "mode": mode,
            "observed_count": m["observed_count"],
            "matches": m["matches"],
        },
    }


def _real_engine(record: dict[str, Any], idx: int) -> tuple[MemoryEngine, str]:
    user_id = f"oracle_{idx}_{uuid.uuid4().hex}"
    engine = MemoryEngine(str(ROOT / "data" / f"oracle_{idx}_{uuid.uuid4().hex}.db"))
    for session in _sessions(record):
        messages = []
        for raw in session["messages"]:
            role, text, ts = _msg(raw)
            if text:
                messages.append(AddMessage(role=role, content=text, timestamp=ts))
        if messages:
            engine.add(AddRequest(
                request_id=f"{user_id}:{session['session_id']}",
                messages=messages,
                user_id=user_id,
                session_id=session["session_id"],
            ))
    return engine, user_id


def run_record(record: dict[str, Any], idx: int) -> dict[str, Any]:
    trace = record_to_trace(record)
    gold = [e.__dict__ for e in trace.gold_evidence]
    oracle = _gold_artifacts(record)

    engine, user_id = _real_engine(record, idx)
    results = engine.search(SearchRequest(
        query=record["question"], user_id=user_id, top_k=10, multi_hop=True
    ))
    real = retrieval_artifacts(results)

    # Real Memory: actual end-to-end memory retrieval.
    trace.retrieval = type(trace.retrieval)(
        **_stage([], gold, real, "real_memory")
    )

    # Oracle Memory: pretend all gold evidence survived formation/storage/
    # evolution, then apply the same retrieval evidence accounting.
    trace.storage = type(trace.storage)(**_stage([], gold, oracle, "oracle_memory"))
    trace.evolution = type(trace.evolution)(**_stage([], gold, oracle, "oracle_memory"))
    trace.rerank = type(trace.rerank)(**_stage([], gold, oracle, "oracle_memory"))

    # Oracle Context: gold evidence is placed directly at the final boundary.
    trace.context = type(trace.context)(**_stage([], gold, oracle, "oracle_context"))

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


def run(dataset: str, limit: int) -> dict[str, Any]:
    rows = [run_record(record, i) for i, record in enumerate(iter_normalized(dataset, limit=limit))]
    # The per-row traces retain the original benchmark evidence IDs. Do not
    # replace them with positional IDs: that would corrupt recall calculations.
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

    OUT.mkdir(parents=True, exist_ok=True)
    jsonl = OUT / "comparison.jsonl"
    with jsonl.open("w", encoding="utf-8") as f:
        for row in rows:
            f.write(json.dumps(row, ensure_ascii=False) + "\n")

    summary = {
        "dataset": dataset,
        "limit": limit,
        "records": len(rows),
        "real_memory": summarize_traces(real_traces),
        "oracle_memory": summarize_traces(oracle_traces),
        "oracle_context": summarize_traces(context_traces),
        "answer_scoring": "not_run",
        "note": "This experiment measures evidence availability ceilings; it does not claim answer accuracy.",
    }
    (OUT / "summary.json").write_text(json.dumps(summary, ensure_ascii=False, indent=2), encoding="utf-8")
    return summary


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--dataset", default="longmemeval_s_sample10")
    parser.add_argument("--limit", type=int, default=10)
    args = parser.parse_args()
    print(json.dumps(run(args.dataset, args.limit), ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
