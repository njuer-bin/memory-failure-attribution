"""Generate a conservative LoCoMo multi-hop candidate dataset.

This step is intentionally candidate generation only. It must not decide that a
question is multi-hop, infer a path, or invent relations. Human review later
freezes hop_count, ordered_path, relations, and bridge evidence.
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any, Iterable

from datasets.loader import iter_normalized

ROOT = Path(__file__).resolve().parents[1]
OUT_DIR = ROOT / "results" / "multihop_candidates"

TEMPORAL_TERMS = (
    "when", "what day", "what date", "how long", "before", "after",
    "later", "earlier", "多久", "什么时候", "哪天", "几号", "之前", "之后",
)
CAUSAL_TERMS = (
    "why", "why did", "reason", "because", "lead to", "result in",
    "cause", "caused", "为什么", "原因", "导致", "因为", "结果",
)
RELATIONAL_TERMS = (
    "who", "which person", "relationship", "friend", "worked with", "met",
    "是谁", "谁和", "关系", "朋友", "一起", "认识",
)


def _text(value: Any) -> str:
    return str(value or "").strip()


def _evidence_features(record: dict[str, Any]) -> dict[str, Any]:
    evidence = [e for e in (record.get("gold_evidence") or []) if isinstance(e, dict)]
    sessions = {str(e.get("source_id")) for e in evidence if e.get("source_id") is not None}
    turns = {str(e.get("turn_id")) for e in evidence if e.get("turn_id") is not None}
    return {
        "gold_evidence_count": len(evidence),
        "distinct_source_count": len(sessions),
        "distinct_turn_count": len(turns),
        "cross_session_evidence": len(sessions) > 1,
        "cross_turn_evidence": len(turns) > 1,
    }


def _query_signals(question: str) -> dict[str, bool]:
    q = question.lower()
    return {
        "temporal_language": any(term in q for term in TEMPORAL_TERMS),
        "causal_language": any(term in q for term in CAUSAL_TERMS),
        "relational_language": any(term in q for term in RELATIONAL_TERMS),
    }


def candidate_record(record: dict[str, Any]) -> dict[str, Any] | None:
    """Return a candidate annotation record, or None when there is no signal.

    Signals are deliberately weak. In particular, two evidence items are not
    treated as proof of a two-hop chain.
    """
    qid = _text(record.get("question_id") or record.get("example_id"))
    question = _text(record.get("question"))
    evidence = [e for e in (record.get("gold_evidence") or []) if isinstance(e, dict)]
    features = _evidence_features(record)
    signals = _query_signals(question)
    task_types = [str(x) for x in (record.get("task_type") or [])]
    task_blob = " ".join(task_types).lower()

    reasons: list[str] = []
    if features["gold_evidence_count"] >= 2:
        reasons.append("multiple_gold_evidence_items")
    if features["cross_session_evidence"]:
        reasons.append("cross_session_evidence")
    if features["cross_turn_evidence"]:
        reasons.append("cross_turn_evidence")
    if signals["temporal_language"]:
        reasons.append("temporal_question_signal")
    if signals["causal_language"]:
        reasons.append("causal_question_signal")
    if signals["relational_language"]:
        reasons.append("relational_question_signal")
    if "multi_hop" in task_blob:
        reasons.append("benchmark_task_type_multi_hop")

    # Candidate inclusion is intentionally broad enough for recall, but every
    # record still carries explicit reasons so later review can audit selection.
    if not reasons:
        return None

    return {
        "dataset": record.get("dataset"),
        "family": record.get("family"),
        "example_id": record.get("example_id"),
        "question_id": qid,
        "question": question,
        "reference_answer": _text(record.get("answer")),
        "gold_evidence": evidence,
        "candidate_features": features,
        "query_signals": signals,
        "task_type": task_types,
        "candidate_reasons": reasons,
        "review": {
            "status": "unreviewed",
            "hop_count": None,
            "hop_type": "unknown",
            "ordered_path": [],
            "relations": [],
            "bridge_evidence": [],
            "notes": "Candidate only; no hop/path/relation inference has been made.",
        },
    }


def generate(dataset_id: str, limit: int | None = None) -> Iterable[dict[str, Any]]:
    for record in iter_normalized(dataset_id, limit=limit):
        candidate = candidate_record(record)
        if candidate is not None:
            yield candidate


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--dataset", default="locomo_refined_public")
    parser.add_argument("--limit", type=int, default=None)
    parser.add_argument("--output", default=None)
    args = parser.parse_args()

    output = Path(args.output) if args.output else OUT_DIR / f"{args.dataset}_candidates.jsonl"
    output.parent.mkdir(parents=True, exist_ok=True)

    count = 0
    with output.open("w", encoding="utf-8") as fh:
        for item in generate(args.dataset, args.limit):
            fh.write(json.dumps(item, ensure_ascii=False) + "\n")
            count += 1
    print(f"Generated {count} candidates -> {output}")


if __name__ == "__main__":
    main()
