# V3 Second-Model Replication — gemma3:12b (2026-11-17)

> **Update (v3.2.5 writer recheck):** the 84 writer items were re-annotated
> under v3.2.5; primary-judgment κ **0.834**. §6 supersedes the provisional
> writer numbers in §5. The agent result in §2 is unchanged.

**Protocol:** `V3_REPLICATION_PROTOCOL.md`, frozen `V3_REPLICATION_FREEZE.md`.
**Models:** `gemma3:12b` for both writer and agent.
**Status:** writer replication generated; 84-item blind human set pending.
Agent replication complete.

## 1. Writer phase

The runner was resumed without `--limit 12`, so it generated all 30 P2
trajectories (210/210 conditions); the pre-registered R1 cohort is the first
12, and the other 18 are exploratory. This deviation is recorded, not hidden.

Deterministic MATCH/12 (first 12 trajectories):

| Condition | MATCH | ABSENT | AMBIGUOUS |
|---|---:|---:|---:|
| direct | 7 | 3 | 2 |
| recursive | 2 | 9 | 1 |
| rewrite_matched | 0 | 11 | 1 |
| repeated_direct | 7 | 3 | 2 |
| neutral_source | 4 | 6 | 2 |
| status_aware | 7 | 3 | 2 |
| status_aware_source | 8 | 2 | 2 |

Across all 30 trajectories the same direction holds: direct 19/30,
recursive 5/30, rewrite-matched 4/30, repeated-direct 18/30, neutral-source
15/30, status-aware 15/30, combined 20/30.

**Interpretation.** The chaining effect replicates: direct and repeated-direct
preserve more deterministic status than recursive and rewrite-matched, and
rewrite-matched equals recursive. Source access does **not** restore status as
strongly as it did with qwen2.5:7b (neutral-source 4/12 here vs 29/30 there),
which may be a model difference or a cue-extraction difference from gemma's
longer paraphrases. Human labels are required; deterministic cues are not the
primary outcome.

Budget inflation vs recursive: direct 1.23×, rewrite-matched 1.04×,
repeated-direct 1.24×, neutral-source 1.19×, status-aware 1.26×, combined
1.35×. gemma writes longer memories than qwen.

## 2. Agent phase (complete)

30 trajectories × 120 decisions, 0 parse failures. Same scoring as P4.

| Variant | PROCEED | CONFIRM | ABSTAIN | Unauthorized | Evidence-consistent |
|---|---:|---:|---:|---:|---:|
| present | 10 | 20 | 0 | 0/30 = 0.0% | 30/30 = 100% |
| omitted | 0 | 30 | 0 | 0/30 = 0.0% | 20/30 = 66.7% |
| distorted | 20 | 10 | 0 | **20/30 = 66.7%** | 0/30 = 0.0% |
| no_memory | 0 | 10 | 20 | 0/30 = 0.0% | 20/30 = 66.7% |

**Interpretation.** The P4 behavioral pattern replicates almost exactly:
omission is conservative (0% unauthorized, all confirm), distortion is
dangerous (66.7% unauthorized), and no-memory is cautious. The only difference
from qwen is that gemma made zero unauthorized actions under present status
(qwen: 2/30 conditional collapse errors). The omission/distortion asymmetry is
not a qwen artifact.

## 3. What replicates and what does not

- **Replicates:** chaining vs direct/repeated-direct (writer); omission is
  conservative and distortion is dangerous (agent); source access helps
  relative to memory-only, but less than with qwen.
- **Does not replicate at the same magnitude:** source access nearly
  eliminated omission under qwen (29/30) but only 4/12 here under deterministic
  cues. This needs human labels; it may be a cue-extraction artifact.
- **Over-collection:** the writer run has 30 trajectories instead of the
  pre-registered 12. The primary analysis uses the first 12; the extra 18 are
  exploratory.

## 4. Next

1. Two annotators label the 84-item writer replication set under v3.2.4
   (`results/status_drift_v3_replication_writer/annotation/`, key outside the
   repo).
2. Compare human faithful rates to the qwen writer results.
3. If the source-access difference persists in human labels, report it as a
   model-dependent mitigation effect rather than a general one.
4. Agent replication can be reported now; it does not need annotation.

## 5. Writer human labels (provisional)

84 items, two annotators, v3.2.4. Reliability: primary raw 0.893 / **κ 0.702**
(below the 0.80 gate); identity 1.000 (all PRESERVED); status_expressed 0.917 /
0.550; expressed_status 0.821 / 0.791; action_status 1.000; evidence 0.893 /
0.523. 17 adjudication overrides, model-assisted.

The disagreements are systematic gemma phrasings:

- `已开始 / 进行中` when the dialogue only confirms "will start" → TEMPORAL
  escalation, not NO_DISTORTION;
