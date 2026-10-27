"""Re-evaluate the stored answers of a completed run under the current protocol.

The answers, retrieved contexts and lifecycle traces are already on disk; only the
*evaluation* changed (numeric/duration layer, tightened lexical skip). Re-scoring
offline avoids re-running ingestion and generation, which is the expensive and
memory-hungry part.

Attribution is recomputed with the same stored gates and stages, so every number
that does not depend on the answer verdict is unchanged; the diff between the two
summary files isolates the effect of the evaluator change.

Usage:
    python -m experiments.rescore_answers \\
        --input results/oracle_experiments_n50_repaired/comparison.jsonl \\
        --out-dir results/oracle_experiments_n50_rescored
"""
from __future__ import annotations

import argparse
import copy
import json
from pathlib import Path
from typing import Any

from evaluation import attribution
from evaluation.answer_semantic_eval import numeric_answer_verdict
from experiments import run_oracle_experiments as runner

MODES = ("real_memory", "oracle_memory", "oracle_context")
_SEMANTIC_KEYS = (
    "semantic_correct", "semantic_judge_correct", "semantic_evidence_sufficient",
    "semantic_confidence", "semantic_reason", "semantic_adjudication",
    "semantic_adjudication_anchor", "semantic_judge_model", "semantic_error",
)
_PROTOCOL = (
    "semantic verdicts recomputed with the deterministic numeric/duration layer "
    "and the tightened lexical skip; answer verdicts only, lifecycle traces kept. "
    "Answers the judge already ruled on keep their stored verdict unless "
    "--rejudge-everything is passed, so the diff isolates the evaluator change "
    "from judge re-sampling."
)


def _clean_answer(answer: dict[str, Any]) -> dict[str, Any]:
    return {k: v for k, v in answer.items() if not k.startswith("semantic_")}


def _apply_ordering_refutation(
    question: str,
    answer: dict[str, Any],
    gold: list[dict[str, Any]],
) -> dict[str, Any] | None:
    """Offline flip of a stored judge verdict the ordering check refutes.

    Applies the same contract as the refutation inside evaluate_answer: only a
    stored judge-ruled, not-lexically-correct answer can flip, and only when
    the evidence proves the picked option is the later one.
    """
    from evaluation.answer_semantic_eval import _ordering_refutes_judge
    if answer.get("semantic_adjudication") != "judge":
        return None
    if not (
        answer.get("semantic_correct") is True
        and answer.get("semantic_evidence_sufficient") is True
        and answer.get("semantic_confidence") in {"medium", "high"}
    ):
        return None
    refutation = _ordering_refutes_judge(
        question, str(answer.get("answer") or ""), list(gold or [])
    )
    if not refutation:
        return None
    return {
        "semantic_correct": False,
        "semantic_judge_correct": False,
        "semantic_evidence_sufficient": answer.get("semantic_evidence_sufficient"),
        "semantic_confidence": answer.get("semantic_confidence"),
        "semantic_reason": answer.get("semantic_reason"),
        "semantic_adjudication": "ordering_refutation",
        "semantic_adjudication_anchor": f"{refutation[1]} precedes {refutation[0]}",
        "semantic_judge_model": answer.get("semantic_judge_model"),
        "semantic_error": None,
    }


def rescore_answer(
    question: str,
    stored_answer: dict[str, Any],
    gold: list[dict[str, Any]],
    gold_answer: str,
    *,
    rejudge_everything: bool = False,
) -> dict[str, Any]:
    """Re-evaluate one stored answer under the current protocol.

    The numeric layer is applied first; the judge is then left alone for answers
    it already ruled on, so only answers whose *evaluation rule* changed move.
    """
    answer = {**_clean_answer(stored_answer), **{key: None for key in _SEMANTIC_KEYS}}
    candidate = str(answer.get("answer") or "").strip()
    if answer.get("model_error") or not candidate:
        answer["semantic_correct"] = None
        answer["semantic_error"] = answer.get("model_error") or "empty answer"
        return answer

    if gold_answer is not None:
        numeric = numeric_answer_verdict(question, candidate, gold_answer)
        if numeric is not None:
            return {**answer, **runner._semantic_fields(numeric)}

    if not rejudge_everything and stored_answer.get("semantic_judge_correct") is not None:
        return {
            **answer,
            **{key: stored_answer.get(key) for key in _SEMANTIC_KEYS},
        }

    return runner._semantic_eval(question, answer, gold, gold_answer)


