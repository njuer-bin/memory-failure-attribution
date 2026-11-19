# V3 Numbers Table (internal source of truth)

Status: internal working artifact, 2026-11-18. Not part of the submission.
Every number in `V3_PAPER_DRAFT.md` must trace to a row here and to the listed
artifact. If a number changes, change it here first.

Conventions:

- `n/N` is count/denominator. Rates are proportions.
- Paired differences are trajectory- or scenario-level paired means with
  cluster bootstrap 95% intervals (10,000 resamples), unless stated otherwise.
- `omission` is `STATUS_OMISSION` among `PRESERVED` items.
- `unsupported` is `UNSUPPORTED_STATUS_DISTORTION` among `PRESERVED` items.
- `faithful` = `NO_DISTORTION` + `LEGITIMATE_UPDATE` among `PRESERVED` items.
- `PLR` (proposition loss rate) = `PARTIAL` + `LOST` over all items in the
  condition.
- Reliability is Cohen's kappa on adjudicated/primary labels per the run note.

## 1. P2 generation (frozen)

Source: `docs/research/V3_P2_PROTOCOL.md`,
`results/status_drift_v3_p2/summary.json`, `run_config.json`.

| Quantity | Value |
|---|---|
| Trajectories | 30 = 5 topics x 3 dimensions x 2 update variants |
| Topics | 换一份工作, 开始健身, 开一家网店, 学会游泳, 考驾照 |
| Generated conditions | 300/300; raw references 30; total artifacts 330 |
| Generation errors / empty finals | 0 / 0 |
| Writer | qwen2.5:7b (local Ollama), neutral prompt |
| Final budget | 100 Chinese characters (prompt target) |
| Seeds | 42 (deterministic and temp1), 43 (temp2) |
| Temperature | 0.0 deterministic; 0.7 temp1/temp2 |

Condition means (final chars / eval tokens / topic-mention):

| Condition | Chars | Tokens | Topic mention |
|---|---:|---:|---:|
| direct | 28.2 | 20.0 | 0.967 |
| recursive | 22.7 | 16.4 | 0.900 |
| rewrite_matched | 23.0 | 16.5 | 0.900 |
| repeated_direct | 28.4 | 20.1 | 0.967 |
| source_peek | 28.2 | 20.1 | 0.967 |
| para | 23.6 | 17.5 | 0.933 |
| temp1 | 20.7 | 15.4 | 0.867 |
| temp2 | 21.9 | 16.1 | 0.867 |
| path_s2 | 21.5 | 15.8 | 0.833 |
| retrieval | 46.8 | n/a | 1.000 |

## 2. P3 annotation (frozen, blind human labels)

Source: `docs/research/2026-11-17-v3-p3-outcomes.md`,
`results/status_drift_v3_p2/analysis/p3_summary.json`,
`annotation/annotator_A.csv`, `annotator_B.csv`, `adjudication.csv`.

| Field | n | Raw | Kappa |
|---|---:|---:|---:|
| proposition_identity | 330 | 0.991 | 0.943 |
| primary_dimension | 330 | 1.000 | 1.000 |
| status_expressed | 330 | 0.988 | 0.972 |
| expressed_status | 330 | 0.991 | 0.989 |
| action_status | 330 | 0.961 | 0.924 |
| evidence_support | 330 | 0.988 | 0.972 |
| primary_judgment | 330 | 0.967 | **0.944** |
| confidence | 330 | 0.742 | 0.266 |

Adjudication: 23 overrides, model-assisted (not human). One B data-entry
inconsistency (P2A-0149) resolved; original labels preserved.

## 3. P3 outcomes

Source: same as §2; `analysis/condition_table.csv`,
`analysis/paired_contrasts.csv`.

Labels (n = 330): NO_DISTORTION 182, STATUS_OMISSION 88, PROPOSITION_LOSS 30,
LEGITIMATE_UPDATE 27, UNSUPPORTED_STATUS_DISTORTION 3.
Identity: PRESERVED 300, PARTIAL 29, LOST 1.
Joint: preserved-faithful 209, preserved-omission 88, preserved-unsupported 3,
proposition-loss 30.

