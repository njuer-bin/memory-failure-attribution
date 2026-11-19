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

## 3. Optional, only if there is time

- **Chinese parallel subset.** Ten scenarios translated and re-run under the
  same factorial, to rule out an English-prompt artifact. Needs its own
  mechanical checks; do not merge it into the 54-scenario matrix.
- **Frontier API model.** Must pass the same 20-control × 2-form probe before a
  full matrix. The local probe showed `mistral:7b` fails the action gate
  (9/20), so a small local model is not a shortcut.

## 4. Not needed under decision C

- No more real-dialogue annotation. The LSF/SSF calibration is reported as a
  negative result; the gold calibration passed after adjudication and is in
  Fig. 6.

## Where things stand

- Branch `research/path-dependent-state-distortion-v3`, commits through
  `f85e927`. Push is blocked from this machine (local proxy 127.0.0.1:443 is
  unreachable); the commits are local and ready to push.
- Audit log: `docs/research/2026-11-19-pre-submission-audit-log.md`.
- Run note: `docs/research/2026-11-19-v3-p4-2-v31-run.md`.
