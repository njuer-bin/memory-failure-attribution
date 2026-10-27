"""Score round-5 stage annotations with multiclass Cohen's kappa.

The project's `evaluation.paired_stats.cohens_kappa` is binary-only; passing
string labels to it silently coerces to booleans and reports a spurious 1.0.
This scorer implements multiclass kappa, the human-human confusion matrix, the
human-vs-automatic confusion matrix, and the uncertain share.

Labels: formation | storage | retrieval | rerank | context | none | e0 |
uncertain. `evolution` is not measured and is treated as invalid.

Usage:
    python -m experiments.score_stage_annotations \
        --key results/annotation_package/round5_stage_pilot_v2_key.csv \
        --labels a=results/annotation_package/round5_stage_pilot_v2_review1.csv \
        --labels b=results/annotation_package/round5_stage_pilot_v2_review2.csv \
        --out results/analysis_round5_pilot_v2.json
"""
from __future__ import annotations

import argparse
import csv
import json
from collections import Counter
from pathlib import Path
from typing import Any

VALID = {"formation", "storage", "retrieval", "rerank", "context", "none", "e0", "uncertain"}
AUTO_MAP = {
    "F1_FORMATION": "formation",
    "F2_STORAGE": "storage",
    "F3_EVOLUTION": "uncertain",
    "F4_RETRIEVAL": "retrieval",
    "F5_CONTEXT": "context",
    "F6_REASONING_CANDIDATE": "none",
    "E0_EVIDENCE_INSUFFICIENT": "e0",
    "EVAL_SEMANTIC_UNCERTAIN": "uncertain",
    "none": "none",
    "E0": "e0",
}


def _load(path: Path) -> dict[str, dict[str, str]]:
    with path.open(encoding="utf-8-sig", newline="") as fh:
        return {row["row_id"]: row for row in csv.DictReader(fh)}


def _label(row: dict[str, str] | None) -> str | None:
    value = ((row or {}).get("annotated_first_loss_stage") or "").strip().lower()
    return value or None


def kappa_multi(a: list[str], b: list[str]) -> float | None:
    n = len(a)
    if n == 0:
        return None
    po = sum(1 for x, y in zip(a, b) if x == y) / n
    categories = set(a) | set(b)
    pe = sum((a.count(c) / n) * (b.count(c) / n) for c in categories)
    return (po - pe) / (1 - pe) if pe < 1 else 1.0


def _auto(row: dict[str, str]) -> str | None:
    return AUTO_MAP.get((row.get("auto_first_loss") or "").strip())


def _confusion(a: list[str], b: list[str]) -> dict[str, int]:
    return {f"{x}->{y}": n for (x, y), n in sorted(Counter(zip(a, b)).items())}


def score(key: dict[str, dict[str, str]],
          labels: dict[str, dict[str, dict[str, str]]]) -> dict[str, Any]:
    names = list(labels)
    rows = sorted(key)
    pair = [(rid, _label(labels[names[0]].get(rid)), _label(labels[names[1]].get(rid))) for rid in rows]
    valid_pairs = [(rid, a, b) for rid, a, b in pair if a in VALID and b in VALID]
    x = [a for _, a, _ in valid_pairs]
    y = [b for _, _, b in valid_pairs]
    no_unc = [(a, b) for a, b in zip(x, y) if a != "uncertain" and b != "uncertain"]
    result: dict[str, Any] = {
        "annotators": names,
        "rows": len(rows),
        "valid_co_decided": len(valid_pairs),
        "invalid_or_missing": {
            "a": dict(Counter(a for _, a, _ in pair if a not in VALID)),
            "b": dict(Counter(b for _, _, b in pair if b not in VALID)),
        },
        "uncertain_share": {
            "a": (x.count("uncertain") / len(x)) if x else None,
            "b": (y.count("uncertain") / len(y)) if y else None,
        },
        "human_human": {
            "n": len(x),
            "agreement": (sum(1 for i, j in zip(x, y) if i == j) / len(x)) if x else None,
            "kappa_multi": kappa_multi(x, y),
            "confusion": _confusion(x, y),
            "excluding_uncertain": {
                "n": len(no_unc),
                "agreement": (sum(1 for a, b in no_unc if a == b) / len(no_unc)) if no_unc else None,
                "kappa_multi": kappa_multi([a for a, _ in no_unc], [b for _, b in no_unc]) if no_unc else None,
            },
            "classes_used": sorted(set(x) | set(y)),
        },
        "human_vs_auto": {},
    }
    for name in names:
        pairs = [(rid, _label(labels[name].get(rid)), _auto(key[rid])) for rid in rows]
        sel = [(a, b) for _, a, b in pairs if a in VALID and b in VALID]
        result["human_vs_auto"][name] = {
            "n": len(sel),
            "agreement": (sum(1 for i, j in zip(*zip(*sel)) if i == j) / len(sel)) if sel else None,
            "kappa_multi": (kappa_multi([a for a, _ in sel], [b for _, b in sel]) if sel else None),
            "confusion": _confusion([a for a, _ in sel], [b for _, b in sel]) if sel else {},
        }
    result["acceptance"] = {
        "bar": 0.70,
        "kappa": result["human_human"]["kappa_multi"],
        "passed": bool(result["human_human"]["kappa_multi"] is not None
                       and result["human_human"]["kappa_multi"] >= 0.70),
    }
    return result


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--key", required=True)
    parser.add_argument("--labels", action="append", required=True,
                        help="name=sheet.csv (repeatable, exactly two)")
    parser.add_argument("--out", default=None)
    args = parser.parse_args()
    key = _load(Path(args.key))
    labels = {}
    for spec in args.labels:
        name, path = spec.split("=", 1)
        labels[name] = _load(Path(path))
    if len(labels) != 2:
        raise SystemExit("exactly two --labels sheets are required for kappa")
    result = score(key, labels)
    text = json.dumps(result, ensure_ascii=False, indent=2)
    if args.out:
        Path(args.out).write_text(text, encoding="utf-8")
    print(text)


if __name__ == "__main__":
    main()