| Condition | n | PLR | Preserved | USDR | Omission | Faithful |
|---|---:|---:|---:|---:|---:|---:|
| raw | 30 | 0.000 | 30 | 0.000 | 0.000 | 1.000 |
| direct | 30 | 0.100 | 27 | 0.000 | 0.037 | 0.963 |
| recursive | 30 | 0.100 | 27 | 0.037 | 0.444 | 0.519 |
| rewrite_matched | 30 | 0.133 | 26 | 0.000 | 0.462 | 0.538 |
| repeated_direct | 30 | 0.100 | 27 | 0.000 | 0.037 | 0.963 |
| source_peek | 30 | 0.000 | 30 | 0.000 | 0.000 | 1.000 |
| para | 30 | 0.200 | 24 | 0.000 | 0.542 | 0.458 |
| temp1 | 30 | 0.133 | 26 | 0.077 | 0.423 | 0.500 |
| temp2 | 30 | 0.100 | 27 | 0.000 | 0.519 | 0.481 |
| path_s2 | 30 | 0.133 | 26 | 0.000 | 0.538 | 0.462 |
| retrieval | 30 | 0.000 | 30 | 0.000 | 0.333 | 0.667 |

Paired vs recursive (trajectory-level, 30 pairs):

| Condition | Omission diff [95% CI] | Faithful diff [95% CI] |
|---|---|---|
| direct | -0.367 [-0.567, -0.167] | +0.400 [0.200, 0.600] |
| repeated_direct | -0.367 [-0.567, -0.167] | +0.400 [0.200, 0.600] |
| source_peek | -0.400 [-0.567, -0.233] | +0.533 [0.367, 0.700] |
| rewrite_matched | 0.000 [-0.167, 0.167] | 0.000 [-0.167, 0.167] |
| para | +0.033 [-0.167, 0.233] | -0.100 [-0.300, 0.100] |
| temp1 | -0.033 [-0.233, 0.167] | -0.033 [-0.200, 0.133] |
| temp2 | +0.067 [-0.100, 0.233] | -0.033 [-0.133, 0.067] |
| path_s2 | +0.067 [-0.067, 0.200] | -0.067 [-0.167, 0.000] |
| retrieval | -0.067 [-0.333, 0.200] | +0.200 [-0.067, 0.467] |

Dimension (110 items each, omission among preserved): conditional 0.276,
epistemic 0.330, intentional 0.273. PLR: 0.109 / 0.064 / 0.100. One
unsupported case in each dimension. USDR events: recursive 1, temp1 2.

## 4. P4 behavioral study (qwen2.5:7b)

Source: `docs/research/2026-11-17-v3-p4-behavioral.md`,
`results/status_drift_v3_p4/records.jsonl`.

Completeness: 30/30 trajectories, 120/120 items, 0 parse failures, 0 errors.

| Variant | PROCEED | CONFIRM | ABSTAIN | Unauthorized | Evidence-consistent |
|---|---:|---:|---:|---:|---:|
| present | 12 | 18 | 0 | 2/30 = 0.067 | 28/30 = 0.933 |
| omitted | 0 | 30 | 0 | 0/30 = 0.000 | 20/30 = 0.667 |
| distorted | 20 | 10 | 0 | 20/30 = 0.667 | 0/30 = 0.000 |
| no_memory | 0 | 13 | 17 | 0/30 = 0.000 | 20/30 = 0.667 |

Paired vs present:

| Contrast | Unauthorized | Evidence-consistent |
|---|---|---|
| omitted | -0.067 [-0.167, 0.000] | -0.267 [-0.467, -0.067] |
| distorted | +0.600 [0.433, 0.767] | -0.933 [-1.000, -0.833] |

Conditional agent-side collapse under present: 2/10 (both present-status
unauthorized cases). Conditional omitted 0/10 unauthorized; conditional
distorted 10/10.

**Artifact caveat.** `results/status_drift_v3_p4/summary.json` contains stale
paired contrasts (+0.667 / -0.333) and a stale by-dimension present count
(0/10). The raw records and the run note agree on +0.600 / -0.267 and 2/10;
use the run note. Do not cite `summary.json` directly.

## 5. P4 gemma3:12b agent replication

Source: `docs/research/2026-11-17-v3-replication.md` §2,
`results/status_drift_v3_replication_agent/summary.json`.

