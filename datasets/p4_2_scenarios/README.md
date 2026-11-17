# P4.2 Scenario Bank

40 curated high-stakes scenarios for the status-only behavioral intervention.
English, sandboxed, four domains (money, health, authorization, commitments).

## Files

- `p4_2_scenarios.yaml` — the bank.
- `../experiments/v3_p4_2_bank.py` — validator/generator.
- `../../results/status_drift_v3_p4_2/items.jsonl` — runnable items (one row per
  scenario x variant).
- `../../results/status_drift_v3_p4_2/validation.csv` — internal validation
  sheet with expected decisions and manipulation diagnostics (do not give this
  to annotators).
- `../../results/status_drift_v3_p4_2/validation_A.csv` /
  `validation_B.csv` — blinded two-annotator sheets (no expected labels).
- `../../docs/research/P4_2_VALIDATION_HOWTO.md` — how to fill them.
- `../../results/status_drift_v3_p4_2/analysis/bank_summary.json` — automated
  counts and manipulation flags.

## Schema

```yaml
- id: MON-01
  domain: money                 # money | health | authorization | commitments
  title: ...
  role: ...                     # assistant role used in the prompt
  control_type: over_commitment # over_commitment | authorized_execution
  evidence: >-                  # original user evidence, identical across variants
  target: ...                   # the proposition P
  gold:                         # intentional or conditional state
    dimension: intentional
    status: CONSIDERING
    strength: moderate
  rule: ...                     # authorization rule, identical across variants
  request: ...                  # downstream request, identical across variants
  variants:
    present: ...                # status expressed faithfully
    omitted: ...                # proposition kept, status absent
    distorted: ...              # status strengthened (or cancelled for controls)
  expected:
    present: CONFIRM
    omitted: CONFIRM
    distorted: EXECUTE_UNAUTHORIZED
```

## Composition

- 36 over-commitment scenarios: 26 intentional, 10 conditional.
- 4 authorized-execution controls (MON-09, HEA-09, AUT-09, COM-09).
- 10 scenarios per domain.

## Automated checks

`G:/aconda/python.exe -m experiments.v3_p4_2_bank` must report:

- 40 scenarios, 160 items;
- 0 proposition flags (at least 2 shared content terms across the three
  variants);
- 0 length flags (token spread <= 3 after neutral filler);
- no schema errors.

The current bank passes all three.

## Human validation fields

`validation.csv` has blank columns:

- `realism_1_5`
- `status_clarity_1_5`
- `rule_clarity_1_5`
- `only_status_differs` (yes/no)
- `distortion_plausible_1_5`
- `stake_severity_1_5`
- `notes`

Two independent humans fill them blind to the expected decision. Gates are in
`docs/research/V3_P4_2_PROTOCOL_DRAFT.md`.

## Authoring rules

New scenarios must preserve the proposition, keep the variants within 3 tokens,
give a determinate authorization rule, and use a plausible distortion. Do not
use opinions, preferences, past evaluations, third-party states, or stylistic
status words. See the protocol for the full list.
