# V3 P5 Mitigation Pilot — Protocol

**Status:** pilot protocol for protocol development, not a confirmatory result.
12 trajectories × 6 writer strategies; same chained budget schedule. Deterministic
diagnostics only; blind human annotation is a separate follow-up.

## 1. Trajectories

12 P2 trajectories: the first 2 topics (`换一份工作`, `开始健身`) × 2 update
variants × 3 dimensions = 4 per dimension (2 stable, 2 updated).

## 2. Strategies

All strategies use the same 5-stage chain: 220 → 180 → 140 → 120 → 100
characters. Source access is recorded and differs by design.

| Strategy | Prompt | Source access | Verification |
|---|---|---|---|
| `neutral` | neutral summary | previous memory only | none |
| `status_aware` | preserve proposition, certainty, intent strength, condition | previous memory only | none |
| `unknown_heavy` | write `状态不明` when no explicit status; do not guess | previous memory only | none |
| `source_peek` | neutral summary | previous memory + original dialogue | none |
| `evidence_anchored` | preserve status and append `（依据：Turn X）` | previous memory + original dialogue | none |
| `transition_verification` | neutral write, then a verifier corrects the status against the original dialogue | previous memory; verifier sees original dialogue | one verifier call per stage |

## 3. Prompts

- `neutral` and `status_aware`: existing `writer_prompt`.
- `unknown_heavy`: "保留命题和条件；如果输入没有明确状态，写‘状态不明’，不要猜测；不要输出解释。"
- `evidence_anchored`: "保留命题、确定性和条件状态；在记忆末尾用（依据：Turn X）标注支持该状态的轮次；不得改变状态；不要输出解释。"
- `transition_verification` verifier: "你是状态核对员。根据原始对话核对记忆是否保留命题、确定性和条件状态。若丢失或改变，按原文修正；否则原样返回。只输出记忆。"

## 4. Outcomes (deterministic, diagnostic)

- Status-cue state: `MATCH` / `MIXED` / `OPPOSITE` / `ABSENT` for epistemic and
  intentional; `SATISFIED` / `ACTIVE` / `AMBIGUOUS` / `OMITTED` for conditional.
- Topic mention (weak proposition proxy).
- Final characters and eval tokens; budget inflation vs neutral.
- Abstention marker rate (`状态不明` / `不确定` / `无法判断`).
- All intermediate memories retained.

These are **not** human status-fidelity labels. No mitigation success claim is
made from the pilot.

## 5. Gates

- 12/12 trajectories, 6/6 strategies complete.
- No silent generation failures; errors logged.
- Report budget inflation; flag any strategy above 1.5× the neutral mean.
- Report abstention rate; `unknown_heavy` is expected to be high and is a
  trivial-abstention control.

## 6. Analysis

Per strategy and dimension: cue-state counts, topic mention, mean characters,
mean eval tokens, abstention rate. Compare each strategy to neutral with counts
and descriptive differences; no inferential claims at n=12.

## 7. Follow-up

If a strategy looks promising on deterministic diagnostics, build a blind
annotation set from the final memories and label it under v3.2.3. Do not pool
the pilot with P2/P3/P4 or v2.x.
