"""Relabel stored comparison rows under the human-validated abstention rule.

An abstention-style answer ("Not mentioned.", "Cannot be determined.", ...) that
the semantic judge accepted as correct is treated as wrong, but only when the
reference answer is itself a concrete fact. If the reference answer is also an
abstention (LongMemEval ``_abs`` questions), abstaining is the correct behaviour
and the row is left alone. Human adjudication (n=200) confirms this guard: it
flips exactly the 13 abstentions humans called wrong and preserves the 12 they
called right (see docs/STATUS.md, 2026-10-25). Only whole-answer abstentions are
considered; a partial answer that states a fact and notes a missing sub-part is
left alone.

The flip is label-only: no API calls, no re-scoring. ``answer_failure_type`` is
recomputed with the frozen ``evaluation.attribution.attribute_failure`` path so
the corrected labels stay comparable to the stored ones.

Usage:
    python -m experiments.abstention_correct \
        --comparison results/oracle_experiments_locomo_n200/comparison.jsonl \
        --out results/_corrected_comparison_locomo_n200.jsonl \
        --summary results/analysis_abstention_corrected_locomo_n200.json
"""
from __future__ import annotations

import argparse
import json
import re
from collections import Counter
from pathlib import Path
from typing import Any

from evaluation import attribution

_ABSTENTION = re.compile(
    r"^(?:"
    r"unknown"
    r"|not mentioned"
    r"|not stated"
    r"|not specified"
    r"|not provided"
    r"|not enough (?:information|info)"
    r"|it is not (?:stated|mentioned|specified|provided)"
    r"|that information is not (?:provided|mentioned|stated|specified)"
    r"|no information(?: is)?(?: available| provided)?"
    r"|cannot be determined"
    r"|cannot determine"
    r"|can't be determined"
    r"|could not be determined"
    r"|unable to determine"
    r"|i (?:do not|don't) know"
    r")"
    r"(?: (?:from|in|by) the (?:given |provided |available )?"
    r"(?:evidence|information|context|data|conversation))?"
    r"[.!\s]*$",
    re.I,
)


def is_abstention(answer: str | None) -> bool:
    return bool(_ABSTENTION.match((answer or "").strip()))


# Reference-answer phrasing that means "the evidence does not answer this", e.g.
# LongMemEval "_abs" golds: "The information provided is not enough. You only
# mentioned ...". A concrete gold that merely contains "did not mention" (e.g.
# "0. You did not mention visiting any museum") is NOT an abstention.
_GOLD_ABSTENTION = re.compile(
    r"^(?:"
    r"the (?:information|evidence|data|context)(?: provided| given| available)?"
    r" (?:is|was) not enough"
    r"|not enough information"
    r"|(?:it is )?not (?:mentioned|stated|specified|provided|known)"
    r"|cannot be determined"
    r"|can't be determined"
    r"|no information(?: is)?(?: available| provided)?"
    r"|unknown"
    r")",
    re.I,
)


def gold_is_abstention(reference: Any) -> bool:
    return bool(_GOLD_ABSTENTION.match(str(reference or "").strip()))


def correct_row(row: dict[str, Any]) -> int:
    """Flip abstention false positives in-place; return number of flips."""
    gold = row.get("gold_evidence") or []
    reference = row.get("gold_answer")
    if gold_is_abstention(reference):
        return 0
    flips = 0
    for mode, mode_data in row.get("modes", {}).items():
        answer = mode_data.get("answer") or {}
        gate = mode_data.get("evidence_sufficiency") or {}
        if answer.get("semantic_correct") is True and is_abstention(answer.get("answer")):
            answer["semantic_correct"] = False
            answer["_abstention_flip"] = True
            mode_data["answer_failure_type"] = attribution.attribute_failure(
                answer, gate, mode_data, gold, mode=mode,
            )
            flips += 1
    return flips


def failure_distribution(rows: list[dict[str, Any]]) -> dict[str, dict[str, int]]:
    dist: dict[str, Counter[str]] = {}
    for row in rows:
        for mode, mode_data in row.get("modes", {}).items():
            dist.setdefault(mode, Counter())[
                str(mode_data.get("answer_failure_type") or "none")
            ] += 1
    return {mode: dict(sorted(c.items())) for mode, c in sorted(dist.items())}


def accuracy(rows: list[dict[str, Any]]) -> dict[str, dict[str, Any]]:
    """Two canonical views, matching the project's other analyses.

    ``semantic_accuracy`` is computed on judged rows only (semantic verdict
    present), as in the STATUS n=200 tables. ``attributed_accuracy`` applies the
    attribution fallback: a missing semantic verdict with a lexically correct
    answer counts as correct.
    """
    judged: dict[str, list[bool]] = {}
    attributed: dict[str, list[bool]] = {}
    for row in rows:
        for mode, mode_data in row.get("modes", {}).items():
            answer = mode_data.get("answer") or {}
            semantic = answer.get("semantic_correct")
            attributed.setdefault(mode, []).append(
                semantic is True or (semantic is None and answer.get("correct") is True)
            )
            if semantic is not None:
                judged.setdefault(mode, []).append(semantic is True)
    return {
        mode: {
            "semantic_accuracy": (sum(v) / len(v) if v else None),
            "semantic_judged": len(v),
            "attributed_accuracy": (
                sum(attributed[mode]) / len(attributed[mode]) if attributed[mode] else None
            ),
        }
        for mode, v in sorted(judged.items())
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--comparison", required=True)
    parser.add_argument("--out", required=True)
    parser.add_argument("--summary", required=True)
    args = parser.parse_args()

    rows = [json.loads(line) for line in Path(args.comparison).read_text(encoding="utf-8").splitlines() if line.strip()]
    auto_dist = failure_distribution(rows)
    auto_acc = accuracy(rows)

    flips = [correct_row(row) for row in rows]

    summary = {
        "source": args.comparison,
        "rows": len(rows),
        "flips": sum(flips),
        "rows_with_flips": sum(1 for f in flips if f),
        "accuracy": {"auto": auto_acc, "corrected": accuracy(rows)},
        "failure_distribution": {
            "auto": auto_dist, "corrected": failure_distribution(rows),
        },
    }

    out = Path(args.out)
    out.write_text(
        "\n".join(json.dumps(row, ensure_ascii=False) for row in rows) + "\n",
        encoding="utf-8",
    )
    Path(args.summary).write_text(json.dumps(summary, ensure_ascii=False, indent=2), encoding="utf-8")
    print(json.dumps(summary, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
