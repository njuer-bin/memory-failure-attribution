# V3 Pilot Freeze (2026-11-17)

Purpose: freeze the V3 pilot (P1–P5, replication, novelty audit) before moving
to real-dialogue feasibility work. This record does not replace any raw result;
it fixes what the existing numbers mean and what must not be edited.

## Git state

- Branch: `research/path-dependent-state-distortion-v3`
- Frozen commit: `15faa4d7d53915fdbb96b925f390d56dcfe2b177`
- Tag: `freeze/v3-pilot-2026-11-17`
- Tracked experiment artifacts: 254 files hashed in
  `docs/research/V3_FREEZE_MANIFEST.txt` (all of `results/`, `experiments/`,
  `evaluation/`, and `docs/research/V3_*`).
- Raw outputs under `results/status_drift_*` are committed and must not be
  overwritten by later work. New work goes to new directories.

## Frozen protocols, runners, analyzers

| Artifact | SHA-256 |
|---|---|
| `V3_P2_PROTOCOL.md` | `2548989c653d9d1da72fa18bcf8077ac408ff11cc21ebf4290a165b68a95e70b` |
| `V3_P2_FREEZE.md` | `104af773efdcfc29bf58f7a6634a318d7cc990b5680a330c771dbe1268ca4905` |
| `V3_P4_PROTOCOL.md` | `a5271b0acb6e8c27dcd9eb74e345aaf38831fc14a66d54c31de4a218c2fbd534` |
| `V3_P4_FREEZE.md` | `e993cd578dfd245e15606dfbbc5448394dbad3472c4f0e85f3b915572a6a1d9e` |
| `V3_P5_CONFIRMATORY_PROTOCOL.md` | `fc572426d857eb2eb03392d3a7a2c2cad7db7611795aa06094bdeaa0ef8f528f` |
| `V3_P5_CONFIRMATORY_FREEZE.md` | `bbbddbfc4d774d29f68df54f3562921d0b6f55b428eab0f9b7abb27f2e32973d` |
| `V3_REPLICATION_PROTOCOL.md` | `4f45d84ae88e88f3243a8cf56470a0b2d84e7d28c54e1127d3a238bcdeae7c7c` |
| `V3_REPLICATION_FREEZE.md` | `49aac527d6053f73f3868e8055cabd5804d2e7db3cf71ec77d94fe0e8f6bb3f7` |
| `V3_FORMAL_DEFINITIONS.md` | `2c984a124e299e4a6b8c4ed457bf108fc996d840ba4705e4a95852d9cff7faf2` |
| `V3_ANNOTATION_GUIDELINES.md` | `b9d2be5ab2c21654dc1712150f455ced3bc506075c27b7f91794ad762514157a` |
| `V3_STATISTICAL_ANALYSIS_PLAN.md` | `02b62b3da46b5b932efa9a5336d618b4ff0f1d70850e6be10f20ab78568e195d` |
| `v3_p2_paired_study.py` | `0d5cb0fc6f8591bdac4098f26c5fec343e2a76f5653ddd635c02f4f4026512cf` |
| `v3_p4_behavioral.py` | `36ec772b6608d4a27c84334f71b39d7ae8af4e287d00652244debe2dda94fda2` |
| `v3_p5_confirmatory.py` | `ace0bac58b66be6f8c00be92d1e5fa2f776b2125ea3963260e01a53aa774f7c2` |
| `analyze_p3_outcomes.py` | `a212ad8fe6080d5c8827f86a6fbe1302638ba8d2766f58f2b6481dab63dc0f5d` |
| `analyze_p5_confirmatory_outcomes.py` | `4ca1babce154643ccf4ec41f5432d27fe66beedcebb91e224328cd73d692d1e5` |

## Statistical caliber corrections

These clarify the existing numbers. No raw record is changed.

1. **Condition-level percentages are descriptive, not inferential.** The
   Wilson intervals in `condition_table.csv` treat items as independent, but
   items cluster within 30 trajectories. The trajectory-level estimates are the
   paired contrasts (10,000-resample bootstrap over per-trajectory paired
   differences). Do not quote a Wilson interval on a condition rate as a
   trajectory-level CI.
2. **Paired omission contrasts are cell-level proportions.** `mean_difference`
   is the paired difference in the fraction of *all* trajectory-condition
   cells labeled `STATUS_OMISSION`, not a difference in omission conditional on
   proposition preservation. The conditional rates are in the condition table
   (denominator = PRESERVED). Both are reported; do not relabel one as the
   other.
3. **Unsupported-distortion denominators differ.** 3/330 = 0.9% over all
   adjudicated items including the raw reference; 3/300 = 1.0% over the 300
   generated-condition items. Always state the denominator.
4. **Reliability kappas are item-level across all condition cells.** Kappa is
   prevalence-sensitive: P5 identity was raw 0.992 / κ 0.853, and the gemma
   writer evidence field raw 0.952 / κ 0.850. Report raw agreement and kappa
   together.
5. **Adjudication is model-assisted, not independent human adjudication.**
   Annotator A/B files are the primary labels and are preserved; the
   adjudication column is a model-assisted resolution. No text in this project
   may describe it as two independent human adjudicators.
6. **Do not mix guide versions.** P2/P3 used v3.2.3; the P5 recheck used
   v3.2.4; the gemma writer recheck used v3.2.5. Reliability statistics are
   reported per version and are not pooled.
7. **Writer replication cohort.** 30 trajectories were collected, but the
   pre-registered primary cohort is the first 12; the remaining 18 are
   exploratory and must be labeled as such.
8. **V2 numbers are not pooled.** All v2.x results are exploratory and use
   deterministic cue metrics and model judges. V3 is the confirmatory line.

## Freeze policy from here

- The frozen commit and tag are the reference for the pilot. Any rerun must go
  to a new results directory and carry its own run configuration.
- The real-dialogue work starts a new line (Stage 1+). It does not modify the
  synthetic-transformation results.
- Annotator provenance must be recorded for all new annotation sets. Model
  output may assist screening and adjudication, but it is never reported as
  human annotation.

## Integrity statement

No raw outputs, labels, or statistics were edited during this freeze. Only
documentation was added; the manifest records the hash of every tracked
experiment artifact at the frozen commit.