def rescore_row(
    row: dict[str, Any], *, rejudge_everything: bool = False,
    apply_ordering_refutation: bool = False,
) -> dict[str, Any]:
    row = copy.deepcopy(row)
    question = str(row.get("question") or "")
    gold = list(row.get("gold_evidence") or [])
    gold_answer = row.get("gold_answer", "")
    for mode in MODES:
        mode_data = row["modes"].get(mode)
        if not mode_data:
            continue
        answer = rescore_answer(
            question, mode_data.get("answer") or {}, gold, gold_answer,
            rejudge_everything=rejudge_everything,
        )
        if apply_ordering_refutation:
            flip = _apply_ordering_refutation(question, answer, gold)
            if flip:
                answer = {**_clean_answer(answer), **flip}
        mode_data["answer"] = answer
        failure = attribution.attribute_failure(
            answer, mode_data.get("evidence_sufficiency") or {},
            mode_data, gold, mode=mode,
        )
        mode_data["answer_failure_type"] = failure
        if mode == "real_memory":
            mode_data["failure_type"] = failure
    return row


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--input", required=True, help="comparison.jsonl of a completed run")
    parser.add_argument("--out-dir", default=None)
    parser.add_argument(
        "--rejudge-everything",
        action="store_true",
        help="Re-run the judge for every answer instead of keeping stored verdicts "
             "for the answers it already ruled on.",
    )
    parser.add_argument(
        "--apply-ordering-refutation",
        action="store_true",
        help="Also apply the deterministic ordering refutation to stored judge verdicts.",
    )
    args = parser.parse_args()

    source = Path(args.input)
    out = Path(args.out_dir) if args.out_dir else source.parent.parent / (source.parent.name + "_rescored")
    out.mkdir(parents=True, exist_ok=True)

    rows = [json.loads(line) for line in source.read_text(encoding="utf-8").splitlines() if line.strip()]
    stored_summary_path = source.parent / "summary.json"
    stored_summary = (
        json.loads(stored_summary_path.read_text(encoding="utf-8"))
        if stored_summary_path.exists() else {}
    )
    dataset = str(stored_summary.get("dataset") or "unknown")

    rescored: list[dict[str, Any]] = []
    for i, row in enumerate(rows, 1):
        print(f"[{i}/{len(rows)}] {row.get('question_id')}", flush=True)
        rescored.append(rescore_row(
            row, rejudge_everything=args.rejudge_everything,
            apply_ordering_refutation=args.apply_ordering_refutation,
        ))

    (out / "comparison.jsonl").write_text(
        "".join(json.dumps(row, ensure_ascii=False) + "\n" for row in rescored),
        encoding="utf-8",
    )
    summary = runner._build_summary(dataset, len(rescored), rescored, 0)
    summary["rescore"] = {"input": str(source), "protocol": _PROTOCOL}
    (out / "summary.json").write_text(
        json.dumps(summary, ensure_ascii=False, indent=2), encoding="utf-8",
    )
    (out / "answer_failure_comparison.json").write_text(
        json.dumps(_failure_diff(rows, rescored), ensure_ascii=False, indent=2),
        encoding="utf-8",
    )
    print(json.dumps({"out": str(out), "records": len(rescored)}, ensure_ascii=False), flush=True)


def _failure_diff(
    before: list[dict[str, Any]], after: list[dict[str, Any]]
) -> dict[str, Any]:
    """Per-question failure-type changes, so the evaluator's effect is auditable."""
    changes: list[dict[str, Any]] = []
    for old, new in zip(before, after):
        for mode in MODES:
            old_mode = old.get("modes", {}).get(mode) or {}
            new_mode = new.get("modes", {}).get(mode) or {}
            old_failure = old_mode.get("answer_failure_type")
            new_failure = new_mode.get("answer_failure_type")
            if old_failure != new_failure:
                changes.append({
                    "question_id": new.get("question_id"),
                    "mode": mode,
                    "old_failure": old_failure,
                    "new_failure": new_failure,
                    "old_semantic_correct": (old_mode.get("answer") or {}).get("semantic_correct"),
                    "new_semantic_correct": (new_mode.get("answer") or {}).get("semantic_correct"),
                    "new_adjudication": (new_mode.get("answer") or {}).get("semantic_adjudication"),
                    "gold_answer": new.get("gold_answer"),
                    "answer": str((new_mode.get("answer") or {}).get("answer"))[:200],
                })
    return {"n_changes": len(changes), "changes": changes}


if __name__ == "__main__":
    main()
