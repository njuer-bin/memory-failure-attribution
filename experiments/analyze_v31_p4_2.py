"""V3.1 P4.2 run — stratified tables and paired contrasts.

Reads the frozen v3.1 records, writes per-model tables (all / over-commitment /
over-commitment excluding the six action-completed distortions / authorized
controls), paired contrasts against `present`, and the request-form interaction.

Usage:
    G:/aconda/python.exe -m experiments.analyze_v31_p4_2
"""

from __future__ import annotations

import argparse
import csv
import json
from pathlib import Path

from experiments.v3_p4_2_v3_runner import (
    DECISIONS,
    MEMORY_VARIANTS,
    REQUEST_CONDITIONS,
    bootstrap_ci,
    contrast,
    index_records,
    interaction,
    rate,
)

ACTION_COMPLETED_DISTORTIONS = {
    "MON-04", "HEA-01", "HEA-04", "HEA-06", "AUT-02", "COM-05",
}
OUTCOMES = ("unauthorized_execute", "unsupported_execute", "evidence_consistent",
            "under_action", "false_refusal", "authorized_execute",
            "gold_authorized_execute", "conditional_collapse")


def load_records(path: Path) -> list[dict]:
    return [json.loads(line) for line in path.open(encoding="utf-8") if line.strip()]


def cell(group: list[dict]) -> dict:
    return {
        "n": len(group),
        "decisions": {d: sum(1 for r in group if r["decision"] == d) for d in DECISIONS},
        **{o: rate([r[o] for r in group]) for o in OUTCOMES},
    }


def table(records: list[dict], ids: set[str]) -> dict:
    table_out = {}
    for request_condition in REQUEST_CONDITIONS:
        table_out[request_condition] = {}
        for variant in MEMORY_VARIANTS:
            group = [r for r in records
                     if r["scenario_id"] in ids
                     and r["request_condition"] == request_condition
                     and r["variant"] == variant]
            table_out[request_condition][variant] = cell(group)
    return table_out


def strata(records: list[dict]) -> dict[str, set[str]]:
    over = {r["scenario_id"] for r in records if r["control_type"] == "over_commitment"}
    control = {r["scenario_id"] for r in records
               if r["control_type"] == "authorized_execution"}
    return {
        "all_over_commitment": over,
        "over_commitment_excluding_action_completed": over - ACTION_COMPLETED_DISTORTIONS,
        "action_completed_distortion_subset": over & ACTION_COMPLETED_DISTORTIONS,
        "authorized_controls": control,
    }


def contrasts(records: list[dict], sets: dict[str, set[str]]) -> list[dict]:
    index = index_records(records)
    out = []
    for label, ids in sets.items():
        for request_condition in REQUEST_CONDITIONS:
            for condition in ("omitted", "distorted", "no_memory"):
                for outcome in OUTCOMES:
                    entry = contrast(index, sorted(ids), condition, "present",
                                     outcome, request_condition)
                    if entry:
                        entry["subset"] = label
                        out.append(entry)
    return out


def interactions(records: list[dict], sets: dict[str, set[str]]) -> list[dict]:
    index = index_records(records)
    out = []
    for label, ids in sets.items():
        for condition in ("omitted", "distorted", "no_memory"):
            for outcome in ("unauthorized_execute", "unsupported_execute",
                            "evidence_consistent", "under_action",
                            "authorized_execute", "gold_authorized_execute"):
                entry = interaction(index, sorted(ids), condition, outcome)
                if entry:
                    entry["subset"] = label
                    out.append(entry)
    return out


def write_csv(path: Path, rows: list[dict], fields: list[str]) -> None:
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields)
        writer.writeheader()
        for row in rows:
            writer.writerow({field: row.get(field) for field in fields})


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--records-dir", type=Path,
                        default=Path("results/status_drift_v3_p4_2_v3_v31/run"))
    parser.add_argument("--out-dir", type=Path,
                        default=Path("results/status_drift_v3_p4_2_v3_v31/analysis"))
    parser.add_argument("--models", nargs="+", default=["qwen2.5:7b", "gemma3:12b"])
    args = parser.parse_args()
    args.out_dir.mkdir(parents=True, exist_ok=True)

    slug = lambda model: model.replace(":", "_").replace(".", "_")
    summary = {}
    table_rows = []
    contrast_rows = []
    interaction_rows = []

    for model in args.models:
        records = load_records(args.records_dir / f"records_{slug(model)}.jsonl")
        sets = strata(records)
        model_tables = {label: table(records, ids) for label, ids in sets.items()}
        model_contrasts = contrasts(records, sets)
        model_interactions = interactions(records, sets)
        summary[model] = {
            "n_records": len(records),
            "parse_rate": rate([r["parse_ok"] for r in records])["rate"],
            "tables": model_tables,
            "contrasts": model_contrasts,
            "interactions": model_interactions,
        }
        for label, table_out in model_tables.items():
            for request_condition, variants in table_out.items():
                for variant, values in variants.items():
                    table_rows.append({
                        "model": model, "subset": label,
                        "request_condition": request_condition, "variant": variant,
                        "n": values["n"],
                        **{f"decision_{d}": values["decisions"][d] for d in DECISIONS},
                        **{o: values[o]["count"] for o in OUTCOMES},
                        **{f"{o}_rate": values[o]["rate"] for o in OUTCOMES},
                    })
        contrast_rows.extend({"model": model, **entry} for entry in model_contrasts)
        interaction_rows.extend({"model": model, **entry} for entry in model_interactions)

    (args.out_dir / "p4_2_v31_summary.json").write_text(
        json.dumps(summary, ensure_ascii=False, indent=2), encoding="utf-8")
    write_csv(args.out_dir / "condition_table.csv", table_rows,
              ["model", "subset", "request_condition", "variant", "n",
               *[f"decision_{d}" for d in DECISIONS],
               *OUTCOMES, *[f"{o}_rate" for o in OUTCOMES]])
    write_csv(args.out_dir / "paired_contrasts.csv", contrast_rows,
              ["model", "subset", "request_condition", "condition", "reference",
               "outcome", "n_pairs", "mean_difference", "bootstrap_low",
               "bootstrap_high"])
    write_csv(args.out_dir / "request_form_interactions.csv", interaction_rows,
              ["model", "subset", "condition", "outcome", "n_pairs",
               "mean_difference", "bootstrap_low", "bootstrap_high"])
    print(f"wrote {args.out_dir}")


if __name__ == "__main__":
    main()
