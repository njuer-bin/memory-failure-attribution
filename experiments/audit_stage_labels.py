"""Audit the stage-label instrument beyond Cohen's kappa.

Three readouts, all label-only (no model calls):

1. Per-class precision/recall/F1 of the automatic first-loss label against each
   annotator and against their consensus, with percentile bootstrap CIs over
   rows. The 40-row round-5 v2 pilot is the only human stage annotation that
   exists; everything here is scoped to it.
2. Per-system stage distributions under the automatic vs human labels on the
   same pilot rows (the pilot sampled semantic and verbatim questions).
3. Monte-Carlo misclassification sensitivity for the n=100 fingerprint: perturb
   a share q of stored automatic labels, redrawing from (A) the empirical
   auto->human confusion estimated on the pilot, or (B) a uniform swap over the
   observed classes, and report the share of draws that keep each pair's
   Stuart-Maxwell p < 0.05.

Usage:
    python -m experiments.audit_stage_labels \
        --key results/annotation_package/round5_stage_pilot_v2_key.csv \
        --labels a=..._review1.csv --labels b=..._review2.csv \
        --fingerprint results/systems_locomo_n200_fixedgate/comparison.jsonl \
        --out results/analysis_stage_label_audit.json
"""
from __future__ import annotations

import argparse
import json
import random
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any

from evaluation.stage_distribution_tests import stuart_maxwell
from experiments.score_stage_annotations import (
    VALID,
    _auto,
    _confusion,
    _label,
    _load,
    kappa_multi,
)

CLASSES = ["e0", "formation", "none", "rerank", "retrieval", "context", "storage"]

# Map the pilot's reduced stage vocabulary onto the stored run labels.
PILOT_TO_FULL = {
    "formation": "F1_FORMATION",
    "storage": "F2_STORAGE",
    "retrieval": "F4_RETRIEVAL",
    "rerank": "F4_RETRIEVAL",
    "context": "F5_CONTEXT",
    "e0": "E0_EVIDENCE_INSUFFICIENT",
    "none": "none",
}

# Inverse map used to bring stored run labels into the pilot taxonomy, where
# the noise model is estimated. EVAL rows pass through as their own class.
FULL_TO_PILOT = {
    "F1_FORMATION": "formation",
    "F2_STORAGE": "storage",
    "F3_EVOLUTION": "evolution",
    "F4_RETRIEVAL": "retrieval",
    "F5_CONTEXT": "context",
    "F6_REASONING_CANDIDATE": "none",
    "E0_EVIDENCE_INSUFFICIENT": "e0",
    "E0": "e0",
    "EVAL_SEMANTIC_UNCERTAIN": "eval",
    "none": "none",
}


def _to_pilot(labels: list[str]) -> list[str]:
    return [FULL_TO_PILOT.get(label, label) for label in labels]


def _confusion_matrix(pairs: list[tuple[str, str]], classes: list[str]) -> dict[str, dict[str, int]]:
    matrix = {h: {a: 0 for a in classes} for h in classes}
    for human, auto in pairs:
        if human in matrix and auto in matrix[human]:
            matrix[human][auto] += 1
    return matrix


def _per_class(pairs: list[tuple[str, str]], classes: list[str]) -> dict[str, dict[str, Any]]:
    out = {}
    for c in classes:
        tp = sum(1 for h, a in pairs if h == c and a == c)
        fp = sum(1 for h, a in pairs if h != c and a == c)
        fn = sum(1 for h, a in pairs if h == c and a != c)
        precision = tp / (tp + fp) if (tp + fp) else None
        recall = tp / (tp + fn) if (tp + fn) else None
        if precision is not None and recall is not None and (precision + recall) > 0:
            f1 = 2 * precision * recall / (precision + recall)
        elif precision is None or recall is None:
            f1 = None
        else:
            f1 = 0.0
        out[c] = {
            "support": tp + fn,
            "predicted": tp + fp,
            "precision": precision,
            "recall": recall,
            "f1": f1,
        }
    return out


