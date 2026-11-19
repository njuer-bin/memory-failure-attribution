# Outstanding human-only tasks — 2026-11-19

Everything that can be done without a human is done: the P4.2 v3.1 factorial,
its analysis, the paper section, all six figures, the citation check, and the
claim audit. The items below need a person; none of them blocks starting the
LaTeX build, but two should be resolved or disclosed before submission.

## 1. Validate the 16 new authorized controls (highest priority)

The original 40 scenarios were validated by two humans (WMY, YTB). Sixteen
controls were added later for control precision and are only mechanically
checked.

- Scenarios: `MON-11..14`, `HEA-11..14`, `AUT-11..14`, `COM-11..14`
  (`datasets/p4_2_scenarios/p4_2_scenarios.yaml`).
- Use the same rubric as `check_p4_2_validation.py`: realism, status clarity,
  rule clarity, distortion plausibility, stake severity (1–5), and
  `only_status_differs` (yes/no).
- Also review `results/status_drift_v3_p4_2_v3_v31/request_check.csv` (54 rows):
  confirm each neutral/action pair keeps the action phrase and differs only in
  request form.
- Acceptance: pooled realism ≥ 3.5, `only_status_differs` yes-both ≥ 0.90.
  If a control fails, exclude it and recompute the control gate; 19/20 still
  gives a usable gate.

Until this is done the paper must keep the sentence "the 16 new controls are
mechanically checked but not two-human-validated".

## 2. Independent second rater for the reason coding

- Sheet: `results/status_drift_v3_p4_2_v3_v31/analysis/reason_sheet_blind.csv`
  (39 rows; no analyst code, no variant, shuffled).
- Codes: `D1_FOLLOWED_DISTORTED_MEMORY`, `O1_ASSERTED_UNSTATED_COMMITMENT`,
  `O2_MENTION_AS_COMMITMENT`, `O3_REQUEST_AS_AUTHORIZATION`.
- Report raw agreement and kappa against
  `analysis/unauthorized_reason_codes.csv` (`analyst_code` column). If a rater
  is not available, keep the current sentence: "analyst, post hoc,
  gold-unblinded".

## 2b. Annotate the remaining 18 writer-replication trajectories (CCF-B upgrade)

The blind sheets are generated and ready; this is now only a labeling task.

- Directory: `results/status_drift_v3_replication_writer/annotation_v325_remaining/`.
- 126 items (18 trajectories x 7 conditions), item ids `REPR-0085`–`REPR-0210`.
- Give `annotator_A.csv` to one person and `annotator_B.csv` to another. Do not
  give either of them `key.csv` (gold/condition), and do not use a model to
  draft labels.
- Protocol: `docs/research/V3_ANNOTATION_GUIDELINES.md` (v3.2.5); instructions
  in the directory's `README.md`.
- After labeling: run `experiments.check_v3_annotations`, adjudicate
  disagreements, and merge with `annotation_v325/adjudication.csv`. Report
  n = 12 (pre-registered, already in the paper) and n = 30 (post-hoc
  sensitivity) separately.
- Rebuilder: `experiments/make_replication_annotation_remaining.py`.

## 2c. Frontier API replication (blocked on credentials)

No API key is available in this environment, so the frontier arm cannot run
here. If a key is provided (OpenAI-, Anthropic-, or OpenAI-compatible endpoint),
the P4.2 probe is 20 controls x 2 forms x 4 variants = 160 calls per model; it
must pass the control gate before the full 864-call matrix. Do not use the
Claude Code session token for bulk experiment calls.

## 3. Build the 8-page PDF (needs Overleaf or a local TeX install)

There is no TeX distribution on this machine and installing one was blocked by
the permission policy. Structural checks pass (balanced environments, every
cross-reference and citation resolves), and the source is in
`paper/submission/main.tex`. Either:

- build on Overleaf using `paper/submission/README.md` (recommended; no local
  install), or
- authorize a portable TeX install (for example TinyTeX or MiKTeX) if the page
  count must be checked locally.

The body is estimated at 7-7.5 pages of the 8-page main body; this is not yet
verified.

## 4. Not needed under decision C

- No more real-dialogue annotation. The LSF/SSF calibration is reported as a
  negative result; the gold calibration passed after adjudication and is in
  Fig. 6.

## Where things stand

- Branch `research/path-dependent-state-distortion-v3`; commits are local and
  pushed when the network allows. Push from this machine failed earlier (local
  proxy 127.0.0.1:443 unreachable); the commits are local and ready.
- Audit log: `docs/research/2026-11-19-pre-submission-audit-log.md`.
- Run note: `docs/research/2026-11-19-v3-p4-2-v31-run.md`.
