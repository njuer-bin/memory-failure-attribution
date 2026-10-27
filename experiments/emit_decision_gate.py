"""Emit a decision-gate artifact from the ablation analyses (no model calls).

The pre-registered criteria are copied verbatim from
docs/research/2026-10-26-architecture-ablation-design.md so a later reader can
see that the bar was not moved after the result.

Usage:
    python -m experiments.emit_decision_gate --stage B \
        --out results/decision_gate_b.json
"""
from __future__ import annotations

import argparse
import json
from datetime import datetime, timezone
from pathlib import Path

# Verbatim from docs/research/2026-10-26-architecture-ablation-design.md
PREREGISTERED_B = {
    "pass_condition": (
        "The fingerprint is architecture-conditional if, for at least two of "
        "the three systems, turning off its bottleneck: (1) changes that "
        "system's dominant-stage share by >= 20 percentage points (e.g. "
        "semantic F1 share falls by >= 0.20), and (2) the within-system "
        "Stuart-Maxwell p < 0.05 survives Holm across the three tests."
    ),
    "fail_condition": (
        "The fingerprint is architecture-independent if all three knobs leave "
        "the dominant-stage share within +-10 points and no within-system test "
        "is significant."
    ),
    "between": (
        "Anything between is reported as partial and the claim is narrowed to "
        "the systems/conditions where the stage moved."
    ),
    "share_bar_points": 20.0,
    "alpha": 0.05,
}

CONDITIONS = {
    "A1": {
        "system": "semantic",
        "knob": "raw-write verbatim storage (removes the fact-extraction bottleneck)",
        "analysis": "results/analysis_ablation_a1_n100.json",
        "pair": "semantic_vs_semantic_rawwrite",
        "attention_stages": ("F1_FORMATION", "F4_RETRIEVAL"),
    },
    "A3": {
        "system": "verbatim",
        "knob": "hybrid ranking (0.5 cosine + 0.5 question-token overlap)",
        "analysis": "results/analysis_ablation_a3_n100.json",
        "pair": "verbatim_vs_verbatim_hybrid",
        "attention_stages": ("F4_RETRIEVAL",),
    },
}


def _share(failures: dict[str, int], label: str, n: int) -> float:
    return round(failures.get(label, 0) / n, 4)


def _evaluate(cond: dict, data: dict) -> dict:
    systems = data["systems"]
    a, b = cond["pair"].split("_vs_")
    n = data["rows"]
    stages = set(cond["attention_stages"]) | {
        max(systems[a]["failure_distribution"], key=systems[a]["failure_distribution"].get),
        max(systems[b]["failure_distribution"], key=systems[b]["failure_distribution"].get),
    }
    stages.discard("none")
    stages.discard("E0_EVIDENCE_INSUFFICIENT")
    shares = {}
    for label in sorted(stages):
        sa = _share(systems[a]["failure_distribution"], label, n)
        sb = _share(systems[b]["failure_distribution"], label, n)
        shares[label] = {"baseline": sa, "knob_on": sb, "move_points": round(abs(sb - sa) * 100, 1)}
    moved = max(shares.values(), key=lambda v: v["move_points"])["move_points"]

    tests = data["stage_distribution_tests"][cond["pair"]]
    sm = tests["stuart_maxwell"]
    holm = data["stage_distribution_holm"][cond["pair"]]
    acc = data["paired_accuracy"][cond["pair"]]

    crit1 = moved >= PREREGISTERED_B["share_bar_points"]
    crit2 = holm < PREREGISTERED_B["alpha"]
    return {
        "system": cond["system"],
        "knob": cond["knob"],
        "analysis": cond["analysis"],
        "pair": cond["pair"],
        "shares": shares,
        "largest_move_points": moved,
        "stuart_maxwell": {"chi2": round(sm["chi2"], 3), "df": sm["df"],
                           "p": sm["p_value"], "holm": holm},
        "permutation_p": tests.get("permutation", {}).get("p_value"),
        "criterion_1_share_20pts": crit1,
        "criterion_2_holm_significant": crit2,
        "condition_pass": crit1 and crit2,
        "paired_accuracy": {
            "baseline": systems[a]["semantic_accuracy"],
            "knob_on": systems[b]["semantic_accuracy"],
            "mcnemar_p": acc["mcnemar"]["p_value"],
            "bootstrap_diff": acc["bootstrap"]["diff"],
            "bootstrap_ci": [acc["bootstrap"]["ci_low"], acc["bootstrap"]["ci_high"]],
        },
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--stage", default="B")
    parser.add_argument("--out", default="results/decision_gate_b.json")
    args = parser.parse_args()

    results = {}
    for name, cond in CONDITIONS.items():
        path = Path(cond["analysis"])
        if not path.exists():
            results[name] = {"status": "missing", "analysis": cond["analysis"]}
            continue
        results[name] = _evaluate(cond, json.loads(path.read_text(encoding="utf-8")))

    passed = [k for k, v in results.items() if v.get("condition_pass")]
    evaluated = [k for k, v in results.items() if "condition_pass" in v]
    if len(passed) >= 2:
        verdict = "pass"
    elif not evaluated:
        verdict = "undetermined"
    else:
        verdict = "partial"

    gate = {
        "stage": args.stage,
        "generated_utc": datetime.now(timezone.utc).isoformat(),
        "preregistered_criteria": PREREGISTERED_B,
        "preregistration_sources": [
            "docs/research/2026-10-26-architecture-ablation-design.md",
            "docs/CCF_B_DECISION_PLAN_2026-10-26.md",
        ],
        "conditions": results,
        "conditions_passed": passed,
        "conditions_evaluated": evaluated,
        "verdict": verdict,
        "note": (
            "A2 (summary raw-context) is deferred; the smoke showed its stage "
            "does not move because context assembly, not summary lossiness, "
            "binds. With two evaluated conditions at most one can pass, so the "
            "pre-registered 'at least two of three' rule cannot be satisfied "
            "until A2 or A4 runs."
        ),
    }
    Path(args.out).write_text(json.dumps(gate, indent=2, ensure_ascii=False) + "\n",
                              encoding="utf-8")
    print(json.dumps({k: gate[k] for k in ("verdict", "conditions_passed",
                                           "conditions_evaluated")}, indent=2))
    for name, r in results.items():
        if "condition_pass" in r:
            print(f"{name}: largest move {r['largest_move_points']} pts, "
                  f"SM p={r['stuart_maxwell']['p']:.4g} (Holm {r['stuart_maxwell']['holm']:.4g}), "
                  f"pass={r['condition_pass']}")


if __name__ == "__main__":
    main()