def _bootstrap_metrics(
    pairs: list[tuple[str, str]],
    classes: list[str],
    repeats: int,
    seed: int,
) -> dict[str, dict[str, list[float] | None]]:
    rng = random.Random(seed)
    draws: dict[str, dict[str, list[float]]] = defaultdict(lambda: defaultdict(list))
    n = len(pairs)
    if not n:
        return {}
    for _ in range(repeats):
        sample = [pairs[rng.randrange(n)] for _ in range(n)]
        metrics = _per_class(sample, classes)
        for c, values in metrics.items():
            for key in ("precision", "recall", "f1"):
                if values[key] is not None:
                    draws[c][key].append(values[key])
    out: dict[str, dict[str, list[float] | None]] = {}
    for c in classes:
        entry: dict[str, list[float] | None] = {}
        for key in ("precision", "recall", "f1"):
            values = sorted(draws[c][key])
            if len(values) < repeats // 10:
                entry[key] = None
            else:
                lo = values[int(0.025 * len(values))]
                hi = values[min(len(values) - 1, int(0.975 * len(values)))]
                entry[key] = [lo, hi]
        out[c] = entry
    return out


def _metrics_block(
    human: list[str],
    auto: list[str],
    classes: list[str],
    repeats: int,
    seed: int,
) -> dict[str, Any]:
    pairs = list(zip(human, auto))
    return {
        "n": len(pairs),
        "agreement": (sum(1 for h, a in pairs if h == a) / len(pairs)) if pairs else None,
        "kappa_multi": kappa_multi(human, auto) if pairs else None,
        "confusion": _confusion(human, auto),
        "matrix": _confusion_matrix(pairs, classes),
        "per_class": _per_class(pairs, classes),
        "per_class_ci95": _bootstrap_metrics(pairs, classes, repeats, seed),
    }


def _dist(values: list[str]) -> dict[str, Any]:
    counts = Counter(values)
    total = sum(counts.values()) or 1
    top = counts.most_common()
    return {
        "counts": dict(sorted(counts.items())),
        "shares": {k: v / total for k, v in sorted(counts.items())},
        "dominant": top[0][0] if top else None,
    }


def _load_fingerprint(path: Path) -> dict[str, dict[str, Any]]:
    rows = {}
    for line in path.read_text(encoding="utf-8").splitlines():
        if not line.strip():
            continue
        row = json.loads(line)
        if isinstance(row, dict) and row.get("question_id"):
            rows[str(row["question_id"])] = row
    return rows


def _labels_for(rows: dict[str, dict[str, Any]], system: str) -> list[str]:
    return [
        (row.get("modes", {}).get(system, {}).get("answer_failure_type") or "none")
        for row in rows.values()
        if system in (row.get("modes") or {})
    ]


def _empirical_redraw(
    auto_class: str,
    mapping: dict[str, Counter],
    observed: list[str],
    rng: random.Random,
) -> str:
    pool = mapping.get(auto_class)
    if not pool:
        return auto_class
    population = list(pool.elements())
    return rng.choice(population) if population else auto_class


