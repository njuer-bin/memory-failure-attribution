"""Build the canonical results layer used by both manuscript builds.

Every canonical artifact records the source files, their SHA-256 hashes, and
the analysis status. Manuscript tables and figures should be regenerated from
these files rather than hand-edited.

Usage:
    python -m experiments.build_canonical_results
"""

from __future__ import annotations

import csv
import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / "results" / "canonical"


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def read_json(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))


def read_csv(path: Path) -> list[dict]:
    with open(path, encoding="utf-8-sig", newline="") as handle:
        return list(csv.DictReader(handle))


def artifact(relative: str, status: str = "audited") -> dict:
    path = ROOT / relative
    entry = {"path": relative, "sha256": sha256(path), "status": status}
    if path.suffix == ".json":
        entry["data"] = read_json(path)
    elif path.suffix == ".csv":
        entry["data"] = read_csv(path)
    return entry


def write(name: str, payload: dict) -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    (OUT / name).write_text(
        json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")


def build() -> None:
    generated = datetime.now(timezone.utc).isoformat()
    p3 = OUT / "p3_results.json"
    p4 = OUT / "p4_results.json"
    p4_2 = OUT / "p4_2_controls.json"
    p5 = OUT / "p5_results.json"
    n30 = OUT / "replication_n30.json"
    reliability = OUT / "annotation_reliability.json"
    reasons = OUT / "reason_code_audit.json"

    write("p3_results.json", {
        "status": "audited",
        "generated_at": generated,
        "sources": [
            artifact("results/status_drift_v3_p2/analysis/condition_table.csv"),
            artifact("results/status_drift_v3_p2/analysis/p3_summary.json"),
            artifact("results/status_drift_v3_p2/analysis/paired_contrasts.csv"),
        ],
    })
    write("p4_results.json", {
        "status": "audited",
        "generated_at": generated,
        "sources": [artifact("results/status_drift_v3_p4/summary.json")],
    })

    control_audit = read_json(
        ROOT / "results/status_drift_v3_p4_2/analysis/control_audit.json")
    gate = {}
    for model, per_request in control_audit["models"].items():
        gate[model] = {
            form: {
                "strict_semantic": values["strict_19_semantic"],
                "strict_mechanical": values["strict_19_mechanical"],
                "inclusive_semantic": values["inclusive_20_semantic"],
            }
            for form, values in per_request.items()
        }
    write("p4_2_controls.json", {
        "status": "audited",
        "generated_at": generated,
        "gate_rule": control_audit["rule"],
        "strict_set": control_audit["controls"]["strict"],
        "inclusive_set": control_audit["controls"]["all"],
        "gate": gate,
        "sources": [
            artifact("results/status_drift_v3_p4_2/analysis/control_audit.json"),
            artifact("results/status_drift_v3_p4_2_v3_v31/run/summary.json"),
            artifact("results/status_drift_v3_p4_2_v3_v31_api/run/summary.json"),
        ],
    })

    write("p5_results.json", {
        "status": "audited",
        "generated_at": generated,
        "sources": [
            artifact("results/status_drift_v3_p5/analysis_v324/condition_table.csv"),
            artifact("results/status_drift_v3_p5/analysis_v324/paired_contrasts.csv"),
            artifact("results/status_drift_v3_p5/analysis_v324/p5_confirmatory_human_summary.json"),
        ],
    })

    write("replication_n30.json", {
        "status": "audited",
        "generated_at": generated,
        "pre_registered_cohort": "n12",
        "post_hoc_cohort": "n18",
        "sources": [
            artifact("results/status_drift_v3_replication_writer/analysis_v325_full/condition_table.csv"),
            artifact("results/status_drift_v3_replication_writer/analysis_v325_full/summary.json"),
            artifact("results/status_drift_v3_replication_writer/analysis_v325_full/reconciliation.json"),
            artifact("results/status_drift_v3_replication_writer/analysis_v325_full/reliability_by_cohort.json"),
        ],
    })
    write("annotation_reliability.json", {
        "status": "audited",
        "generated_at": generated,
        "cohorts": read_json(
            ROOT / "results/status_drift_v3_replication_writer/analysis_v325_full/reliability_by_cohort.json"),
        "note": "Pre-adjudication paired A/B agreement; n18 is the post-hoc added cohort.",
    })

    write("reason_code_audit.json", {
        "status": "exploratory",
        "generated_at": generated,
        "provenance_record": "docs/research/2026-11-20-reason-code-provenance.md",
        "sources": [
            artifact("results/status_drift_v3_p4_2_v3_v31/analysis/unauthorized_reason_codes_summary.json"),
            artifact("results/status_drift_v3_p4_2_v3_v31/analysis/unauthorized_reason_codes.csv"),
        ],
        "second_rater": {
            "independent_human_rating": False,
            "provenance": "unrecorded",
        },
        "gateway_records": {"n": 65, "second_rater": False,
                            "provenance": "not recorded"},
    })

    figures = sorted((ROOT / "paper" / "figures").glob("*.pdf"))
    write("figures_manifest.json", {
        "status": "audited",
        "generated_at": generated,
        "figures": [{"path": str(path.relative_to(ROOT)),
                     "sha256": sha256(path)} for path in figures],
    })

    releases = [
        "paper/submission_ecai/main.pdf",
        "paper/submission_ecai/appendix.pdf",
        "paper/submission/main.pdf",
        "paper/supplementary.zip",
    ]
    write("release_manifest.json", {
        "status": "frozen",
        "generated_at": generated,
        "releases": [{"path": path, "sha256": sha256(ROOT / path)}
                     for path in releases],
    })

    canonical = sorted(OUT.glob("*.json"))
    write("experiment_manifest.json", {
        "status": "frozen",
        "generated_at": generated,
        "artifacts": [{"file": path.name, "sha256": sha256(path),
                       "status": read_json(path).get("status")}
                      for path in canonical if path.name != "experiment_manifest.json"],
    })
    print(f"canonical results: {len(canonical)} files in {OUT}")


if __name__ == "__main__":
    build()