| Variant | Unauthorized | Evidence-consistent |
|---|---:|---:|
| present | 0/30 | 30/30 |
| omitted | 0/30 | 20/30 |
| distorted | 20/30 | 0/30 |
| no_memory | 0/30 | 20/30 |

Present-status conditional collapse: 0/30 (qwen: 2/30).

## 6. P4.2 bank validation

Source: `docs/research/2026-11-18-v3-p4-2-results.md`,
`results/status_drift_v3_p4_2/analysis/validation_summary.json`,
`docs/research/V3_P4_2_FREEZE.md`.

Bank: 40 scenarios (10 each: money, health, authorization, commitments);
36 over-commitment (26 intentional, 10 conditional) + 4 authorized-execution
controls; 4 variants = 160 items.

Two blind human annotators (WMY, YTB), provenance recorded, no model
assistance.

| Field | Pooled mean | A | B |
|---|---:|---:|---:|
| realism (1-5) | 4.1125 | 3.975 | 4.250 |
| status clarity | 4.975 | 5.000 | 4.950 |
| rule clarity | 4.950 | 4.950 | 4.950 |
| distortion plausibility | 4.250 | 4.025 | 4.475 |
| stake severity | 3.350 | 3.275 | 3.425 |

`only_status_differs`: yes-both 38/40 = 0.950; yes-either 39/40 = 0.975;
exact agreement 0.975; kappa 0.655. Excluded: AUT-05 (both no), AUT-01
(B no, A yes; A dissent recorded). Frozen bank: 38 scenarios / 152 items,
34 over-commitment + 4 controls; 28 intentional + 10 conditional.

## 7. P4.2 run — v2 single-form design (superseded)

Superseded by §7b; reported here only so that the record shows what the design
amendment changed. Do not pool §7 and §7b.

Source: same as §6; `results/status_drift_v3_p4_2/run/summary.json`,
`records_qwen2_5_7b.jsonl`, `records_gemma3_12b.jsonl`.

304/304 calls (38 x 4 x 2 models), 0 parse failures, authorized controls
4/4 present in both models.

| Variant | qwen unauthorized | gemma unauthorized |
|---|---:|---:|
| present | 0/38 | 0/38 |
| omitted | 6/38 = 0.158 | 5/38 = 0.132 |
| distorted | 9/38 = 0.237 | 8/38 = 0.211 |
| no_memory | 0/38 | 0/38 |

Paired vs present:

| Contrast | qwen | gemma |
|---|---|---|
| omitted | +0.158 [0.053, 0.289] | +0.132 [0.026, 0.237] |
| distorted | +0.237 [0.105, 0.368] | +0.211 [0.079, 0.342] |

Over-commitment scenarios only (n = 34):

| Contrast | qwen | gemma |
|---|---|---|
| omitted unauthorized | 2/34 = 0.059 | 3/34 = 0.088 |
| distorted unauthorized | 9/34 = 0.265 | 8/34 = 0.235 |
| omitted - present | +0.059 [0.000, 0.147] | +0.088 [0.000, 0.206] |
| distorted - present | +0.265 [0.118, 0.412] | +0.235 [0.088, 0.382] |
| distorted - omitted | +0.206 [0.088, 0.353] | +0.147 [0.029, 0.265] |

Controls (n = 4):

| Variant | qwen | gemma |
|---|---|---|
| present EXECUTE | 4/4 | 4/4 |
| omitted EXECUTE | 4/4 | 2/4 |
| distorted EXECUTE | 0/4 | 0/4 |
| no_memory EXECUTE | 0/4 | 0/4 |

Conditional: omission 0/10 both; distorted 2/10 qwen, 3/10 gemma;
agent-side conditional collapse 0/10 both.

## 7b. P4.2 v3.1 factorial run (primary agent result)

Source: `docs/research/2026-11-19-v3-p4-2-v31-run.md`;
`results/status_drift_v3_p4_2_v3_v31/run/summary.json`;
`results/status_drift_v3_p4_2_v3_v31/analysis/` (`condition_table.csv`,
`paired_contrasts.csv`, `request_form_interactions.csv`).

Design: 54 scenarios = 24 intentional + 10 conditional over-commitment (34)
plus 20 authorized controls; 2 request forms × 4 variants × 2 models = 864
calls; 432/432 per model, parse 1.000, 0 empty. Temperature 0, seed 20261118,
items sha256 `a77dd300…`, bank sha256 `d3b1152b…`, runner sha256 `3b5c15e7…`.

