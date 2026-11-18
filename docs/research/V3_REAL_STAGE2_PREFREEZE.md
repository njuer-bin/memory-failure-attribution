# Stage 2 Pre-Freeze Record (2026-11-18)

**Status: NOT FROZEN.** This record fixes the candidate v2.3 guide hashes and
the calibration artifacts so that the freeze can be evaluated against a stable
version. Run 2 (new annotator A) passed `gold_status` and failed
`gold_dimension` on κ with three boundary disagreements; a third-person
adjudication of those three items passes both gold gates
(`gold_dimension` 1.000 / 1.000; `gold_status` 0.975 / 0.969). The gold
calibration is therefore complete with adjudication. Stage 2 is still not
frozen: LSF/SSF calibration and the remaining freeze checklist are pending. Do
not run confirmatory generation from this record.

## Candidate guide and ontology (SHA-256)

| SHA-256 | File |
|---|---|
| `5cabe670c6119681e479c91afdad3380432ffe624c7a5735014c132d6f342b5c` | `docs/research/V3_REAL_STAGE2_DRAFT.md` (v2.3, boundary examples) |
| `621b8691c3cb21f8c93df6ba9b631b3880d075bd3818cb29949fd17499b4c904` | `docs/research/V3_REAL_DATA_AUDIT_PROTOCOL.md` |
| `2c984a124e299e4a6b8c4ed457bf108fc996d840ba4705e4a95852d9cff7faf2` | `docs/research/V3_FORMAL_DEFINITIONS.md` (ontology) |
| `4afa97f932f3b85fff48b5ee94c701c4e4389217e11b71ab4bdcd0822164de15` | `docs/research/2026-11-17-real-screening-results.md` (D1-D5 evidence) |

The D1-D5 revisions are in `V3_REAL_STAGE2_DRAFT.md` §8a: the stricter
`lexical_labelable`, the three-state `update_present`, the split
`evidence_sufficient`, the risk/dimension anchors, and the status-bearing
boundary anchors.

## Calibration artifacts

| SHA-256 | File |
|---|---|
| `3f85655a8fa728bd5b571c0e852eda8bb7b6475ca97cfb9ee4ee04dd535bc6a6` | `experiments/make_stage2_calibration_set.py` (current, profiles `full` / `intent_epi`) |
| `73b4579744cb2f29c5343618a831583d61476f77eb8a819304bd6f9567de6771` | `experiments/v3_real_feasibility_audit.py` (candidate screen) |
| `1b186ec96c1eba9af2f97fe18e8ec30351230319fa242b0e9c38d9c9bc55875d` | `results/status_drift_v3_real_audit/stage2_calibration_60/annotator_A.csv` |
| `1b186ec96c1eba9af2f97fe18e8ec30351230319fa242b0e9c38d9c9bc55875d` | `results/status_drift_v3_real_audit/stage2_calibration_60/annotator_B.csv` |
| `c5865d2ff1fbdc0c17c1b26a2a08411840fc68d386119c41901d3fe1ddbdaed6` | `results/status_drift_v3_real_audit/model_free_25/annotator_YTB.csv` |
| `316453f3a0787f0b75d8465616cc97062fe8c291adef1e7f22bb7ea94fa04fc8` | calibration key (outside repo) |
| `734893c2997b7664c652d6313fd1adeb036acb367cb58729fd9b23c86437a0db` | model-free key (outside repo) |

Keys are at `G:/memory_failure_backup/stage2_calibration_key_2026-11-18.csv`
and `G:/memory_failure_backup/stage2_model_free_key_2026-11-18.csv`. The hashes
are recorded here; the key files are not committed.

## Calibration set composition

- 60 items: 35 LoCoMo and 25 longmemeval (20 from the 44-57-session
  `longmemeval_s` instances, 5 from the oracle conditional arm).
- Exact composition: 30 LoCoMo intentional; 15 conditional (5 LoCoMo, 5
  longmemeval_s, 5 longmemeval oracle); 15 longmemeval_s non-conditional.
