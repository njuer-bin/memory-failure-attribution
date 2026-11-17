# V3 P4 Downstream Behavioral Result (2026-11-17)

**Design:** 30 P2 trajectories × `present` / `omitted` / `distorted` memory
variants + `no_memory` reference; sandboxed assistant chooses
`PROCEED` / `CONFIRM` / `ABSTAIN` / `OTHER`. Frozen in `V3_P4_FREEZE.md`.
**Completeness:** 30/30 trajectories, 120/120 items, 0 parse failures,
0 errors.
**Agent:** `qwen2.5:7b`, temperature 0, seed 42.

## 1. Action distribution

| Variant | PROCEED | CONFIRM | ABSTAIN | OTHER |
|---|---:|---:|---:|---:|
| present | 12 | 18 | 0 | 0 |
| omitted | 0 | 30 | 0 | 0 |
| distorted | 20 | 10 | 0 | 0 |
| no_memory | 0 | 13 | 17 | 0 |

## 2. Rates

| Variant | Unauthorized | Memory-consistent | Evidence-consistent | Clarify | Abstain |
|---|---:|---:|---:|---:|---:|
| present | 2/30 = 6.7% | 28/30 = 93.3% | 28/30 = 93.3% | 60.0% | 0.0% |
| omitted | 0/30 = 0.0% | 30/30 = 100% | 20/30 = **66.7%** | 100% | 0.0% |
| distorted | 20/30 = **66.7%** | 30/30 = 100% | 0/30 = **0.0%** | 33.3% | 0.0% |
| no_memory | 0/30 = 0.0% | 30/30 = 100% | 20/30 = 66.7% | 43.3% | 56.7% |

## 3. Paired contrasts

Trajectory-level paired differences, cluster bootstrap 95% CI (10,000
resamples).

| Contrast | Outcome | Difference | 95% CI |
|---|---|---:|---|
| omitted vs present | unauthorized | −0.067 | [−0.167, 0.000] |
| omitted vs present | evidence-consistent | −0.267 | [−0.467, −0.067] |
| omitted vs present | memory-consistent | +0.067 | [0.000, 0.167] |
| distorted vs present | unauthorized | **+0.600** | [0.433, 0.767] |
| distorted vs present | evidence-consistent | **−0.933** | [−1.000, −0.833] |
| distorted vs present | memory-consistent | +0.067 | [0.000, 0.167] |
| no_memory vs present | unauthorized | −0.067 | [−0.167, 0.000] |
| no_memory vs present | evidence-consistent | −0.267 | [−0.467, −0.067] |

## 4. By dimension

Unauthorized / evidence-consistent:

| Dimension | present | omitted | distorted | no_memory |
|---|---|---|---:|---:|---:|
| epistemic | 0/10 / 1.00 | 0/10 / 0.50 | 5/10 / 0.00 | 0/10 / 0.50 |
| intentional | 0/10 / 1.00 | 0/10 / 0.50 | 5/10 / 0.00 | 0/10 / 0.50 |
| conditional | 2/10 / 0.80 | 0/10 / 1.00 | 10/10 / 0.00 | 0/10 / 1.00 |

## 5. Interpretation

1. **Status omission is behaviorally conservative, not dangerous.** With no
   status in memory, the agent always asks (`CONFIRM`) and never acts without
   authorization. The cost is **under-action**: evidence-consistent actions
   fall by 26.7 percentage points, concentrated in established/committed
   statuses where `PROCEED` is appropriate. For conditional items, where the
   correct action is never to proceed without confirmation, omission costs
   nothing on this task.
2. **Status distortion is behaviorally harmful.** It flips the action in the
   direction of the distorted status: 66.7% unauthorized actions, a +60-point
   paired increase over present. The agent is memory-consistent (it follows the
   distorted memory) but evidence-inconsistent.
3. **The two failure modes are not interchangeable.** P3 found omission to be
   the dominant memory failure (44–54% of preserved outputs) and distortion
   rare (0.9%). P4 shows the dominant failure is the safer one behaviorally,
   while the rare failure is the dangerous one. Reports must separate them.
4. **Conditional present is fragile even without distortion.** 2/10 present
   conditional memories (condition satisfied, action only considering) were
   read as decided and produced `PROCEED`. This is a conditional-collapse error
   in the agent, not a memory-generation error.
5. **No-memory is a cautious baseline.** 0/30 unauthorized, 13 `CONFIRM`,
   17 `ABSTAIN`. The omitted-status result is not an artifact of having no
   information; omitted memories still contain the proposition.

## 6. Gate verdict

**P4 gate: PASS.** The status-only intervention produces a large, interpretable
behavioral difference for distorted status (+60 points unauthorized), and a
null-on-unauthorized but clear under-action effect for omitted status
(−26.7 points evidence-consistent). Report both, not a single "drift" effect.

## 7. Limitations

- One agent model (`qwen2.5:7b`), one scenario per trajectory, 30 trajectories;
  no power claim.
- Synthetic templates; the request explicitly states the decision rule, which
  makes the task a clean status-reading probe but may overstate clarification.
- `OTHER` was 0/120; parsing succeeded on all items.
- Sandboxed only; no real actions.
- P4 is not pooled with P2/P3 or v2.x.
- The conditional present error (2/10) is a model behavior, not a memory
  manipulation; report separately.

## 8. Next

1. Update the paper narrative: omission is the dominant memory failure but the
   safe one; distortion is rare but behaviorally dangerous.
2. P5 mitigation: status-aware / evidence-anchored / transition verification,
   scored on both omission and distortion.
3. Consider a second agent model and a second scenario per trajectory as
   replication, not part of the primary contrast.
