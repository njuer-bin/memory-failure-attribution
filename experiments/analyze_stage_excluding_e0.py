"""Stage-distribution tests with E0 questions excluded.

E0 is the gate's noisiest category (human audit: kappa 0.07). This script reruns
the paired stage-distribution tests on questions whose shared gate is
``sufficient``, and reports the E0-included version side by side. Label-only;
no model calls.

Usage:
    python -m experiments.analyze_stage_excluding_e0 \
        --comparison results/systems_locomo_n200_fixedgate/comparison.jsonl \
        --out results/analysis_stage_excluding_e0_locomo_n100.json
"""
from __future__ import annotations

import argparse
import json
from collections import Counter
from pathlib import Path
from typing import Any

from evaluation.stage_distribution_tests import stage_distribution_test
from experiments.analyze_ladder import _holm


def _load(path: Path) -> list[dict[str, Any]]:
    return [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines() if line.strip()]


def _labels(rows: list[dict[str, Any]], mode: str) -> list[str]:
    return [str((row["modes"][mode].get("answer_failure_type")) or "none") for row in rows]


def _gate_status(row: dict[str, Any]) -> str:
    for mode_data in (row.get("modes") or {}).values():
        return str(((mode_data.get("evidence_sufficiency") or {}).get("status")) or "unknown")
    return "unknown"


def _tests(rows: list[dict[str, Any]], modes: list[str]) -> dict[str, Any]:
    out = {}
    raw: dict[str, float] = {}
    for i, a in enumerate(modes):
        for b in modes[i + 1:]:
            test = stage_distribution_test(_labels(rows, a), _labels(rows, b))
            out[f"{a}_vs_{b}"] = test
            p = test.get("stuart_maxwell", {}).get("p_value")
            if p is not None:
                raw[f"{a}_vs_{b}"] = p
    if raw:
        holm = _holm(raw)
        for pair, value in holm.items():
            out[pair]["stuart_maxwell_holm"] = value
        out["_holm"] = holm
    return out


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--comparison", required=True)
    parser.add_argument("--out", required=True)
    parser.add_argument("--modes", default=None)
    parser.add_argument("--keep-status", default="sufficient")
    args = parser.parse_args()
    rows = _load(Path(args.comparison))
    modes = ([m.strip() for m in args.modes.split(",")] if args.modes
             else sorted({m for row in rows for m in (row.get("modes") or {})}))
    kept = [row for row in rows if _gate_status(row) == args.keep_status]
    excluded = len(rows) - len(kept)
    result = {
        "comparison": args.comparison,
        "rows_total": len(rows),
        "rows_used": len(kept),
        "rows_excluded": excluded,
        "excluded_by_gate": dict(Counter(_gate_status(row) for row in rows)),
        "modes": modes,
        "e0_excluded": _tests(kept, modes),
        "e0_included_sensitivity": _tests(rows, modes),
        "label_distribution_used": {
            mode: dict(sorted(Counter(_labels(kept, mode)).items())) for mode in modes
        },
    }
    Path(args.out).write_text(json.dumps(result, ensure_ascii=False, indent=2), encoding="utf-8")
    print(json.dumps({k: result[k] for k in ("rows_total", "rows_used", "excluded_by_gate")}, ensure_ascii=False, indent=2))
    for section in ("e0_excluded", "e0_included_sensitivity"):
        print(f"\n{section}:")
        for pair, test in result[section].items():
            if pair.startswith("_"):
                continue
            sm = test["stuart_maxwell"]
            print(f"  {pair}: chi2={sm['chi2']} df={sm['df']} p={sm['p_value']} holm={test.get('stuart_maxwell_holm')}")


if __name__ == "__main__":
    main()