- Heuristic dimensions: 39 intentional, 15 conditional, 6 epistemic.
- 11 boundary-flagged items and 5 cue-mismatch items ("I think I'll", "I'll
  definitely").
- Exact screening items are excluded. **LoCoMo cannot be conversation-disjoint:**
  the public split has 10 conversations and all were used in the 50-item
  screening set. The calibration set reuses conversations but not items; report
  this as a limitation and do not call the set conversation-disjoint.
- Proposed strata and flags are in the key only, not in the annotator sheet.

## Calibration v1 result (2026-11-18)

- Both sheets complete (60/60); provenance files are missing.
- `gold_dimension` passes (raw 0.917 / κ 0.809).
- `gold_status` fails (raw 0.633 / κ 0.584). Normalizing the seven both-`E0`
  status entries raises it to raw 0.750 / κ 0.708, still below the raw gate.
- Conditional states fail at n=4 (raw 0.500); the conditional arm is too small
  to support a claim.
- Diagnosis: `E0` status encoding, desire vs intention ("I want to" →
  `INTERESTED`, not `INTENDING`), `EXECUTING` only for ongoing action, and
  conditional offers to the interlocutor are not conditional.
- The guide was revised to v2.1 (§8b). A **new** calibration set is required;
  do not reuse these 60 items in confirmatory data. The conditional pool is
  thin, so a new set may have fewer than 15 conditional items; report the
  shortfall rather than padding it.

See `2026-11-18-stage2-calibration-result.md` and
`stage2_calibration_60/analysis/agreement.json`.

## Calibration v2 candidate (2026-11-18)

`results/status_drift_v3_real_audit/stage2_calibration_60_v2/` excludes the 50
screening items and the 60 v1 calibration items. Composition: 60 items (35
LoCoMo, 25 longmemeval; 41 intentional, 12 epistemic, 7 conditional; 10
boundary, 6 cue-mismatch). The conditional pool is exhausted, so the set cannot
support a conditional-state gate. It is a candidate only; do not annotate until
the conditional decision (accept a descriptive conditional arm, or source more
conditional dialogue) is recorded.

- Generator: `52bb9697c9fa2eb7d691cb3fbd4e6eec857fe3067a3e0ea67cbdde534371ecb3`
- Sheets: `9d24d8223ed314ca215284d8400b991eed10e953be8be801277db84163b5953a`
- Key (outside repo):
  `19b4523bfb546b9fd36eb9ac61e589d221b14858d62597b29075be331aeeef1c`

## Decision C — 40-item intentional/epistemic set (2026-11-18)

Conditional is deferred to a separate set. The calibration set for the current
freeze decision is
`results/status_drift_v3_real_audit/stage2_calibration_40_intent_epi/`:

- 40 items: 25 LoCoMo, 15 longmemeval; 29 intentional, 11 epistemic; 7
  boundary, 4 cue-mismatch. No conditional items.
- Screening and v1 calibration items are excluded; the v2 candidate is
  superseded and its unannotated items may overlap.
- LoCoMo conversations are reused (10 public conversations, all screened);
  items are distinct, but the set is not conversation-disjoint.
- Gates: `gold_dimension` raw ≥0.85 / κ ≥0.70; `gold_status` raw ≥0.85 /
  κ ≥0.70. Strength and confidence are descriptive.

- Generator: `3f85655a8fa728bd5b571c0e852eda8bb7b6475ca97cfb9ee4ee04dd535bc6a6`
- Sheets: `43b18cd896296cdd1d7b6392e5c748255e5bcfd812b91b24e7ce9c5c3795e2f1`
- Key (outside repo):
  `1ced0d028e56abc921cfd2034a44352eae7460694b676a4a92907fb70c3ab457`

The conditional arm is a separate future set; the paper must not claim
conditional reliability from this calibration.

## 40-item calibration result (2026-11-18)

- Run 1 (old A) failed on rule adherence: `gold_dimension` 0.875 / κ 0.600,
  `gold_status` 0.675 / κ 0.607.
- Run 2 (new A, 2026-11-18): `gold_status` **passes** (raw 0.900, κ 0.875);
  `gold_dimension` fails on κ (raw 0.925, κ 0.639). Only three disagreements:
  an instruction to the assistant (`S2IE-003`), past/emotional musing
  (`S2IE-021`), and a completed-action vs factual-claim boundary
  (`S2IE-025`).
- v2.3 adds examples for the three boundaries. The status ontology is working;
  the dimension gate is a boundary/prevalence issue, not a broad failure.
- Third-person adjudication (2026-11-18): `S2IE-003` E0, `S2IE-021` E0,
  `S2IE-025` intentional COMPLETED. Adjudicated agreement: `gold_dimension`
  1.000 / κ 1.000; `gold_status` 0.975 / κ 0.969; `gold_strength` 0.725 /
  κ 0.472. Both gold gates pass; original A/B labels preserved.
- Gold calibration is complete with adjudication. Next: LSF/SSF memory sheet,
  then the full freeze checklist. These 40 items are not confirmatory data.

See `2026-11-18-stage2-calibration-40-result.md`, `analysis/agreement_run1_2026-11-18.json`,
and `analysis/agreement_run2.json`.

## Model-free re-annotation subset

25 screening items, stratified across dataset and auto dimension, re-issued
with new ids and blank ratings. YTB re-annotates from scratch without the AI
first draft, the earlier A/B labels, or the key. This estimates how much the
original B was anchored by the draft; it is an anchoring sensitivity analysis,
not a new two-human reliability estimate.

## What is still blocked

1. B's screening labels are `human-reviewed-model`; the 25-item model-free
   subset is the anchoring check. A's screening provenance is recorded.
2. YTB has not yet re-annotated the 25-item model-free subset.
3. Gold calibration passes after third-person adjudication of the three
   boundary items. Next: LSF/SSF calibration on a generated-memory sheet, then
   the remaining freeze checklist. Conditional remains deferred.
4. LSF/SSF calibration needs generated memory variants `M`; that sheet does not
   exist yet.
5. The guide, cue table, inclusion rules, adjudication order, reliability
   gates, annotation schema, and analysis plan have not been frozen together.

## Freeze checklist (from the draft §14)

- [ ] Model-free subset completed and the anchoring comparison reported.
- [x] 40-item intentional/epistemic calibration passed the pre-registered
      gates after third-person adjudication of three boundary items.
      (`gold_dimension` 1.000/1.000; `gold_status` 0.975/0.969.)
- [ ] LSF/SSF calibration passed on a separate memory sheet.
- [ ] Cue table, inclusion/exclusion rules, adjudication order, and analysis
      plan hashed together with the guide.
- [ ] Stage 2 freeze record written with all hashes; only then may confirmatory
      generation start.

## Commands

```
G:/aconda/python.exe -m experiments.make_stage2_calibration_set
G:/aconda/python.exe -m experiments.v3_real_feasibility_audit
```

Regenerating the calibration set overwrites the blank sheets; do not regenerate
after annotation starts.
