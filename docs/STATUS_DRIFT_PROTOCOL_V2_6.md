# Status Drift Pilot — Protocol v2.6 (Topic Expansion to 10)

**Status:** pre-registered; no v2.6 outputs exist yet.
**Branch:** `research/status-drift-v2-pilot`
**Scope:** doubles the topic set from 5 to 10 (30 → 60 trajectories) for the
judge-independent cue measurement. No prompt or label change.

## 1. Why

The current pilot uses 5 topics per dimension (30 trajectories). The chaining
effect is consistent, but 5 topics is a small sample and a single unusual topic
could drive it. Expanding to all 10 predefined topics doubles the sample and
tests whether the effect is topic-general.

## 2. Design

- Design v3 (crossed topic × update, fixed conditional turns), all 10 topics.
- 3 dimensions × 10 topics × 2 variants = **60 trajectories**.
- Writer styles: neutral and status-aware (separate runs).
- `--skip-judge`, no model judging for this stage. Primary metrics are
  judge-independent.

## 3. Metrics

- Deterministic status-cue state for updated cases
  (`evaluation.status_cue_metrics`): MATCH / MIXED / OPPOSITE / ABSENT by
  dimension, condition, and depth.
- Deterministic proposition omission.
- Deterministic condition omission.
- Per-topic cue-loss counts, to check that no single topic dominates the effect.

Report raw counts and denominators. No significance tests.

## 4. Pre-registered reading

- The chaining effect is topic-general if, in both writers, direct ABSENT stays
  low (0–2 of 20 updated cases per depth) and recursive D3/D5 ABSENT is
  clearly higher.
- The status-aware mitigation is topic-general if it reduces recursive cue loss
  relative to neutral across the 10 topics, not just in aggregate.
- If one or two topics account for most of the effect, report that explicitly
  and narrow the claim.

## 5. Gates

Interpret only if:

- all 60 trajectories complete and parse;
- deterministic proposition omission < 10%;
- no single topic contributes more than half of all cue-loss cases;
- the direct-versus-recursive pattern is present in both writers.

If a gate fails, report the failure and do not aggregate as a topic-general
effect.

## 6. Integrity

- Existing 30-trajectory outputs are unchanged.
- New runs go to separate directories.
- No judge is used to rescue a null cue-level result.
- Private/synthetic data only; the templates are synthetic.