def _simulate(
    la: list[str],
    lb: list[str],
    q: float,
    model: str,
    mapping: dict[str, Counter],
    classes: list[str],
    sims: int,
    seed: int,
) -> dict[str, Any]:
    rng = random.Random(seed)
    p_values = []

    def perturb(label: str) -> str:
        if rng.random() >= q:
            return label
        if model == "empirical":
            return _empirical_redraw(label, mapping, classes, rng)
        return rng.choice(classes)

    for _ in range(sims):
        a = [perturb(x) for x in la]
        b = [perturb(x) for x in lb]
        result = stuart_maxwell(a, b)
        p = result.get("p_value")
        p_values.append(p if p is not None else 1.0)
    p_values.sort()
    return {
        "q": q,
        "model": model,
        "sims": sims,
        "survival_p05": sum(1 for p in p_values if p < 0.05) / len(p_values),
        "median_p": p_values[len(p_values) // 2],
        "p90": p_values[int(0.9 * len(p_values))],
    }


def audit(
    key: dict[str, dict[str, str]],
    labels: dict[str, dict[str, dict[str, str]]],
    fingerprint: dict[str, dict[str, Any]],
    *,
    bootstrap_repeats: int = 2000,
    sims: int = 300,
    seed: int = 42,
) -> dict[str, Any]:
    names = list(labels)
    rows = sorted(key)
    valid = [(rid, _label(labels[names[0]].get(rid)), _label(labels[names[1]].get(rid)))
             for rid in rows]
    valid = [(rid, a, b) for rid, a, b in valid if a in VALID and b in VALID]
    human_a = [a for _, a, _ in valid]
    human_b = [b for _, _, b in valid]
    auto = [_auto(key[rid]) or "uncertain" for rid, _, _ in valid]
    consensus_rows = [(h, au) for h, x, au in zip(human_a, human_b, auto) if h == x]

    classes = [c for c in CLASSES if c in set(human_a) | set(human_b) | set(auto) or c == "none"]

    result: dict[str, Any] = {
        "n_rows": len(rows),
        "n_valid": len(valid),
        "human_human": {
            "n": len(human_a),
            "agreement": sum(1 for a, b in zip(human_a, human_b) if a == b) / len(human_a),
            "kappa_multi": kappa_multi(human_a, human_b),
            "confusion": _confusion(human_a, human_b),
        },
        "auto_vs_human": {},
        "consensus": None,
        "pilot_system_distributions": {},
        "fingerprint_sensitivity": {},
    }
    for name, human in ((names[0], human_a), (names[1], human_b)):
        result["auto_vs_human"][name] = _metrics_block(
            human, auto, classes, bootstrap_repeats, seed)
    if consensus_rows:
        result["consensus"] = _metrics_block(
            [h for h, _ in consensus_rows],
            [a for _, a in consensus_rows],
            classes, bootstrap_repeats, seed,
        )

    # Per-system distributions on the pilot rows (auto vs each annotator).
    by_system: dict[str, dict[str, list[str]]] = defaultdict(lambda: {"auto": [], "a": [], "b": []})
    for rid, a, b in valid:
        system = key[rid].get("system") or "unknown"
        by_system[system]["auto"].append(_auto(key[rid]) or "uncertain")
        by_system[system]["a"].append(a)
        by_system[system]["b"].append(b)
    for system, data in by_system.items():
        result["pilot_system_distributions"][system] = {
            labeler: _dist(values) for labeler, values in data.items()
        }

    # Monte-Carlo misclassification sensitivity on the full fingerprint.
    systems = sorted({s for row in fingerprint.values() for s in (row.get("modes") or {})})
    mapping: dict[str, Counter] = defaultdict(Counter)
    for rid, a, b in valid:
        auto_class = _auto(key[rid])
        if auto_class in PILOT_TO_FULL:
            mapping[auto_class][a] += 1
            mapping[auto_class][b] += 1
    result["conditional_human_given_auto"] = {
        auto_class: dict(counts) for auto_class, counts in sorted(mapping.items())
    }
    observed = sorted({label for counts in mapping.values() for label in counts})
    for i, system_a in enumerate(systems):
        for system_b in systems[i + 1:]:
            la_full = _labels_for(fingerprint, system_a)
            lb_full = _labels_for(fingerprint, system_b)
            baseline = stuart_maxwell(la_full, lb_full)
            la = _to_pilot(la_full)
            lb = _to_pilot(lb_full)
            pair_classes = observed or sorted(set(la) | set(lb))
            baseline_pilot = stuart_maxwell(la, lb)
            pair_key = f"{system_a}_vs_{system_b}"
            entry: dict[str, Any] = {
                "n": len(la),
                "baseline_p_full_labels": baseline.get("p_value"),
                "baseline_chi2_full_labels": baseline.get("chi2"),
                "baseline_df_full_labels": baseline.get("df"),
                "baseline_p_pilot_taxonomy": baseline_pilot.get("p_value"),
                "simulations": [],
            }
            for model in ("empirical", "uniform"):
                for q in (0.1, 0.2, 0.3, 0.5):
                    entry["simulations"].append(
                        _simulate(la, lb, q, model, mapping, pair_classes, sims, seed)
                    )
            result["fingerprint_sensitivity"][pair_key] = entry
    return result


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--key", required=True)
    parser.add_argument("--labels", action="append", required=True,
                        help="name=sheet.csv (repeatable, exactly two)")
    parser.add_argument("--fingerprint", required=True)
    parser.add_argument("--out", default=None)
    parser.add_argument("--bootstrap-repeats", type=int, default=2000)
    parser.add_argument("--sims", type=int, default=300)
    args = parser.parse_args()

    key = _load(Path(args.key))
    labels = {}
    for spec in args.labels:
        name, path = spec.split("=", 1)
        labels[name] = _load(Path(path))
    if len(labels) != 2:
        raise SystemExit("exactly two --labels sheets are required")
    fingerprint = _load_fingerprint(Path(args.fingerprint))
    result = audit(
        key, labels, fingerprint,
        bootstrap_repeats=args.bootstrap_repeats,
        sims=args.sims,
    )
    text = json.dumps(result, ensure_ascii=False, indent=2)
    if args.out:
        Path(args.out).write_text(text, encoding="utf-8")
    print(text)


if __name__ == "__main__":
    main()
