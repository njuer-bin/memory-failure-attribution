"""Score human annotation against the automatic evaluator and each other.

Inputs are the files produced by ``build_annotation_package.py``: the hidden
``key.csv`` plus one filled ``annotations.csv`` per annotator. Outputs:

- inter-annotator agreement and Cohen's kappa for answer correctness and
  evidence sufficiency;
- evaluator precision/recall/F1 against the adjudicated human label, for both
  targets;
- the count of rows excluded as ``uncertain`` / blank.

Usage:
    python -m experiments.score_annotations \
        --key results/annotation_package/key.csv \
        --labels annotator1=results/annotation_package/annotations.csv \
        --labels annotator2=results/annotation_package/annotations_a2.csv
"""
from __future__ import annotations

import argparse
import csv
import json
from pathlib import Path
from typing import Any

from evaluation.paired_stats import agreement, cohens_kappa

YES = {"yes", "y", "true", "1"}
NO = {"no", "n", "false", "0"}


def _load_csv(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8", newline="") as fh:
        return list(csv.DictReader(fh))


def _label(value: str) -> bool | None:
    text = (value or "").strip().lower()
    if text in YES:
        return True
    if text in NO:
        return False
    return None


def _stored(value: str) -> bool | None:
    text = (value or "").strip()
    if text == "True":
        return True
    if text == "False":
        return False
    return None


def precision_recall_f1(gold: list[bool], predicted: list[bool]) -> dict[str, Any]:
    tp = sum(1 for g, p in zip(gold, predicted) if g and p)
    fp = sum(1 for g, p in zip(gold, predicted) if not g and p)
    fn = sum(1 for g, p in zip(gold, predicted) if g and not p)
    precision = tp / (tp + fp) if tp + fp else None
    recall = tp / (tp + fn) if tp + fn else None
    f1 = (2 * precision * recall / (precision + recall)
          if precision is not None and recall is not None and precision + recall else None)
    return {"tp": tp, "fp": fp, "fn": fn, "precision": precision,
            "recall": recall, "f1": f1, "n": len(gold)}


def score(key: dict[str, dict[str, str]], labels: dict[str, dict[str, dict[str, str]]]) -> dict[str, Any]:
    names = list(labels)
    result: dict[str, Any] = {"annotators": names, "fields": {}}
    for field, target in (
        ("answer_correct_yes_no_uncertain", "stored_semantic_correct"),
        ("evidence_sufficient_yes_no_uncertain", "gate_status"),
    ):
        # Inter-annotator agreement over rows both labelled yes/no.
        if len(names) >= 2:
            a_all = labels[names[0]]
            b_all = labels[names[1]]
            a, b = [], []
            for sid in sorted(key):
                if sid not in a_all or sid not in b_all:
                    continue
                la = _label(a_all[sid].get(field, ""))
                lb = _label(b_all[sid].get(field, ""))
                if la is not None and lb is not None:
                    a.append(la)
                    b.append(lb)
            result[f"inter_annotator_{field}"] = {
                "n": len(a),
                "agreement": agreement(a, b),
                "kappa": cohens_kappa(a, b),
            }

        # Evaluator vs the adjudicated label (use the first annotator, or the
        # intersection where both agree; disagreements are reported separately).
        human: list[bool] = []
        auto: list[bool] = []
        excluded = 0
        for sid, row in key.items():
            if sid not in labels[names[0]]:
                excluded += 1
                continue
            labels_for_row = [_label(labels[name][sid].get(field, ""))
                              for name in names if sid in labels[name]]
            decided = {x for x in labels_for_row if x is not None}
            if len(decided) != 1:
                excluded += 1
                continue
            if target == "gate_status":
                status = row.get("gate_status", "")
                stored = (True if status == "sufficient"
                          else False if status == "insufficient" else None)
            else:
                stored = _stored(row.get(target, ""))
            if stored is None:
                excluded += 1
                continue
            human.append(decided.pop())
            auto.append(stored)
        result["fields"][field] = {
            "evaluator_vs_human": precision_recall_f1(human, auto),
            "excluded_uncertain_or_missing": excluded,
        }
    return result


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--key", required=True)
    parser.add_argument("--labels", action="append", required=True,
                        help="name=annotations.csv (repeatable)")
    parser.add_argument("--out", default=None)
    args = parser.parse_args()
    key = {row["sample_id"]: row for row in _load_csv(Path(args.key))}
    labels = {}
    for spec in args.labels:
        name, path = spec.split("=", 1)
        labels[name] = {row["sample_id"]: row for row in _load_csv(Path(path))}
    result = score(key, labels)
    text = json.dumps(result, ensure_ascii=False, indent=2)
    if args.out:
        Path(args.out).write_text(text, encoding="utf-8")
    print(text)


if __name__ == "__main__":
    main()
