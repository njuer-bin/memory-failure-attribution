"""Check that canonical results and both manuscripts agree.

Presence is checked for every canonical value that the manuscripts are expected
to report, and a small blacklist catches wording that the v2.1 audit replaced.
The check is advisory: a missing value means the manuscript source may have
drifted from the canonical layer, not that the canonical layer is wrong.

Usage:
    python -m experiments.check_canonical_consistency
"""

from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
CANON = ROOT / "results" / "canonical"
MANUSCRIPTS = [
    "paper/submission_ecai/main.tex",
    "paper/submission_ecai/appendix.tex",
    "paper/submission/main.tex",
]
BLACKLIST = [
    "All reported $\\kappa$ values are post-adjudication",
    "On the 20 authorized controls, present executes 20/20",
    "the 20 authorized controls are not shown here",
    "one expansion scenario was excluded because its distorted variant",
]


def read(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def main() -> int:
    texts = {path: read(ROOT / path) for path in MANUSCRIPTS}
    combined = "\n".join(texts.values())

    controls = json.loads((CANON / "p4_2_controls.json").read_text(encoding="utf-8"))
    reliability = json.loads((CANON / "annotation_reliability.json").read_text(encoding="utf-8"))
    n30 = json.loads((CANON / "replication_n30.json").read_text(encoding="utf-8"))

    expected = []
    for model, per_request in controls["gate"].items():
        for form, values in per_request.items():
            strict = values["strict_semantic"]
            inclusive = values["inclusive_semantic"]
            expected.append({
                "claim": f"{model} {form} strict semantic",
                "value": f"{strict['count']}/{strict['denominator']}",
            })
            expected.append({
                "claim": f"{model} {form} inclusive semantic",
                "value": f"{inclusive['count']}/{inclusive['denominator']}",
            })
    for cohort in ("n12_pre_registered", "n18_post_hoc", "full_210"):
        entry = reliability["cohorts"][cohort]
        expected.append({"claim": f"{cohort} raw agreement",
                         "value": f"{entry['raw_agreement']:.3f}"})
        kappa = entry["cohen_kappa"]
        expected.append({"claim": f"{cohort} kappa",
                         "value": "0.000" if kappa is None else f"{kappa:.3f}"})

    n30_source = n30["sources"][0]["data"]
    for row in n30_source:
        if row["condition"] in ("direct", "rewrite_matched"):
            expected.append({"claim": f"n30 {row['condition']} faithful",
                             "value": f"{int(row['faithful_n'])}/{int(row['n'])}"})

    expected.extend([
        {"claim": "call accounting local attempts", "value": "864"},
        {"claim": "call accounting gateway attempts", "value": "432"},
        {"claim": "gateway parse successes", "value": "429"},
    ])

    report = {"missing": [], "blacklisted": [], "checked_values": len(expected)}
    for item in expected:
        if item["value"] not in combined:
            report["missing"].append(item)
    for phrase in BLACKLIST:
        if phrase in combined:
            report["blacklisted"].append(phrase)

    report["ok"] = not report["missing"] and not report["blacklisted"]
    out = CANON / "consistency_report.json"
    out.write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")
    print(json.dumps(report, ensure_ascii=False, indent=2))
    return 0 if report["ok"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