Control gate (present EXECUTE): gemma neutral 20/20, action 18/20; qwen
neutral 16/20, action 10/20. gemma is the primary agent model.

Over-commitment unauthorized execution (gemma; n = 34 per cell):

| Memory | neutral | action |
|---|---:|---:|
| present | 0/34 | 0/34 |
| omitted | 5/34 = 0.147 | 0/34 |
| distorted | 24/34 = 0.706 | 10/34 = 0.294 |
| no_memory | 0/34 | 0/34 |

Paired vs present (gemma, n = 34): neutral omitted +0.147 [0.029, 0.265],
neutral distorted +0.706 [0.559, 0.853]; action omitted 0.000, action distorted
+0.294 [0.147, 0.441].

Excluding 6 action-completed distortions (n = 28): neutral omitted +0.179
[0.036, 0.321], neutral distorted +0.679 [0.500, 0.857]; action distorted
+0.250 [0.107, 0.429].

Request-form interaction (action minus neutral, gemma, n = 28): distorted
−0.429 [−0.607, −0.250]; omitted −0.179 [−0.321, −0.036].

By dimension, over-commitment only (gemma, unauthorized): intentional
n=24 neutral present 0 / omitted 3 / distorted 16, action 0 / 0 / 4;
conditional n=10 neutral 0 / 2 / 8, action 0 / 0 / 6. Present-status
conditional collapse 0/10.

Action-completed distortion subset (6 scenarios): gemma distorted neutral 5/6,
action 3/6; qwen 1/6 neutral, 0/6 action.

Authorized controls (gemma): neutral present 20/20, omitted 7/20, distorted
1/20, no_memory 0/20; action present 18/20, omitted 2/20, distorted 0/20,
no_memory 0/20.

qwen: 1/34 distorted executions in each form; floor-limited, reported as a
model limitation, not a replication.

## 8. P4.2 control-wording probe (v2)

Source: `docs/research/2026-11-18-v3-p4-2-results.md` §control probe;
`results/status_drift_v3_p4_2/control_v2/`.

16 items x 2 models = 32 calls; 0 parse failures. New cohort, not part of the
frozen 38.

| Variant | qwen | gemma |
|---|---|---|
| present EXECUTE | 4/4 | 4/4 |
| omitted EXECUTE (topic-only) | 1/4 | 3/4 |
| distorted EXECUTE | 0/4 | 0/4 |
| no_memory EXECUTE | 0/4 | 0/4 |

v1 omitted controls executed: qwen 4/4, gemma 2/4.

## 9. P4.2 v2 unauthorized reason coding (analyst, post hoc; superseded)

Source: `results/status_drift_v3_p4_2/analysis/unauthorized_reason_codes.csv`.

32 unauthorized records: 17 distorted + 15 omission (11 main + 4 probe).

| Code | Count | Definition |
|---|---:|---|
| D1_FOLLOWED_DISTORTED_MEMORY | 17 | Distorted memory states the authorizing status; agent follows it |
| O1_ASSERTED_UNSTATED_COMMITMENT | 6 | Agent asserts committed/decided/agreed, absent from memory |
| O2_MENTION_AS_COMMITMENT | 3 | Agent upgrades "mentioned X" to a commitment |
| O3_REQUEST_AS_AUTHORIZATION | 6 | Agent uses the current request/date as authorization |

Caveat: not human annotation; not pre-registered; gold-unblinded.

## 9b. P4.2 v3.1 unauthorized reason coding (analyst, post hoc)

Source: `docs/research/2026-11-19-v3-p4-2-v31-run.md`;
records in `results/status_drift_v3_p4_2_v3_v31/run/records_gemma3_12b.jsonl`.

39 gemma over-commitment executions (24 distorted neutral, 10 distorted action,
5 omitted neutral):

| Code | Count | Distribution |
|---|---:|---|
| D1_FOLLOWED_DISTORTED_MEMORY | 34 | 24 neutral + 10 action; 8 in the action-completed subset |
| O2_MENTION_AS_COMMITMENT | 5 | all neutral omitted |
| O1_ASSERTED_UNSTATED_COMMITMENT | 0 | — |
| O3_REQUEST_AS_AUTHORIZATION | 0 | — |

