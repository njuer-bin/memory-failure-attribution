"""Validate the v2.4 annotation files and compute inter-annotator agreement.

Usage:
    python -m experiments.check_annotations --a annotator_A.csv --b annotator_B.csv
"""
from __future__ import annotations

import argparse
import csv
import json
from collections import Counter

ALLOWED = {
    "proposition_identity": {"PRESERVED", "PARTIAL", "LOST", "AMBIGUOUS"},
    "polarity": {"POSITIVE", "NEGATIVE", "MIXED", "NOT_APPLICABLE", "UNCLEAR"},
    "epistemic_status": {"POSSIBLE", "PROBABLE", "CERTAIN", "UNKNOWN",
                         "EXPLICITLY_UNCERTAIN", "UNCLEAR", "NOT_APPLICABLE"},
    "intention_status": {"NONE", "CONSIDERING", "INTENDING", "COMMITTED",
                         "EXPLICITLY_NOT_INTENDED", "NOT_APPLICABLE"},
    "action_status": {"NOT_STARTED", "IN_PROGRESS", "COMPLETED", "ABANDONED",
                      "CANCELLED", "UNKNOWN", "NOT_APPLICABLE"},
    "condition_status": {"ACTIVE_UNSATISFIED", "ACTIVE_UNKNOWN", "SATISFIED",
                         "INVALIDATED", "NOT_APPLICABLE", "UNCLEAR"},
    "unsupported_status_change": {"YES", "NO", "UNCLEAR"},
}

AGREEMENT_FIELDS = list(ALLOWED)


def load(path: str) -> list[dict]:
    with open(path, encoding="utf-8-sig", newline="") as handle:
        return list(csv.DictReader(handle))


def key(row: dict) -> tuple[str, str, str]:
    return (row["trajectory_id"], row["condition"], row["depth"])


def validate(rows: list[dict]) -> dict:
    report = {}
    for field, allowed in ALLOWED.items():
        missing = []
        invalid = []
        for row in rows:
            value = (row.get(field) or "").strip()
            if not value:
                missing.append(key(row))
            elif value not in allowed:
                invalid.append({"key": key(row), "value": value})
        report[field] = {"missing": len(missing), "invalid": invalid}
    return report


def cohen_kappa(a: list[str], b: list[str]) -> float | None:
    n = len(a)
    if n == 0 or n != len(b):
        return None
    labels = sorted(set(a) | set(b))
    observed = sum(x == y for x, y in zip(a, b)) / n
    pa = Counter(a)
    pb = Counter(b)
    expected = sum((pa[label] / n) * (pb[label] / n) for label in labels)
    if expected == 1.0:
        return None
    return (observed - expected) / (1.0 - expected)


def agreement(a_rows: list[dict], b_rows: list[dict]) -> dict:
    a_map = {key(row): row for row in a_rows}
    b_map = {key(row): row for row in b_rows}
    common = sorted(set(a_map) & set(b_map))
    result = {"n_common_items": len(common), "fields": {}}
    for field in AGREEMENT_FIELDS:
        pairs = [(a_map[k][field].strip(), b_map[k][field].strip())
                 for k in common
                 if (a_map[k].get(field) or "").strip() and (b_map[k].get(field) or "").strip()]
        labels_a = [x for x, _ in pairs]
        labels_b = [y for _, y in pairs]
        n = len(pairs)
        raw = sum(x == y for x, y in pairs) / n if n else None
        result["fields"][field] = {
            "n_pairs": n,
            "raw_agreement": raw,
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
        missing = sum(v["missing"] for v in report.values())
        invalid = sum(len(v["invalid"]) for v in report.values())
        print(f"{name}: rows={len(rows)} missing_labels={missing} invalid_values={invalid}")
        for field, value in report.items():
            if value["missing"] or value["invalid"]:
                print(f"  {field}: missing={value['missing']} invalid={len(value['invalid'])}")
                for item in value["invalid"][:5]:
                    print(f"    invalid {item['value']!r} at {item['key']}")

    print("\n=== agreement ===")
    result = agreement(a_rows, b_rows)
    print(f"common items: {result['n_common_items']}")
    for field, value in result["fields"].items():
        kappa = value["cohen_kappa"]
        raw = value["raw_agreement"]
        print(f"{field:<28} n={value['n_pairs']:<4} raw={raw if raw is None else round(raw, 3)} "
              f"kappa={kappa if kappa is None else round(kappa, 3)}")
    print("\n" + json.dumps(result, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
