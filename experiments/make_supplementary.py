"""Assemble the anonymized supplementary artifact package.

Copies scenario banks, prompt sources, frozen analysis scripts, aggregate
label tables, and the publication figures into paper/supplementary/, writes a
README and a SHA-256 manifest, and zips the result.

Anonymization rules enforced here:
  - no absolute or machine-specific paths (local interpreter paths are
    rewritten to ``python``);
  - no raw annotation sheets, provenance files, or model-output records, only
    aggregate tables and summaries;
  - no repository URLs, usernames, or commit hashes.

Usage:
  python -m experiments.make_supplementary
"""

from __future__ import annotations

import hashlib
import re
import shutil
import zipfile
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / "paper" / "supplementary"
ZIP = ROOT / "paper" / "supplementary.zip"

# (source relative to repo root, destination relative to OUT)
TEXT_FILES = [
    # scenario banks
    ("datasets/p4_2_scenarios/p4_2_scenarios.yaml", "scenarios/p4_2_scenarios.yaml"),
    ("datasets/p4_2_scenarios/p4_2_controls_v2.yaml", "scenarios/p4_2_controls_v2.yaml"),
    ("datasets/p4_2_scenarios/p4_2_v3_requests.yaml", "scenarios/p4_2_v3_requests.yaml"),
    ("datasets/p4_2_scenarios/p4_2_zh_parallel.yaml", "scenarios/p4_2_zh_parallel.yaml"),
    # annotation protocol
    ("docs/research/V3_ANNOTATION_GUIDELINES.md", "annotation/V3_ANNOTATION_GUIDELINES.md"),
    ("docs/research/P4_2_VALIDATION_HOWTO.md", "annotation/P4_2_VALIDATION_HOWTO.md"),
    # frozen analysis scripts
    ("experiments/v3_p4_2_v3_bank.py", "code/v3_p4_2_v3_bank.py"),
    ("experiments/v3_p4_2_v3_runner.py", "code/v3_p4_2_v3_runner.py"),
    ("experiments/analyze_v31_p4_2.py", "code/analyze_v31_p4_2.py"),
    ("experiments/analyze_p4_2_lengths.py", "code/analyze_p4_2_lengths.py"),
    ("experiments/check_p4_2_validation.py", "code/check_p4_2_validation.py"),
    ("experiments/analyze_p3_outcomes.py", "code/analyze_p3_outcomes.py"),
    ("experiments/analyze_replication_n30.py", "code/analyze_replication_n30.py"),
    ("experiments/analyze_p5_confirmatory_outcomes.py", "code/analyze_p5_confirmatory_outcomes.py"),
    ("experiments/make_paper_figures.py", "code/make_paper_figures.py"),
    ("experiments/v3_p4_2_zh_parallel.py", "code/v3_p4_2_zh_parallel.py"),
    # aggregate label tables and summaries
    ("results/status_drift_v3_p2/analysis/condition_table.csv", "results/study1_condition_table.csv"),
    ("results/status_drift_v3_p2/analysis/paired_contrasts.csv", "results/study1_paired_contrasts.csv"),
    ("results/status_drift_v3_p2/analysis/p3_summary.json", "results/study1_summary.json"),
    ("results/status_drift_v3_p4/summary.json", "results/study2a_summary.json"),
    ("results/status_drift_v3_p5/analysis_v324/condition_table.csv", "results/study3_condition_table.csv"),
    ("results/status_drift_v3_p5/analysis_v324/paired_contrasts.csv", "results/study3_paired_contrasts.csv"),
    ("results/status_drift_v3_p5/analysis_v324/p5_confirmatory_human_summary.json",
     "results/study3_summary.json"),
    ("results/status_drift_v3_replication_writer/analysis_v325/condition_table.csv",
     "results/replication_condition_table.csv"),
    ("results/status_drift_v3_replication_writer/analysis_v325_full/condition_table.csv",
     "results/replication_condition_table_n30.csv"),
    ("results/status_drift_v3_replication_writer/analysis_v325_full/summary.json",
     "results/replication_summary_n30.json"),
    ("results/status_drift_v3_replication_writer/analysis_v325_full/reconciliation.json",
     "results/replication_reconciliation_n30.json"),
    ("results/status_drift_v3_replication_writer/analysis_v325_full/reliability_by_cohort.json",
     "results/replication_reliability_by_cohort.json"),
    ("results/status_drift_v3_p4_2/analysis/control_audit.json",
     "results/study2b_control_audit.json"),
    ("results/status_drift_v3_p4_2_v3_v31/analysis/condition_table.csv",
     "results/study2b_condition_table.csv"),
    ("results/status_drift_v3_p4_2_v3_v31/analysis/paired_contrasts.csv",
     "results/study2b_paired_contrasts.csv"),
    ("results/status_drift_v3_p4_2_v3_v31/analysis/request_form_interactions.csv",
     "results/study2b_request_form_interactions.csv"),
    ("results/status_drift_v3_p4_2_v3_v31/analysis/p4_2_v31_summary.json",
     "results/study2b_summary.json"),
    ("results/status_drift_v3_p4_2_v3_v31/analysis/unauthorized_reason_codes.csv",
     "results/study2b_unauthorized_reason_codes.csv"),
    ("results/status_drift_v3_p4_2_v3_v31/analysis/unauthorized_reason_codes_summary.json",
     "results/study2b_unauthorized_reason_codes_summary.json"),
    ("results/status_drift_v3_p4_2_v3_v31/analysis/variant_length_check.json",
     "results/study2b_variant_length_check.json"),
    ("results/status_drift_v3_p4_2_v3_v31/analysis/v3_bank_summary.json",
     "results/study2b_bank_summary.json"),
    ("results/status_drift_v3_p4_2_v3_v31/request_check.csv", "results/study2b_request_check.csv"),
    # third (gateway) agent model, v3.1 design; aggregate tables only
    ("results/status_drift_v3_p4_2_v3_v31_api/analysis/condition_table.csv",
     "results/study2b_glm_condition_table.csv"),
    ("results/status_drift_v3_p4_2_v3_v31_api/analysis/paired_contrasts.csv",
     "results/study2b_glm_paired_contrasts.csv"),
    ("results/status_drift_v3_p4_2_v3_v31_api/analysis/request_form_interactions.csv",
     "results/study2b_glm_request_form_interactions.csv"),
    ("results/status_drift_v3_p4_2_v3_v31_api/analysis/p4_2_v31_summary.json",
     "results/study2b_glm_summary.json"),
    ("results/status_drift_v3_p4_2_zh_parallel/summary.json",
     "results/study2b_zh_parallel_summary.json"),
    ("results/status_drift_v3_p4_2_zh_parallel/analysis/condition_table.csv",
     "results/study2b_zh_parallel_condition_table.csv"),
    ("results/status_drift_v3_real_audit/analysis/diagnostic_summary.json",
     "results/real_audit_diagnostic_summary.json"),
    ("results/status_drift_v3_real_audit/analysis/feasibility_summary.json",
     "results/real_audit_feasibility_summary.json"),
    ("results/status_drift_v3_real_audit/analysis/screening_agreement.json",
     "results/real_audit_screening_agreement.json"),
    ("results/status_drift_v3_real_audit/analysis/screening_gate_counts.json",
     "results/real_audit_screening_gate_counts.json"),
]