Every omission execution turns "The user mentioned X-ing" into "the user X-ed";
one (COM-01) also treats the conditional clause as satisfied. No case uses the
current request as authorization. Caveat: analyst, post hoc, gold-unblinded.

## 10. P5 confirmatory generation

Source: `results/status_drift_v3_p5/summary.json`, `run_config.json`,
`docs/research/2026-11-17-v3-p5-confirmatory.md`.

30 trajectories x 4 conditions = 120/120, 0 errors. Chain 220 -> 180 -> 140
-> 120 -> 100. Writer qwen2.5:7b.

| Condition | Deterministic MATCH/30 | ABSENT | AMBIGUOUS | Budget vs neutral |
|---|---:|---:|---:|---:|
| neutral | 14 | 16 | 0 | 1.00x |
| status_aware | 27 | 3 | 0 | 1.05x |
| neutral_source | 29 | 1 | 0 | 1.23x |
| status_aware_source | 27 | 0 | 3 | 1.38x |

## 11. P5 human outcomes (v3.2.4 recheck)

Source: `docs/research/2026-11-17-v3-p5-confirmatory.md` §7,
`results/status_drift_v3_p5/analysis_v324/`.

Reliability: primary raw 0.992 / kappa 0.974; identity 0.992/0.853; action
0.992/0.984; evidence 0.983/0.942. 19 overrides, model-assisted.

| Condition | Faithful | Omission | Unsupported | Ambiguous | Loss |
|---|---:|---:|---:|---:|---:|
| neutral | 14/26 = 0.538 | 11/26 = 0.423 | 1/26 = 0.038 | 0/26 | 4/30 = 0.133 |
| status_aware | 27/30 = 0.900 | 0/30 | 2/30 = 0.067 | 1/30 | 0/30 |
| neutral_source | 30/30 = 1.000 | 0/30 | 0/30 | 0/30 | 0/30 |
| status_aware_source | 28/30 = 0.933 | 0/30 | 1/30 = 0.033 | 1/30 | 0/30 |

Paired vs neutral:

| Contrast | Faithful | Omission |
|---|---|---|
| status_aware | +0.433 [0.267, 0.600] | -0.367 [-0.533, -0.200] |
| neutral_source | +0.533 [0.367, 0.700] | -0.367 [-0.533, -0.200] |
| status_aware_source | +0.467 [0.300, 0.633] | -0.367 [-0.533, -0.200] |

Interaction (faithful): -0.500 [-0.667, -0.333].
status_aware_source vs neutral_source: -0.067 [-0.167, 0.000].

## 12. gemma3:12b writer replication (first 12 trajectories)

Source: `docs/research/2026-11-17-v3-replication.md` §6,
`results/status_drift_v3_replication_writer/analysis_v325/`.

Reliability: primary raw 0.940 / kappa 0.834; identity 1.000; status_expressed
1.000; expressed 1.000; action 0.964/0.924; evidence 0.952/0.850. 12
overrides, model-assisted. Deviation: the runner generated 30 trajectories;
first 12 are the pre-registered cohort.

| Condition | Faithful | Omission | Unsupported | Ambiguous |
|---|---:|---:|---:|---:|
| direct | 11/12 | 1/12 | 0/12 | 0/12 |
| repeated_direct | 11/12 | 1/12 | 0/12 | 0/12 |
| neutral_source | 10/12 | 1/12 | 1/12 | 0/12 |
| status_aware | 11/12 | 0/12 | 1/12 | 0/12 |
| status_aware_source | 12/12 | 0/12 | 0/12 | 0/12 |
| recursive | 8/12 | 1/12 | 3/12 | 0/12 |
| rewrite_matched | 6/12 | 1/12 | 3/12 | 2/12 |

## 13. Real-dialogue feasibility audit

Source: `docs/research/2026-11-17-real-dialogue-feasibility-audit.md`,
`docs/research/2026-11-17-real-screening-results.md`,
`results/status_drift_v3_real_audit/candidates.csv`.

| Dataset | Candidates | Conditional | Epistemic | Intentional |
|---|---:|---:|---:|---:|
| LoCoMo (10 conversations x 19 sessions) | 140 | 10 | 46 | 84 |
| LongMemEval oracle (500 x 3 sessions) | 1,995 | 21 | 935 | 1,039 |
| Total | 2,135 | 31 | 981 | 1,123 |

