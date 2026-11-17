"""Validate V3 v3.2 blind annotation files and compute agreement.

Usage:
    python -m experiments.check_v3_annotations --a annotator_A.csv --b annotator_B.csv
"""
from __future__ import annotations

import argparse
import csv
import json
from collections import Counter

from experiments.check_annotations import cohen_kappa

DIMENSION_STATUS = {
    "EPISTEMIC": {"POSSIBLE", "ESTABLISHED", "UNKNOWN", "NOT_EXPRESSED", "UNRECOVERABLE"},
    "INTENTIONAL": {"CONSIDERING", "COMMITTED", "UNKNOWN", "NOT_EXPRESSED", "UNRECOVERABLE"},
    "CONDITIONAL": {"CONDITION_ACTIVE", "CONDITION_SATISFIED", "UNKNOWN",
                    "NOT_EXPRESSED", "UNRECOVERABLE"},
    "ACTION": {"ACTION_NOT_STARTED", "ACTION_STARTED", "UNKNOWN",
               "NOT_EXPRESSED", "UNRECOVERABLE"},
    "CANNOT_DETERMINE": {"UNKNOWN", "NOT_EXPRESSED", "UNRECOVERABLE"},
}

ALLOWED = {
    "proposition_identity": {"PRESERVED", "PARTIAL", "LOST", "AMBIGUOUS"},
    "primary_dimension": set(DIMENSION_STATUS),
    "status_expressed": {"YES", "NO", "UNCLEAR"},
    "expressed_status": set().union(*DIMENSION_STATUS.values()),
    "action_status": {"NOT_EXPRESSED", "NOT_PURSUING", "CONSIDERING",
                      "COMMITTED", "UNKNOWN", "NOT_APPLICABLE"},
    "evidence_support": {"SUPPORTED_BY_DIALOGUE", "CONTRADICTED_BY_LATER_DIALOGUE",
                         "NOT_SUPPORTED", "AMBIGUOUS", "NOT_ASSESSABLE"},
    "primary_judgment": {"NO_DISTORTION", "LEGITIMATE_UPDATE",
                         "UNSUPPORTED_STATUS_DISTORTION", "STATUS_OMISSION",
                         "PROPOSITION_LOSS", "AMBIGUOUS_UNASSESSABLE"},
    "confidence": {"HIGH", "MEDIUM", "LOW"},
}

REQUIRED = ("proposition_identity", "primary_dimension", "status_expressed",
            "primary_judgment", "confidence")


def load(path: str) -> list[dict]:
    with open(path, encoding="utf-8-sig", newline="") as handle:
        return list(csv.DictReader(handle))


def validate(rows: list[dict]) -> dict:
    report = {field: {"missing": 0, "invalid": []} for field in ALLOWED}
    for row in rows:
        for field, allowed in ALLOWED.items():
            value = (row.get(field) or "").strip()
            if not value:
                if field in REQUIRED:
                    report[field]["missing"] += 1
                continue
            if value not in allowed:
                report[field]["invalid"].append({"item_id": row.get("item_id"), "value": value})
        dimension = (row.get("primary_dimension") or "").strip()
        status = (row.get("expressed_status") or "").strip()
        expressed = (row.get("status_expressed") or "").strip()
        if dimension in DIMENSION_STATUS and status:
            if status not in DIMENSION_STATUS[dimension]:
                report["expressed_status"]["invalid"].append({
                    "item_id": row.get("item_id"),
                    "value": f"{status} incompatible with {dimension}",
                })
        if expressed == "NO" and status not in ("", "NOT_EXPRESSED", "UNRECOVERABLE"):
            report["expressed_status"]["invalid"].append({
                "item_id": row.get("item_id"),
                "value": f"{status} but status_expressed=NO",
            })
        if expressed == "YES" and status in ("NOT_EXPRESSED", "UNRECOVERABLE"):
            report["expressed_status"]["invalid"].append({
                "item_id": row.get("item_id"),
                "value": f"{status} but status_expressed=YES",
            })
        action = (row.get("action_status") or "").strip()
        if dimension == "CONDITIONAL":
            if not action:
                report["action_status"]["missing"] += 1
            elif action == "NOT_APPLICABLE":
                report["action_status"]["invalid"].append({
                    "item_id": row.get("item_id"),
                    "value": "NOT_APPLICABLE for CONDITIONAL item",
                })
        elif action and action != "NOT_APPLICABLE":
            report["action_status"]["invalid"].append({
                "item_id": row.get("item_id"),
                "value": f"{action} but primary_dimension={dimension}",
            })
        evidence = (row.get("evidence_support") or "").strip()
        if evidence == "SUPPORTED_BY_DIALOGUE" and (
                expressed in ("NO", "UNCLEAR")
                or status in ("NOT_EXPRESSED", "UNRECOVERABLE")):
            report["evidence_support"]["invalid"].append({
                "item_id": row.get("item_id"),
                "value": f"SUPPORTED_BY_DIALOGUE but status_expressed={expressed}",
            })
    return report


def agreement(a_rows: list[dict], b_rows: list[dict]) -> dict:
    a_map = {row["item_id"]: row for row in a_rows}
    b_map = {row["item_id"]: row for row in b_rows}
    common = sorted(set(a_map) & set(b_map))
    result = {"n_common_items": len(common), "fields": {}}
    for field in ALLOWED:
        pairs = []
        for key in common:
            left = a_map[key]
            right = b_map[key]
            if not (left.get(field) or "").strip() or not (right.get(field) or "").strip():
                continue
            if field == "expressed_status":
                dim_left = (left.get("primary_dimension") or "").strip()
                dim_right = (right.get("primary_dimension") or "").strip()
                if dim_left != dim_right:
                    continue
            pairs.append((left[field].strip(), right[field].strip()))
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