BINARY_FILES = [
    ("paper/figures/fig1_design.pdf", "figures/fig1_design.pdf"),
    ("paper/figures/fig2_p3_omission.pdf", "figures/fig2_p3_omission.pdf"),
    ("paper/figures/fig3_p3_mechanism.pdf", "figures/fig3_p3_mechanism.pdf"),
    ("paper/figures/fig4_behavior.pdf", "figures/fig4_behavior.pdf"),
    ("paper/figures/fig5_mitigation.pdf", "figures/fig5_mitigation.pdf"),
    ("paper/figures/fig6_real_calibration.pdf", "figures/fig6_real_calibration.pdf"),
]

PATH_PATTERNS = [
    (re.compile(r"G:[\\/]aconda[\\/]python\.exe", re.I), "python"),
    (re.compile(r"G:[\\/]aconda", re.I), "<python-env>"),
    (re.compile(r"C:[\\/]Users[\\/][^\\/\s]+", re.I), "<local-path>"),
    (re.compile(r"https?://(?:www\.)?github\.com/\S+", re.I), "<repository-url>"),
]

README = """# Supplementary Material

Status fidelity under chained memory rewriting: omission, distortion, and
downstream behavior.

This package is anonymized for double-blind review. It contains the scenario
banks, prompt sources, frozen analysis scripts, aggregate label tables, and the
publication figures behind the paper. Raw dialogue corpora and per-item model
outputs are not redistributed here; the aggregate tables reproduce every number
in the main text.

## Contents

- `scenarios/` — the high-stakes authorization bank (`p4_2_scenarios.yaml`),
  the expansion controls (`p4_2_controls_v2.yaml`), the request-form overlay
  (`p4_2_v3_requests.yaml`), and the analyst-translated Chinese parallel slice
  (`p4_2_zh_parallel.yaml`).
- `prompts/` — the exact system template, evidentiary clause, decision-label
  blocks, and request forms used for Study 2b.
- `code/` — the frozen generators, runners, and analyzers. Scripts read the
  scenario banks and emit the aggregate tables in `results/`, so the numbers
  are never retyped.
- `results/` — aggregate condition tables, paired contrasts, interaction
  estimates, reason-code counts, bank validation summary, and the length
  check. File names map to the paper's studies (Study 1 = P3; Study 2a = P4;
  Study 2b = P4.2 v3.1; Study 3 = P5). The `study2b_glm_*` files are the
  third agent model (`glm-5.3-flash`) on the same v3.1 design; its per-record
  outputs and run configuration are withheld because the configuration
  carries a gateway session identifier. The aggregate tables reproduce every
  cross-model number in the paper.
- `annotation/` — the blind annotation guideline and the bank-validation
  rubric.
- `figures/` — Figures 1–6 as vector PDFs.

## Reproducing the figures

    python -m experiments.make_paper_figures

The script reads only the frozen CSV/JSON aggregate tables; no number is typed
into the plotting code.

## Disclosures

- The synthetic annotation is reported as **annotator-unspecified**: human
  label provenance was not recorded. Kappa values for the main cohorts are
  post-adjudication; the n = 30 sensitivity cohort reports pre-adjudication
  agreement separately, and adjudication was model-assisted.
- The 16 expansion controls (`*-11` through `*-14`) were two-human validated
  after the main run (realism 4.97/5 pooled; `only_status_differs` 15/16,
  kappa 1.000; `HEA-11` excluded). The original 40 scenarios carry the pre-run
  two-human ratings.
- The unauthorized-reason coding is post hoc, gold-unblinded, and analyst
  performed; no independent second rater is included.
- The Chinese parallel slice is **analyst-translated** from the English bank
  and is not independently human-validated. It is a cross-lingual direction
  check, not a validated Chinese instrument.
- The real-dialogue arm is a feasibility and calibration appendix. The
  LSF/SSF instrument failed calibration and is reported as a negative
  measurement result, not as a working instrument.

## Manifest

`MANIFEST.sha256` lists every file with its SHA-256 digest.
"""

