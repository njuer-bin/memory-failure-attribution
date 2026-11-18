# V3 P4.2 Freeze Record (2026-11-18)

**Decision:** freeze the validated P4.2 scenario bank at **38 scenarios / 152
runnable items** (40 built, 2 excluded by two-human validation). The bank,
the validation sheets, the validation summary, and the checker are frozen. The
P4.2 protocol remains a draft until the runner is written and frozen
separately.

## Frozen artifacts (SHA-256)

| SHA-256 | File |
|---|---|
| `1b0ad5601bd2f98a0005312061a2188c72785db125e973b651cfc98ede0fc20d` | `datasets/p4_2_scenarios/p4_2_scenarios.yaml` |
| `2cb4619237a6b92d2cbe6e75ce5d2b2c28e2f900fbc35bcf068b0c0424559729` | `experiments/v3_p4_2_bank.py` |
| `a12b39da507a591ecfe52a58066f332cde6c8230395b8418ff3f5a805464f922` | `experiments/check_p4_2_validation.py` |
| `0253ff0e1e2409408d7d8d7bc00139fa7bf9c73267671a911c8df849c6b8824c` | `results/status_drift_v3_p4_2/items.jsonl` (all 160 items, pre-exclusion) |
| `57666f457a87b1e42917ff494564f1548170240dc1a79259dcd4b17dfcf27f26` | `results/status_drift_v3_p4_2/validation.csv` (internal sheet; do not share) |
| `f162ea4c9d52a5452391a13e05ab8973266ba9ac0a40010e49f14e6046578859` | `results/status_drift_v3_p4_2/validation_A.csv` |
| `532a10c892980569b1fdd106738cfd7149676eed2e7b863a24e337901172aab2` | `results/status_drift_v3_p4_2/validation_B.csv` |
| `9e69af1a7951ac0ddb33913060b200d10e0744dee5ffa93d067742dd5587eba5` | `results/status_drift_v3_p4_2/validation_provenance_A.json` |
| `cdf756af209ac259b77ac29f30a23aed5c0a7dcf0f3d8bda4a2b14227a695415` | `results/status_drift_v3_p4_2/validation_provenance_B.json` |
| `882bef75cadaf9048dd73d15f9bd4b2c6bb22a19379997dc691f7d3cffcf7902` | `results/status_drift_v3_p4_2/analysis/validation_summary.json` |
| `c31607974c18e498886f833c6464bbce0ffbc237fcb8177b9938a8cc0a811474` | `docs/research/P4_2_VALIDATION_HOWTO.md` |

Base commit: `ad1ac7d8ecfe91c2832447ac1ed216298d1f348e`. The validation
outputs were uncommitted at freeze time; the hashes above are the working-tree
files as of 2026-11-18.

## Validation provenance

- Annotator A: WMY, human, 2026-11-18, independent, blind to expected labels.
- Annotator B: YTB, human, 2026-11-18, independent, blind to expected labels.
- Both read the how-to and the scenario fields only; neither read
  `validation.csv`, `items.jsonl`, or the protocol's expected-decision section.
- No model assistance on any row.
- Rows were not re-shuffled between A and B; both sheets share the same row
  order. This does not affect blindness because the sheets were filled
  independently and the other annotator's file was not opened.

## Gate results

Means are pooled across both annotators (80 ratings per scalar); the protocol
does not specify per-annotator means, and this interpretation is declared here,
before the run. Per-annotator means are reported for transparency.

| Gate | Threshold | Value | Pass | A | B |
|---|---:|---:|---|---:|---:|
| Realism | ≥4.0 | 4.1125 | yes | **3.975** | 4.250 |
| Status clarity | ≥4.0 | 4.9750 | yes | 5.000 | 4.950 |
| Rule clarity | ≥4.0 | 4.9500 | yes | 4.950 | 4.950 |
| Distortion plausibility | ≥4.0 | 4.2500 | yes | 4.025 | 4.475 |
| Stake severity | ≥3.0 | 3.3500 | yes | 3.275 | 3.425 |
| `only_status_differs=yes` | ≥95% | 38/40 = 0.950 | yes | — | — |
| Survivors | ≥36 | 38 | yes | — | — |

Disclosed caveat: A's own realism mean is 3.975, 0.025 below the threshold.
The pass depends on B being slightly higher. The alternative strict reading
(both annotators must reach 4.0) fails by one rating on A's sheet. The bank is
frozen under the pooled interpretation; any later analysis that uses the strict
reading must report that this gate would not pass.

Descriptive agreement (no agreement gate was pre-registered for the scalar
ratings): realism exact agreement 0.525, distortion plausibility 0.550, stake
severity 0.650; status clarity 0.950, rule clarity 0.950. `only_status_differs`
exact agreement 0.975, Cohen's κ 0.655 (one disagreement; κ is
prevalence-sensitive).

## Exclusions

| Scenario | Validation | Reason |
|---|---|---|
| `AUT-05` | A `no`, B `no` | `distorted` changes the scope from read-only consideration to admin approval; the proposition/object differs across variants. |
| `AUT-01` | A `yes`, B `no` | `present` says calendar only and no email; `distorted` says calendar **and email** are authorized. The scope change is verifiable in the text, so B's judgment is adopted and A's dissent is recorded here. |

Both are `over_commitment` scenarios; the four authorized-execution positive
controls are unaffected. Exclusion is a maintainer decision based on the
scenario text and the annotator notes, not a model adjudication.

## Frozen composition

- 38 scenarios: money 10, health 10, commitments 10, authorization 8.
- 34 over-commitment + 4 authorized-execution controls.
- 28 intentional + 10 conditional.
- 152 runnable items (38 × 4 variants: present / omitted / distorted /
  no_memory).
- Planned run: 38 scenarios × 4 variants × 2 agent models = **304 calls**
  (the protocol draft's 320 included the two excluded scenarios).

The runner must filter to the 38 surviving scenario IDs; `items.jsonl` keeps
all 160 pre-exclusion items and is not itself the frozen runnable set.

## Freeze rule

Any change to a frozen artifact invalidates this record. Create a new protocol
version and a separate cohort; do not edit the bank, the validation sheets, the
summary, or the checker in place. The protocol draft and the runner are frozen
separately, before the first P4.2 agent call.
