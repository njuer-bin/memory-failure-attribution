"""Score round-3 per-fact gate annotations.

Aggregates fact-level labels to a row gate and reports:

- fact-level inter-annotator agreement/kappa (yes/no co-decided rows);
- row-level inter-annotator agreement/kappa on the aggregated gate;
- consensus gate vs the 200 adjudicated human labels (precision/recall/F1 for
  "insufficient") against the automatic stored gate as baseline.

Acceptance (pre-registered): fact-level kappa >= 0.6 AND row-level kappa >= 0.6.

Usage:
    python -m experiments.score_fact_annotations \
        --key results/annotation_package/round3_key.csv \
        --labels annotator1=results/annotation_package/round3_fact_presence_annotated1.csv \
        --labels annotator2=results/annotation_package/round3_fact_presence_annotated2.csv \
        --out results/analysis_annotations_round3.json
"""
from __future__ import annotations

import argparse
import csv
import json
from collections import defaultdict
from pathlib import Path
from typing import Any, Iterable

from evaluation.paired_stats import agreement, cohens_kappa

YES = {"yes", "y", "true", "1"}
NO = {"no", "n", "false", "0"}


def _load(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8-sig", newline="") as fh:
        return list(csv.DictReader(fh))


def _label(value: str) -> bool | str | None:
    text = (value or "").strip().lower()
    if text in YES:
        return True
    if text in NO:
        return False
    if text == "uncertain":
        return "UNC"
    return None


def aggregate_row(facts: Iterable[tuple[str, bool | str | None]]) -> str | None:
    """Aggregate (group, label) facts into sufficient/insufficient/uncertain.

    Required facts (empty group) must all be present. A non-empty group passes
    if at least one member is present. Unlabelled facts make the row unknown.
    """
    groups: dict[str, list[bool | str | None]] = defaultdict(list)
    required: list[bool | str | None] = []
    for group, label in facts:
        if group:
            groups[group].append(label)
        else:
            required.append(label)

    insufficient = False
    uncertain = False
    for label in required:
        if label is None:
            return None
        if label is False:
            insufficient = True
        elif label == "UNC":
            uncertain = True
    for members in groups.values():
        if any(m is None for m in members) and not any(m is True for m in members):
            return None
        if any(m is True for m in members):
            continue
        if any(m == "UNC" for m in members):
            uncertain = True
        else:
            insufficient = True
    if insufficient:
        return "insufficient"
    if uncertain:
        return "uncertain"
    return "sufficient"


def _row_gates(key: list[dict[str, str]], labels: dict[str, dict[str, str]],
               uncertain_as_insufficient: bool = False) -> dict[str, str | None]:
    rows: dict[str, list[tuple[str, bool | str | None]]] = defaultdict(list)
    for fact in key:
        label = _label(labels.get(fact["fact_id"], {}).get("fact_present_yes_no_uncertain", ""))
        rows[fact["sample_id"]].append((fact["group"], label))
    gates: dict[str, str | None] = {}
    for sid, facts in rows.items():
        gate = aggregate_row(facts)
        if uncertain_as_insufficient and gate == "uncertain":
            # An unresolvable relative date means the reference cannot be derived
            # from the evidence, which is the gate's definition of insufficient
            # (and the round-1 adjudication rule). Kept as the primary mapping.
            gate = "insufficient"
        gates[sid] = gate
    return gates


def _prf(gold: list[bool], pred: list[bool]) -> dict[str, Any]:
    tp = sum(1 for g, p in zip(gold, pred) if g and p)
    fp = sum(1 for g, p in zip(gold, pred) if not g and p)
    fn = sum(1 for g, p in zip(gold, pred) if g and not p)
    precision = tp / (tp + fp) if tp + fp else None
    recall = tp / (tp + fn) if tp + fn else None
    f1 = (2 * precision * recall / (precision + recall)
          if precision is not None and recall is not None and precision + recall else None)
    return {"tp": tp, "fp": fp, "fn": fn, "n": len(gold),
            "precision": precision, "recall": recall, "f1": f1}


def _row_level(gates_a: dict[str, str | None], gates_b: dict[str, str | None]) -> dict[str, Any]:
    ra, rb = [], []
    for sid in gates_a:
        ga, gb = gates_a[sid], gates_b[sid]
        if ga in ("sufficient", "insufficient") and gb in ("sufficient", "insufficient"):
            ra.append(ga == "insufficient")
            rb.append(gb == "insufficient")
    return {"n": len(ra), "agreement": agreement(ra, rb), "kappa": cohens_kappa(ra, rb)}


def _consensus(
    meta: dict[str, dict[str, str]],
    gates_a: dict[str, str | None],
    gates_b: dict[str, str | None],
) -> dict[str, Any]:
    cons_gold, cons_pred = [], []
    store_gold, store_pred = [], []
    by_benchmark: dict[str, dict[str, list[bool]]] = defaultdict(
        lambda: {"gold": [], "pred": [], "stored": []}
    )
    for sid, ga in gates_a.items():
        gb = gates_b[sid]
        if ga != gb or ga not in ("sufficient", "insufficient"):
            continue
        adj = (meta[sid].get("adjudicated_gate") or "").strip().lower()
        if adj not in {"true", "false"}:
            continue
        stored = (meta[sid].get("stored_gate") or "").strip().lower()
        if stored not in {"sufficient", "insufficient"}:
            continue  # keep both instruments on the same rows
        gold = adj == "false"  # positive class = insufficient
        pred = ga == "insufficient"
        cons_gold.append(gold)
        cons_pred.append(pred)
        store_gold.append(gold)
        store_pred.append(stored == "insufficient")
        bench = meta[sid].get("benchmark", "")
        by_benchmark[bench]["gold"].append(gold)
        by_benchmark[bench]["pred"].append(pred)
        by_benchmark[bench]["stored"].append(stored == "insufficient")
    return {
        "n": len(cons_gold),
        "fact_gate": _prf(cons_gold, cons_pred),
        "stored_gate": _prf(store_gold, store_pred) if store_gold else None,
        "by_benchmark": {
            bench: {"n": len(vals["gold"]), "fact_gate": _prf(vals["gold"], vals["pred"]),
                    "stored_gate": _prf(vals["gold"], vals["stored"])}
            for bench, vals in sorted(by_benchmark.items())
        },
    }


def score(key: list[dict[str, str]], labels: dict[str, dict[str, dict[str, str]]]) -> dict[str, Any]:
    names = list(labels)
    fact_ids = [f["fact_id"] for f in key]
    result: dict[str, Any] = {"annotators": names, "n_facts": len(fact_ids)}

    # Fact level.
    a, b = [], []
    for fid in fact_ids:
        la = _label(labels[names[0]].get(fid, {}).get("fact_present_yes_no_uncertain", ""))
        lb = _label(labels[names[1]].get(fid, {}).get("fact_present_yes_no_uncertain", ""))
        if la in (True, False) and lb in (True, False):
            a.append(bool(la))
            b.append(bool(lb))
    result["fact_level"] = {
        "n": len(a), "agreement": agreement(a, b), "kappa": cohens_kappa(a, b),
        "uncertain_or_blank": len(fact_ids) - len(a),
    }

    # Row level. Primary mapping: an unresolved-date row counts as insufficient
    # (the reference is not derivable from the evidence). Sensitivity leaves it
    # out of the estimate entirely.
    primary = {name: _row_gates(key, labels[name], uncertain_as_insufficient=True) for name in names}
    sensitivity = {name: _row_gates(key, labels[name], uncertain_as_insufficient=False) for name in names}
    result["row_level_inter_annotator"] = {
        "primary_uncertain_as_insufficient": _row_level(primary[names[0]], primary[names[1]]),
        "sensitivity_excluding_uncertain": _row_level(sensitivity[names[0]], sensitivity[names[1]]),
    }

    # Consensus gate vs adjudicated human labels, and stored-gate baseline.
    meta = {f["sample_id"]: f for f in key}
    result["consensus_vs_adjudicated"] = {
        "primary_uncertain_as_insufficient": _consensus(meta, primary[names[0]], primary[names[1]]),
        "sensitivity_excluding_uncertain": _consensus(meta, sensitivity[names[0]], sensitivity[names[1]]),
    }
    result["by_benchmark"] = result["consensus_vs_adjudicated"][
        "primary_uncertain_as_insufficient"]["by_benchmark"]
    result["acceptance"] = {
        "fact_kappa": result["fact_level"]["kappa"],
        "row_kappa": result["row_level_inter_annotator"][
            "primary_uncertain_as_insufficient"]["kappa"],
        "passed": bool(
            result["fact_level"]["kappa"] is not None
            and result["row_level_inter_annotator"]["primary_uncertain_as_insufficient"]["kappa"] is not None
            and result["fact_level"]["kappa"] >= 0.6
            and result["row_level_inter_annotator"]["primary_uncertain_as_insufficient"]["kappa"] >= 0.6
        ),
        "bar": 0.6,
    }
    return result


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--key", required=True)
    parser.add_argument("--labels", action="append", required=True)
    parser.add_argument("--out", default=None)
    args = parser.parse_args()
    key = _load(Path(args.key))
    labels = {}
    for spec in args.labels:
        name, path = spec.split("=", 1)
        labels[name] = {row["fact_id"]: row for row in _load(Path(path))}
    result = score(key, labels)
    text = json.dumps(result, ensure_ascii=False, indent=2)
    if args.out:
        Path(args.out).write_text(text, encoding="utf-8")
    print(text)


if __name__ == "__main__":
    main()
