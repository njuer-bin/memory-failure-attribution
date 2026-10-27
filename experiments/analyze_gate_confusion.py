"""Explicit gate-vs-human confusion matrix with both polarities stated.

The 2026-10-25 prose report reversed two counts. This script makes the polarity
unambiguous: for positive = "insufficient", ``fn`` is the number of truly
insufficient rows the gate misses and ``fp`` is the number of sufficient rows
the gate falsely calls insufficient.

Usage:
    python -m experiments.analyze_gate_confusion \
        --out results/analysis_gate_confusion_n200.json
"""
from __future__ import annotations

import argparse
import csv
import json
from collections import defaultdict
from pathlib import Path


def _load(path: Path) -> dict[str, dict[str, str]]:
    with path.open(encoding="utf-8-sig", newline="") as fh:
        return {row["sample_id"]: row for row in csv.DictReader(fh)}


def _confusion(pairs: list[tuple[bool, bool]]) -> dict:
    """pairs of (human_insufficient, gate_insufficient)."""
    tp = sum(1 for h, g in pairs if h and g)
    fp = sum(1 for h, g in pairs if not h and g)
    fn = sum(1 for h, g in pairs if h and not g)
    tn = sum(1 for h, g in pairs if not h and not g)
    return {
        "positive": "insufficient",
        "tp_both_insufficient": tp,
        "fp_gate_insufficient_human_sufficient": fp,
        "fn_gate_sufficient_human_insufficient": fn,
        "tn_both_sufficient": tn,
        "n": tp + fp + fn + tn,
        "missed_truly_insufficient": fn,
        "falsely_called_insufficient": fp,
        "precision_if_insufficient_positive": tp / (tp + fp) if tp + fp else None,
        "recall_if_insufficient_positive": tp / (tp + fn) if tp + fn else None,
        "precision_if_sufficient_positive": tn / (tn + fn) if tn + fn else None,
        "recall_if_sufficient_positive": tn / (tn + fp) if tn + fp else None,
    }


def analyze(key: dict, adj: dict) -> dict:
    by_bench: dict[str, list[tuple[bool, bool]]] = defaultdict(list)
    all_pairs: list[tuple[bool, bool]] = []
    for sid, k in key.items():
        if sid not in adj:
            continue
        gate = (k.get("gate_status") or "").strip().lower()
        human = (adj[sid].get("adj_evidence_sufficient") or "").strip().lower()
        if gate not in {"sufficient", "insufficient"} or human not in {"true", "false"}:
            continue
        pair = (human == "false", gate == "insufficient")
        all_pairs.append(pair)
        by_bench[sid.split("-")[0]].append(pair)
    return {
        "source": {"key": "results/annotation_package/key.csv",
                   "adjudicated": "results/annotation_package/adjudicated.csv"},
        "overall": _confusion(all_pairs),
        "by_benchmark": {b: _confusion(p) for b, p in sorted(by_bench.items())},
        "note": ("Both polarities are reported. The earlier prose in "
                 "analysis_annotations_adjudicated_n200.json swapped the two "
                 "counts; this file is authoritative."),
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--key", default="results/annotation_package/key.csv")
    parser.add_argument("--adjudicated", default="results/annotation_package/adjudicated.csv")
    parser.add_argument("--out", required=True)
    args = parser.parse_args()
    result = analyze(_load(Path(args.key)), _load(Path(args.adjudicated)))
    Path(args.out).write_text(json.dumps(result, ensure_ascii=False, indent=2), encoding="utf-8")
    print(json.dumps(result, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
