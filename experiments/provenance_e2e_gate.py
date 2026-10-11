"""Validate one LoCoMo sample end-to-end before scaling experiments.

The gate is intentionally provenance-first: it verifies that Gold Evidence
resolves to the exact normalized conversation turn that MemoryEngine ingests.
Lifecycle stages are then inspected to ensure any claimed match points back to
that same source turn. A lifecycle miss is allowed (it may be a real failure);
a provenance mismatch is not.
"""
from __future__ import annotations

import argparse
import json
import tempfile
from pathlib import Path
from typing import Any

from datasets.loader import iter_normalized
from memory_engine.engine import MemoryEngine
from memory_engine.models import AddMessage, AddRequest, SearchRequest
from tracing.engine_trace import artifacts_from_store, retrieval_artifacts, stage_match


def _record(dataset: str, question_id: str) -> dict[str, Any]:
    for record in iter_normalized(dataset):
        if str(record.get("question_id")) == str(question_id):
            return record
    raise SystemExit(f"question_id not found: {question_id}")


def _msg(raw: Any) -> tuple[str, str, int | None]:
    if isinstance(raw, dict):
        role = str(raw.get("role") or raw.get("speaker") or "user")
        text = str(raw.get("content") or raw.get("text") or raw.get("message") or "").strip()
        timestamp = raw.get("timestamp")
        return role, text, timestamp if isinstance(timestamp, int) else None
    return "user", str(raw).strip(), None


def _ingest(record: dict[str, Any], db_path: str) -> tuple[MemoryEngine, str]:
    engine = MemoryEngine(db_path)
    user_id = "provenance_gate_user"
    for session in record.get("conversation") or []:
        messages = []
        for raw in session.get("messages") or []:
            role, text, timestamp = _msg(raw)
            if text:
                messages.append(AddMessage(role=role, content=text, timestamp=timestamp))
        if messages:
            engine.add(AddRequest(
                request_id=f"provenance-gate:{session['session_id']}",
                messages=messages,
                user_id=user_id,
                session_id=str(session["session_id"]),
            ))
    return engine, user_id


def _gold(record: dict[str, Any]) -> list[dict[str, Any]]:
    return [dict(x) for x in (record.get("gold_evidence") or [])]


def _raw_by_turn(engine: MemoryEngine, user_id: str) -> dict[str, dict[str, Any]]:
    rows = engine.store.all_raw(user_id)
    return {
        str(row.get("source_turn_id") or row.get("turn_id")): row
        for row in rows
        if row.get("source_turn_id") or row.get("turn_id")
    }


def _assert_gold_provenance(record: dict[str, Any], raw_by_turn: dict[str, dict[str, Any]]) -> list[dict[str, Any]]:
    checks = []
    for evidence in _gold(record):
        gid = str(evidence.get("evidence_id"))
        turn_id = str(evidence.get("turn_id") or "")
        source_id = str(evidence.get("source_id") or "")
        text = str(evidence.get("text") or "").strip()
        if not turn_id or not source_id or not text:
            raise AssertionError(f"unresolved Gold Evidence metadata: {gid}")
        raw = raw_by_turn.get(turn_id)
        if raw is None:
            raise AssertionError(f"Gold Evidence turn not found in ingested raw memory: {gid} -> {turn_id}")
        if str(raw.get("session_id") or "") != source_id:
            raise AssertionError(
                f"session provenance mismatch for {gid}: gold={source_id!r}, raw={raw.get('session_id')!r}"
            )
        if str(raw.get("content") or "").strip() != text:
            raise AssertionError(f"text provenance mismatch for {gid} -> {turn_id}")
        checks.append({
            "evidence_id": gid,
            "source_id": source_id,
            "turn_id": turn_id,
            "raw_id": raw.get("id"),
            "status": "PASS",
        })
    return checks


def _stage_provenance(gold: list[dict[str, Any]], artifacts: list[dict[str, Any]]) -> dict[str, Any]:
    matched = stage_match(gold, artifacts)
    by_id = {str(x.get("evidence_id")): x for x in gold}
    provenance_errors = []
    for gid, artifact in matched.get("matches", {}).items():
        evidence = by_id[str(gid)]
        expected_turn = str(evidence.get("turn_id") or "")
        actual_turn = str(artifact.get("source_turn_id") or artifact.get("turn_id") or "")
        if expected_turn and actual_turn != expected_turn:
            provenance_errors.append({
                "evidence_id": str(gid),
                "expected_turn_id": expected_turn,
                "actual_turn_id": actual_turn or None,
                "error": "missing_or_mismatched_turn_provenance",
            })
    return {
        "found": matched.get("found", []),
        "missing": matched.get("missing", []),
        "match_types": matched.get("match_types", {}),
        "match_scores": matched.get("match_scores", {}),
        "provenance_errors": provenance_errors,
    }


def run(question_id: str) -> dict[str, Any]:
    record = _record("locomo_refined_public", question_id)
    gold = _gold(record)
    if not gold:
        raise AssertionError("sample has no Gold Evidence")

    with tempfile.TemporaryDirectory(prefix="locomo_provenance_") as tmp:
        engine, user_id = _ingest(record, str(Path(tmp) / "memory.db"))
        raw = _raw_by_turn(engine, user_id)
        gold_checks = _assert_gold_provenance(record, raw)

        stored = artifacts_from_store(engine, user_id)
        formation = stored["facts"] + stored["relations"] + stored["events"] + stored["rules"] + stored["profiles"]
        storage = stored["raw"] + formation
        results = engine.search(SearchRequest(
            query=record["question"], user_id=user_id, top_k=10, multi_hop=True,
        ))
        search_trace = engine.last_search_trace or {}
        retrieval = search_trace.get("retrieval_candidates") or retrieval_artifacts(results)
        reranked = search_trace.get("reranked") or retrieval
        context = search_trace.get("context") or retrieval

        stages = {
            "formation": _stage_provenance(gold, formation),
            "storage": _stage_provenance(gold, storage),
            "evolution": _stage_provenance(gold, formation),
            "retrieval": _stage_provenance(gold, retrieval),
            "rerank": _stage_provenance(gold, reranked),
            "context": _stage_provenance(gold, context),
        }
        provenance_errors = {
            stage: value["provenance_errors"]
            for stage, value in stages.items()
            if value["provenance_errors"]
        }
        if provenance_errors:
            raise AssertionError(f"lifecycle provenance mismatch: {json.dumps(provenance_errors, ensure_ascii=False)}")

        result = {
            "status": "PASS",
            "gate": "LOCOMO_SINGLE_SAMPLE_PROVENANCE_E2E",
            "dataset": record.get("dataset"),
            "question_id": record.get("question_id"),
            "conversation_id": record.get("conversation_id"),
            "question": record.get("question"),
            "session_count": len(record.get("conversation") or []),
            "ingested_raw_count": len(raw),
            "gold_evidence_count": len(gold),
            "gold_provenance": gold_checks,
            "stages": stages,
            "note": "Missing evidence at a lifecycle stage is allowed as a potential failure; provenance mismatch is a gate failure.",
        }
        print(json.dumps(result, ensure_ascii=False, indent=2))
        return result


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--question-id", default="conv-26#q0000")
    args = parser.parse_args()
    run(args.question_id)


if __name__ == "__main__":
    main()