Later-session change cue: 269/2,135 = 12.6%. Later re-mention: 725/2,135 =
34.0%.

50-item screening set: LoCoMo 20, LongMemEval 30; marker dimensions
conditional 13, epistemic 14, intentional 23; 36 unique sources; 35 later
re-mentions.

Model diagnostic (Claude Sonnet 4.6, not human): status-bearing 42/50;
semantic dimension intentional 32, conditional 8, mixed 3, epistemic 2, none
5; proposition clear 43; evidence sufficient 39; consequential 4 yes / 29
partial / 17 no.

Human screening agreement (A=WMY; B=YTB with AI first draft, human-reviewed):
dimension raw 0.920 / kappa 0.826; semantic_labelable 0.960/0.730;
status_bearing 0.920/0.606; evidence_sufficient 0.820/0.535;
lexical_labelable 0.660/0.226; update_present 0.840/0.170.

## 14. Real-dialogue gold calibration

Source: `docs/research/2026-11-18-stage2-calibration-40-result.md`,
`docs/research/2026-11-18-real-data-arm-scoping.md`.

60-item calibration: `gold_dimension` 0.917/0.809 (pass);
`gold_status` 0.633/0.584 (fail; 0.750/0.708 after E0 normalization);
conditional n=4, 0.500. Guide revised to v2.1.

40-item calibration run 1: `gold_dimension` 0.875/0.600 (fail);
`gold_status` 0.675/0.607 (fail). 10/13 status disagreements are v2.1
violations by A.

40-item calibration run 2 (new A): `gold_dimension` 0.925/0.639 (fail on
kappa); `gold_status` 0.900/0.875 (pass); `gold_strength` 0.675/0.326;
`gold_confidence` 0.725/0.362.

Third-person adjudication of S2IE-003 (E0), S2IE-021 (E0), S2IE-025
(intentional COMPLETED): `gold_dimension` 1.000/1.000;
`gold_status` 0.975/0.969; `gold_strength` 0.725/0.472.

## 15. LSF/SSF calibration (failed twice)

Source: `docs/research/2026-11-18-stage2-lsf-ssf-result.md`,
`docs/research/2026-11-18-stage2-lsf-ssf-run2-result.md`.

Sheet: 15 gold items (14 intentional, 1 epistemic) x direct/recursive/
source_peek = 45 memories; writer qwen2.5:7b. Mean final words: direct 20.9,
recursive 19.1, source_peek 24.2.

| Field | Run 1 raw/kappa | Run 2 raw/kappa | Gate |
|---|---:|---:|---|
| lsf_outcome | 0.733 / 0.581 | 0.800 / 0.689 | 0.85 / 0.70 |
| ssf_outcome | 0.578 / 0.432 | 0.756 / 0.625 | 0.80 / 0.65 |
| proposition_identity | 0.756 / 0.507 | 0.800 / 0.607 | 0.90 / 0.80 |
| status_assigned_from_memory | 0.667 / 0.569 | 0.844 / 0.778 | descriptive |

Decision C: real-data arm scoped to feasibility + gold calibration; LSF/SSF
reported as failed calibration and future work; no confirmatory real-dialogue
generation.

## 16. Novelty audit

Source: `docs/research/2026-11-17-novelty-audit.md`,
`literature/pdfs/` (14 PDFs, full text).

Prior work covers: state tracking vs recall (StateMem), structured state
programs (ProgMem), AGM belief revision (BELIEFMEM), implicit stale state and
downstream policy adaptation (STALE), state-to-draft verification
(StateAuditor), recursive summarization omission/update (ABBEL), chained
bounded-note rewriting (Supersede), raw-history preservation and query-time
compression (LiveCtx), periodic recursive summarization (ReSum), compression
lifecycle (LightMem), transactional belief commit and action-safety gating
(MemTX), false authority -> unauthorized action (EAL-Bench), belief-change
intervention (TWIST), derived-state benchmark (MemDerive).

Defensible contribution: status-specific, proposition-controlled
transformation-history diagnostic with the omission/distortion split, blind
human labels, a status-only downstream intervention, and a second-model
replication.
