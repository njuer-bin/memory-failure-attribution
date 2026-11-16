# V3 P1a — Path-Replicate Existence Check (2026-11-16)

**Protocol:** `docs/research/V3_RESEARCH_ROADMAP.md` §7 P1a
**Runner:** `experiments/v3_path_pilot.py`
**Run:** neutral writer, qwen2.5:7b, 12 trajectories (3 dimensions × 2 topics ×
stable/update), 3 intermediate schedules + direct reference, final budget 100.
**Output:** `results/status_drift_v2_pilot/v3_path_pilot/`
**Status:** completed; 12/12, 0 errors.

## 1. Schedules

All paths share the same source and the same final budget (100 characters); only
the intermediate budget schedule differs:

- A: 220 → 180 → 140 → 120 → 100
- B: 220 → 200 → 160 → 130 → 100
- C: 220 → 160 → 150 → 120 → 100
- Direct: one compression to 100.

## 2. Headline result

| Metric | Value |
|---|---:|
| Trajectories | 12 |
| Mean pairwise path disagreement | **0.056** |
| Trajectories with any path divergence | **1 / 12** |
| Mean direct-vs-paths disagreement | **0.347** |

By dimension:

| Dimension | Mean path disagreement | Any divergence |
|---|---:|---:|
| epistemic | 0.167 | 1 / 4 |
| intentional | 0.000 | 0 / 4 |
| conditional | 0.000 | 0 / 4 |

**Path-to-path divergence is rare; direct-vs-chained divergence is common.**

## 3. The one divergent case

`epistemic_01_U` (gold CERTAIN; dialogue: `我已经确认会去上海工作`):

- Path A (`220→180→140→120→100`):
  `上海工作，天气多变，整理日程，处理作业事务。` → cue ABSENT.
- Path B (`220→200→160→130→100`):
  `上海工作确认，整理日程，处理作业，关注天气。` → CERTAIN.
- Path C (`220→160→150→120→100`):
  `上海工作确认，整理日程，处理作业，关注天气。` → CERTAIN.
- Direct: `确认去上海工作，天气多变…` → CERTAIN.

So the intermediate schedule can decide whether the confirmation cue survives.
This is a genuine path-dependence instance, not a metric artifact.

## 4. Interpretation

- **Path dependence exists but is rare under the tested schedule space.** One of
  twelve trajectories changes status across paths with the same source and final
  budget.
- **The dominant contrast is direct vs chained, not path-to-path.** Direct
  preserves the status cue far more often than any chained path (mean
  disagreement 0.347); path A/B/C usually converge to the same state.
- The current path space is narrow: it varies only intermediate character
  budgets. It does not vary source access, prompt phrasing, decoding
  temperature/seed, or intermediate order.

## 5. Gate verdict (roadmap go/no-go #0)

- Is there within-condition path divergence at all? **Yes, but rare (1/12).**
- Is "path-dependent" supported as a general claim at this scale? **No.**
- The result supports a **transformation-history (direct vs chained) effect**
  with path dependence as a secondary, rare phenomenon.

**Verdict: do not title or claim a broad path-dependence effect yet.** Broaden
the path space or reframe the primary claim.

## 6. Next

1. Broaden the path perturbation space:
   - intermediate budget order (not only magnitude);
   - prompt paraphrase across paths;
   - source access (memory-only vs memory+source);
   - decoding temperature/seed.
2. Run a larger path pilot (e.g., 40 trajectories × 5 paths) after freezing the
   path definition.
3. If divergence remains rare, reframe V3 as a **transformation-history effect**
   study, with path dependence reported as an exploratory secondary result.

## 7. Limitations

- n=12; 2 topics; one writer model; deterministic cue metric.
- Topic mention is a weak proposition proxy; one conditional path was
  topic-lost and excluded.
- The schedules are similar by design; this is a narrow path space.
- No human labels in this pilot.
