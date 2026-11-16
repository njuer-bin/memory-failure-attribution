"""Validate V3 blind annotation files and compute inter-annotator agreement.

Usage:
    python -m experiments.check_v3_annotations --a annotator_A.csv --b annotator_B.csv
"""
from __future__ import annotations

import argparse
import csv
import json
from collections import Counter

from experiments.check_annotations import cohen_kappa

ALLOWED = {
    "proposition_identity": {"PRESERVED", "PARTIAL", "LOST", "AMBIGUOUS"},
    "epistemic_applicable": {"APPLICABLE", "NOT_APPLICABLE", "CANNOT_DETERMINE"},
    "intentional_applicable": {"APPLICABLE", "NOT_APPLICABLE", "CANNOT_DETERMINE"},
    "conditional_applicable": {"APPLICABLE", "NOT_APPLICABLE", "CANNOT_DETERMINE"},
    "action_applicable": {"APPLICABLE", "NOT_APPLICABLE", "CANNOT_DETERMINE"},
    "epistemic_status": {"UNKNOWN", "POSSIBLE", "PROBABLE", "SUPPORTED", "ESTABLISHED",
                         "REJECTED", "UNEXPRESSED", "UNRECOVERABLE", "NOT_APPLICABLE"},
    "intention_status": {"NOT_EXPRESSED", "CONSIDERING", "INTERESTED", "INTENDING",
                         "COMMITTED", "EXECUTING", "COMPLETED", "CANCELLED",
                         "NOT_INTENDED", "UNRECOVERABLE", "NOT_APPLICABLE"},
    "action_status": {"NOT_EXPRESSED", "CONSIDERING", "INTENDING", "COMMITTED",
                      "EXECUTING", "COMPLETED", "CANCELLED", "UNKNOWN", "NOT_APPLICABLE"},
    "condition_status": {"UNKNOWN", "ACTIVE_UNSATISFIED", "SATISFIED", "FAILED",
                         "WAIVED", "NOT_APPLICABLE", "UNRECOVERABLE"},
    "evidence_support": {"SUPPORTED_BY_DIALOGUE", "CONTRADICTED_BY_LATER_DIALOGUE",
                         "NOT_SUPPORTED", "AMBIGUOUS", "NOT_ASSESSABLE"},
    "primary_judgment": {"NO_DISTORTION", "LEGITIMATE_UPDATE",
                         "UNSUPPORTED_STATUS_DISTORTION", "STATUS_OMISSION",
                         "PROPOSITION_LOSS", "AMBIGUOUS_UNASSESSABLE"},
    "confidence": {"HIGH", "MEDIUM", "LOW"},
}

REQUIRED = ("proposition_identity", "primary_judgment", "confidence")


def load(path: str) -> list[dict]:
    with open(path, encoding="utf-8-sig", newline="") as handle:
        return list(csv.DictReader(handle))


def validate(rows: list[dict]) -> dict:
    report = {}
    for field, allowed in ALLOWED.items():
        missing = []
        invalid = []
        for row in rows:
            value = (row.get(field) or "").strip()
            if not value:
                if field in REQUIRED:
                    missing.append(row.get("item_id"))
            elif value not in allowed:
                invalid.append({"item_id": row.get("item_id"), "value": value})
        report[field] = {"missing": len(missing), "invalid": invalid}
    return report


def agreement(a_rows: list[dict], b_rows: list[dict]) -> dict:
    a_map = {row["item_id"]: row for row in a_rows}
    b_map = {row["item_id"]: row for row in b_rows}
    common = sorted(set(a_map) & set(b_map))
    result = {"n_common_items": len(common), "fields": {}}
    for field in ALLOWED:
        pairs = [(a_map[key][field].strip(), b_map[key][field].strip())
                 for key in common
                 if (a_map[key].get(field) or "").strip()
                 and (b_map[key].get(field) or "").strip()]
        labels_a = [x for x, _ in pairs]
        labels_b = [y for _, y in pairs]
        n = len(pairs)
        result["fields"][field] = {
            "n_pairs": n,
            "raw_agreement": (sum(x == y for x, y in pairs) / n if n else None),
            "cohen_kappa": cohen_kappa(labels_a, labels_b),
            "label_counts_a": dict(Counter(labels_a)),
            "label_counts_b": dict(Counter(labels_b)),
        }
    return result


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--a", required=True)
    parser.add_argument("--b", required=True)
    args = parser.parse_args()

    a_rows, b_rows = load(args.a), load(args.b)
    print("=== validation ===")
    for name, rows in (("A", a_rows), ("B", b_rows)):
        report = validate(rows)
        missing = sum(value["missing"] for value in report.values())
        invalid = sum(len(value["invalid"]) for value in report.values())
        print(f"{name}: rows={len(rows)} missing_required={missing} invalid_values={invalid}")
        for field, value in report.items():
            if value["missing"] or value["invalid"]:
                print(f"  {field}: missing={value['missing']} invalid={len(value['invalid'])}")
                for item in value["invalid"][:5]:
                    print(f"    invalid {item['value']!r} at {item['item_id']}")

    print("\n=== agreement ===")
    result = agreement(a_rows, b_rows)
    print(f"common items: {result['n_common_items']}")
    for field, value in result["fields"].items():
        raw = value["raw_agreement"]
        kappa = value["cohen_kappa"]
        print(f"{field:<26} n={value['n_pairs']:<4} "
              f"raw={raw if raw is None else round(raw, 3)} "
              f"kappa={kappa if kappa is None else round(kappa, 3)}")
    print("\n" + json.dumps(result, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
