"""Re-judge every discordant intervention pair with a second model.

The judge decides correctness, so a handful of misjudged flips can reverse a
borderline McNemar contrast. This script replays the same evaluator (including
its deterministic floors) with a different judge model over the discordant
pairs only, then reports how many pairs change and recomputes the paired test.

The second model is configured through the usual ``SEMANTIC_JUDGE_*`` variables;
point them at a model from a different family than the one that produced the
stored verdicts.

Usage (cross-model example):
    SEMANTIC_JUDGE_API_STYLE=openai \
    SEMANTIC_JUDGE_BASE_URL=$ANSWER_BASE_URL/v1 \
    SEMANTIC_JUDGE_MODEL=kimi-k3 \
    SEMANTIC_JUDGE_API_KEY=$ANSWER_API_KEY \
    python -m experiments.rejudge_discordants \
        --interventions results/interventions_locomo_n200/interventions.jsonl \
        --baseline results/oracle_experiments_locomo_n200/comparison.jsonl
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

from evaluation.answer_semantic_eval import evaluate_answer
from evaluation.paired_stats import mcnemar_exact
from experiments.analyze_interventions import _load_jsonl, by_question, common_questions

ALL_ARMS = ("first_loss", "path", "agnostic")


def _verdict(row: dict[str, Any], side: str) -> Any:
    return (row.get(side) or {}).get("semantic_correct")


def _answer(row: dict[str, Any], side: str) -> str:
    return str((row.get(side) or {}).get("answer") or "")


def rejudge_pair(
    pair: dict[str, Any],
    baseline_row: dict[str, Any],
) -> dict[str, Any]:
    question = str(baseline_row.get("question") or "")
    gold = baseline_row.get("gold_evidence") or []
    reference = baseline_row.get("gold_answer")
    rejudged = {}
    for side in ("baseline", "repaired"):
        try:
            verdict = evaluate_answer(
                question, _answer(pair, side), gold, reference_answer=reference
            )
            rejudged[side] = {
                "correct": verdict.get("correct"),
                "adjudication": verdict.get("adjudication"),
                "error": None,
            }
        except Exception as exc:  # keep going; report the failure
            rejudged[side] = {
                "correct": None,
                "adjudication": None,
                "error": f"{type(exc).__name__}: {exc}",
            }
    old = (_verdict(pair, "baseline"), _verdict(pair, "repaired"))
    new = (rejudged["baseline"]["correct"], rejudged["repaired"]["correct"])
    return {
        "question_id": pair.get("question_id"),
        "arm": pair.get("arm"),
        "old": old,
        "new": new,
        "changed": old != new,
        "rejudged": rejudged,
    }


def run(interventions: Path, baseline: Path, arms: tuple[str, ...]) -> dict[str, Any]:
    rows = _load_jsonl(interventions)
    baseline_rows = {str(r.get("question_id")): r for r in _load_jsonl(baseline)}
    grouped = by_question(rows)
    common = set(common_questions(grouped, arms))

    details: list[dict[str, Any]] = []
    for qid in sorted(common):
        for arm in arms:
            pair = grouped[qid].get(arm)
            if not pair or pair.get("skipped") or not pair.get("target_stage"):
                continue
            a, b = _verdict(pair, "baseline"), _verdict(pair, "repaired")
            if a is None or b is None or a == b:
                continue
            details.append(rejudge_pair(pair, baseline_rows.get(qid, {})))

    summary: dict[str, Any] = {"discordant_pairs": len(details), "arms": {}}
    for arm in arms:
        arm_rows = [d for d in details if d["arm"] == arm and None not in d["new"]]
        old_a = [d["old"][0] for d in arm_rows]
        old_b = [d["old"][1] for d in arm_rows]
        new_a = [d["new"][0] for d in arm_rows]
        new_b = [d["new"][1] for d in arm_rows]
        summary["arms"][arm] = {
            "pairs": len(arm_rows),
            "pairs_changed": sum(1 for d in arm_rows if d["changed"]),
            "old_net_flips": sum(1 for x, y in zip(old_a, old_b) if not x and y)
            - sum(1 for x, y in zip(old_a, old_b) if x and not y),
            "new_net_flips": sum(1 for x, y in zip(new_a, new_b) if not x and y)
            - sum(1 for x, y in zip(new_a, new_b) if x and not y),
            "old_mcnemar": mcnemar_exact(old_a, old_b),
            "new_mcnemar": mcnemar_exact(new_a, new_b),
        }
    summary["pairs"] = details
    return summary


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--interventions", required=True)
    parser.add_argument("--baseline", required=True)
    parser.add_argument("--arms", default=",".join(ALL_ARMS))
    parser.add_argument("--out", default=None)
    args = parser.parse_args()
    arms = tuple(a.strip() for a in args.arms.split(",") if a.strip())
    result = run(Path(args.interventions), Path(args.baseline), arms)
    text = json.dumps(result, ensure_ascii=False, indent=2)
    if args.out:
        Path(args.out).write_text(text, encoding="utf-8")
    print(text)


if __name__ == "__main__":
    main()
