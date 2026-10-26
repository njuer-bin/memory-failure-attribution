"""Validate the abstention-correction rule against the adjudicated human sample.

The sample is the 200-row annotation package. Restrict to rows the judge stored
as semantically correct, then compare two rules with human adjudication:

- naive: every abstention-style stored answer is wrong;
- guarded: only when the reference answer is not itself an abstention.

Reports precision/recall over the stored-correct sample and a 2x2 over the
abstention-style subset. No model calls.

Usage:
    python -m experiments.validate_abstention_rule \
        --out results/analysis_abstention_rule_validation.json
"""
from __future__ import annotations

import argparse
import csv
import json
from pathlib import Path

from experiments.abstention_correct import gold_is_abstention, is_abstention


def _load(path: Path) -> dict[str, dict[str, str]]:
    with path.open(encoding="utf-8-sig", newline="") as fh:
        return {row["sample_id"]: row for row in csv.DictReader(fh)}


def _bool(value: str) -> bool:
    return str(value).strip().lower() == "true"


def _prf(tp: int, fp: int, fn: int, tn: int) -> dict[str, float | int]:
    return {
        "tp": tp, "fp": fp, "fn": fn, "tn": tn,
        "precision": tp / (tp + fp) if tp + fp else None,
        "recall": tp / (tp + fn) if tp + fn else None,
    }


def validate(key: dict, adj: dict, ann: dict) -> dict:
    stored_correct = [
        sid for sid in key
        if sid in adj and sid in ann and _bool(key[sid].get("stored_semantic_correct", ""))
    ]
    abstention_rows = []
    for sid in stored_correct:
        answer = ann[sid].get("model_answer") or ""
        reference = ann[sid].get("reference_answer") or ""
        if is_abstention(answer):
            abstention_rows.append({
                "sample_id": sid,
                "human_wrong": not _bool(adj[sid].get("adj_answer_correct", "")),
                "gold_is_abstention": gold_is_abstention(reference),
            })
    human_wrong = sum(1 for sid in stored_correct
                      if not _bool(adj[sid].get("adj_answer_correct", "")))

    def confusion(flip_predicate) -> dict:
        tp = fp = fn = tn = 0
        for sid in stored_correct:
            answer = ann[sid].get("model_answer") or ""
            reference = ann[sid].get("reference_answer") or ""
            predicted = flip_predicate(answer, reference)
            actual = not _bool(adj[sid].get("adj_answer_correct", ""))
            if predicted and actual:
                tp += 1
            elif predicted and not actual:
                fp += 1
            elif not predicted and actual:
                fn += 1
            else:
                tn += 1
        return _prf(tp, fp, fn, tn)

    naive = confusion(lambda answer, _reference: is_abstention(answer))
    guarded = confusion(
        lambda answer, reference: is_abstention(answer) and not gold_is_abstention(reference)
    )

    # 2x2 on the abstention subset alone.
    sub_tp = sum(1 for r in abstention_rows if not r["gold_is_abstention"] and r["human_wrong"])
    sub_fp = sum(1 for r in abstention_rows if not r["gold_is_abstention"] and not r["human_wrong"])
    sub_fn = sum(1 for r in abstention_rows if r["gold_is_abstention"] and r["human_wrong"])
    sub_tn = sum(1 for r in abstention_rows if r["gold_is_abstention"] and not r["human_wrong"])

    return {
        "stored_correct_sample": len(stored_correct),
        "human_wrong_in_sample": human_wrong,
        "abstention_style_rows": len(abstention_rows),
        "naive_rule": naive,
        "guarded_rule": guarded,
        "abstention_subset_2x2": {
            **_prf(sub_tp, sub_fp, sub_fn, sub_tn),
            "flipped_human_wrong": sub_tp,
            "flipped_human_correct": sub_fp,
            "preserved_human_wrong": sub_fn,
            "preserved_human_correct": sub_tn,
        },
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--key", default="results/annotation_package/key.csv")
    parser.add_argument("--adjudicated", default="results/annotation_package/adjudicated.csv")
    parser.add_argument("--annotations", default="results/annotation_package/annotations_annotator1.csv")
    parser.add_argument("--out", required=True)
    args = parser.parse_args()
    result = validate(_load(Path(args.key)), _load(Path(args.adjudicated)), _load(Path(args.annotations)))
    Path(args.out).write_text(json.dumps(result, ensure_ascii=False, indent=2), encoding="utf-8")
    print(json.dumps(result, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