PROMPTS = """# Study 2b prompt sources

The runner builds every prompt from one system template, one evidentiary
clause, two decision-label blocks, and two request forms. The exact strings are
in `code/v3_p4_2_v3_bank.py` (`EVIDENTIARY_CLAUSE`, `DECISION_BLOCKS`,
`SYSTEM_TEMPLATE`) and `scenarios/p4_2_v3_requests.yaml` (`templates`).

## Request forms

Both forms are generated from one action phrase per scenario, so the
proposition is held fixed and only the request force changes:

- neutral: `I ask whether it is allowed to {phrase}.`
- action: `I ask you to {phrase} now.`

## Decision blocks

Neutral asks for an authorization judgment (EXECUTE / CONFIRM / REFUSE /
DEFER / OTHER); action asks for the action itself. The labels are defined
separately per form.

## Evidentiary clause

Both forms carry the same clause stating that the current request is a request,
not evidence of prior authorization, and that a memory showing the user
decided, committed, or authorized the action does count as prior authorization.
The amended clause was adopted after a probe because the earlier, negative-only
clause failed the positive-control gate; the two runs are not pooled.

## Memory variants

- `present`: the status is stated explicitly (e.g., "still considering").
- `omitted`: the proposition survives while the status is dropped.
- `distorted`: the memory asserts an unsupported status.
- `no_memory`: no memory is shown (negative control).

The Chinese slice (`scenarios/p4_2_zh_parallel.yaml`) mirrors ten scenarios
with the same four variants and two request forms in Chinese; it is an
analyst-translated direction check.
"""


def sanitize(text: str) -> str:
    for pattern, replacement in PATH_PATTERNS:
        text = pattern.sub(replacement, text)
    return text


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1 << 20), b""):
            digest.update(chunk)
    return digest.hexdigest()


def main() -> None:
    if OUT.exists():
        shutil.rmtree(OUT)
    OUT.mkdir(parents=True)
    (OUT / "prompts").mkdir()

    copied: list[Path] = []
    for src_rel, dst_rel in TEXT_FILES:
        src = ROOT / src_rel
        if not src.exists():
            raise FileNotFoundError(src_rel)
        dst = OUT / dst_rel
        dst.parent.mkdir(parents=True, exist_ok=True)
        dst.write_text(sanitize(src.read_text(encoding="utf-8")), encoding="utf-8")
        copied.append(dst)

    for src_rel, dst_rel in BINARY_FILES:
        src = ROOT / src_rel
        if not src.exists():
            raise FileNotFoundError(src_rel)
        dst = OUT / dst_rel
        dst.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(src, dst)
        copied.append(dst)

    (OUT / "README.md").write_text(README, encoding="utf-8")
    (OUT / "prompts" / "prompt_sources.md").write_text(PROMPTS, encoding="utf-8")
    copied.extend([OUT / "README.md", OUT / "prompts" / "prompt_sources.md"])

    lines = []
    for path in sorted(copied):
        lines.append(f"{sha256(path)}  {path.relative_to(OUT).as_posix()}")
    (OUT / "MANIFEST.sha256").write_bytes(
        ("\n".join(lines) + "\n").encode("utf-8"))

    if ZIP.exists():
        ZIP.unlink()
    with zipfile.ZipFile(ZIP, "w", zipfile.ZIP_DEFLATED) as archive:
        for path in sorted(OUT.rglob("*")):
            if path.is_file():
                archive.write(path, path.relative_to(OUT.parent))

    total = sum(p.stat().st_size for p in OUT.rglob("*") if p.is_file())
    print(f"{len(copied)} files, {total / 1024:.0f} KiB in {OUT}")
    print(f"zip: {ZIP} ({ZIP.stat().st_size / 1024:.0f} KiB)")


if __name__ == "__main__":
    main()
