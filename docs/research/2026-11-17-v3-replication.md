# V3 Second-Model Replication — gemma3:12b (2026-11-17)

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