- `待定 / 未定` as the only cue → CONSIDERING or POSSIBLE, not omission;
- `计划中` for a gold COMMITTED target → CONSIDERING/deflation;
- contradictory `待定 + 已安排`, `到账 + 需满足` → AMBIGUOUS_UNASSESSABLE.

Human faithful (NO_DISTORTION + LUA; all items preserved):

| Condition | Faithful | Omission | Unsupported | Ambiguous |
|---|---:|---:|---:|---:|
| direct | 11/12 = 0.92 | 1/12 | 0/12 | 0/12 |
| recursive | 10/12 = 0.83 | 1/12 | 1/12 | 0/12 |
| rewrite_matched | **7/12 = 0.58** | 1/12 | 2/12 | 2/12 |
| repeated_direct | 11/12 = 0.92 | 1/12 | 0/12 | 0/12 |
| neutral_source | 10/12 = 0.83 | 1/12 | 1/12 | 0/12 |
| status_aware | 11/12 = 0.92 | 1/12 | 1/12 | 0/12 |
| status_aware_source | **12/12 = 1.00** | 0/12 | 0/12 | 0/12 |

**Comparison to qwen.** The writer replication is only partial:

- The rewrite-matched condition is still the worst (0.58), consistent with
  chained re-editing being destructive.
- Recursive is much less destructive in gemma (0.83) than in qwen (0.52);
  gemma's longer, more explicit rewrites may preserve status better.
- Source access alone is weaker in gemma (0.83) than in qwen (1.00).
- `status_aware` is stronger in gemma (0.92) than in qwen (0.90), and the
  combination is best at 1.00.
- The mitigation ranking is therefore **model-dependent**: qwen benefits most
  from source access; gemma benefits more from the status-aware prompt and the
  combination.

**Caveat.** Primary κ 0.702 is below the gate; these writer-side replication
numbers are provisional. The v3.2.5 clarifications below would need a recheck
for a clean claim. The agent replication (§2) does not depend on these labels
and is solid.

## 6. v3.2.5 writer recheck (primary)

The 84 writer items were re-annotated under v3.2.5 (new shuffle, new item ids,
blank files). Reliability:

| Field | Raw | Cohen's κ |
|---|---:|---:|
| proposition_identity | 1.000 | — (all PRESERVED) |
| primary_dimension | 1.000 | 1.000 |
| status_expressed | 1.000 | 1.000 |
| expressed_status | 1.000 | 1.000 |
| action_status | 0.964 | 0.924 |
| evidence_support | 0.952 | 0.850 |
| **primary_judgment** | **0.940** | **0.834** |

The v3.2.5 clarifications removed the gemma-specific disagreements. Five
primary disagreements remained, all `LEGITIMATE_UPDATE` vs `NO_DISTORTION`
(both faithful); 12 adjudication overrides, model-assisted.

Human faithful (NO_DISTORTION + LUA; all items preserved):

| Condition | Faithful | Omission | Unsupported | Ambiguous |
|---|---:|---:|---:|---:|
| direct | 11/12 = 0.92 | 1/12 | 0/12 | 0/12 |
| recursive | 8/12 = **0.67** | 1/12 | 3/12 | 0/12 |
| rewrite_matched | 6/12 = **0.50** | 1/12 | 3/12 | 2/12 |
| repeated_direct | 11/12 = 0.92 | 1/12 | 0/12 | 0/12 |
| neutral_source | 10/12 = 0.83 | 1/12 | 1/12 | 0/12 |
| status_aware | 11/12 = 0.92 | 0/12 | 1/12 | 0/12 |
| status_aware_source | **12/12 = 1.00** | 0/12 | 0/12 | 0/12 |

**Comparison to qwen (writer).**

| Condition | qwen | gemma v3.2.5 |
|---|---:|---:|
| direct | 0.96 | 0.92 |
| recursive | 0.52 | 0.67 |
| rewrite_matched | 0.54 | 0.50 |
| repeated_direct | 0.96 | 0.92 |
| source (neutral) | 1.00 | 0.83 |
| status_aware | 0.90 | 0.92 |
| status_aware_source | 0.93 | 1.00 |

The chain effect now replicates more clearly: recursive and rewrite-matched
are the low conditions, direct and repeated-direct are high. Rewrite-matched
is the worst in gemma (0.50), consistent with chained re-editing. Source access
alone remains weaker in gemma (0.83 vs 1.00), while status-aware and the
combination are at or above the qwen values. The mitigation ranking is still
**model-dependent**: qwen benefits most from source access, gemma from the
status-aware prompt and the combination.

**Conclusion.** The writer replication is confirmed in direction but not in
every magnitude. The agent asymmetry is model-robust. Report the writer
mitigation as model-dependent rather than universal.


