# 2026-10-11 — LoCoMo-Refined n=50 post-fix validation and provenance gate plan

## 1. Engineering progress recorded

The following evaluator fixes are now implemented and locally verified:

- benchmark timestamp parsing for strings such as `1:56 pm on 8 May, 2023`;
- relative temporal answer equivalence rules including `last week`, relative weekdays, `last weekend`, and `two days ago`;
- evidence-gate contradiction handling for judge reasons such as `does not mention`, `does not specify`, and `does not establish`;
- evidence schema compatibility between trace `text` and artifact `content`.

Verification checkpoint:

- targeted tests: 20 passed;
- full repository tests: 33 passed.

These are engineering validations, not evidence that all remaining answer failures are reasoning failures.

## 2. Latest LoCoMo-Refined n=50 validation

Command:

```text
G:\\aconda\\python.exe -u -m experiments.run_oracle_experiments --dataset locomo_refined_public --limit 50
```

Result:

- records: 50
- errors: 0
- Real Memory accuracy: 1/50 = 0.02
- Oracle Memory accuracy: 30/50 = 0.60
- Oracle Context accuracy: 30/50 = 0.60
- Real Memory lifecycle recall: formation 0.885, storage 0.98, evolution 0.885, retrieval 0.8183333333, rerank 0.7533333333, context 0.44
- Real Memory first-loss distribution: none 20, retrieval 8, rerank 2, context 13, formation 7
- Evidence Gate: sufficient 46, insufficient 4
- First answer-failure distribution: F6 18, E0 4, F4 8, F5 13, F1 6

Compared with the preceding n=50 checkpoint, Oracle Memory/Context accuracy increased from 38% to 60%, while lifecycle recall stayed unchanged. F6 decreased from 19 to 18 and E0 increased from 3 to 4.

## 3. Interpretation status

### Confirmed

1. The latest evaluator changes are compatible with the full experiment and produce 50/50 completed records with zero execution errors.
2. Temporal scoring changes materially affect answer evaluation: Oracle Memory/Context moved from 19/50 to 30/50 on this rerun.
3. Lifecycle evidence recall is unchanged by the scorer changes.
4. The Real Memory context stage remains the largest lifecycle evidence-loss point in this n=50 sample at 0.44 recall.
5. The current 18 raw F6 cases must not be interpreted as 18 confirmed reasoning failures.

### Not yet confirmed

- The truth of LoCoMo Gold Evidence provenance against MemoryEngine internal turn IDs.
- The proportion of genuine F6 reasoning failures after the latest scorer/gate changes.
- Whether the current E0=4 cases are all legitimate evidence insufficiency cases.

## 4. Critical methodological gate before scaling

Do **not** run n=100/n=500 yet.

The next required step is a single-sample LoCoMo end-to-end provenance gate, preferably `conv-26#q0000`, that verifies the full chain:

`raw LoCoMo conversation -> normalized sessions/turns -> MemoryEngine Add -> stored raw provenance -> semantic memory provenance -> retrieval/rerank/context artifacts -> Gold Evidence matching`

The gate must explicitly check:

- `session_id`
- benchmark `dia_id` / turn identity
- generated engine turn identity
- speaker/role
- raw message text
- normalized message text
- Gold Evidence text
- Gold Evidence resolution status
- provenance alignment at formation/storage/evolution/retrieval/rerank/context

The gate should fail loudly if a Gold Evidence item is unresolved or if its provenance points to a different message/session.

## 5. Research protocol rule

Until the provenance gate passes, the n=50 numbers are treated as **protocol-validation results**, not final benchmark claims.

After provenance passes, the planned order is:

1. freeze the evaluation protocol;
2. manually annotate 20–30 cases and measure agreement (preferably Cohen's kappa);
3. run LoCoMo at n>=100;
4. run LongMemEval at n>=100;
5. bootstrap confidence intervals;
6. run lexical-anchor ablation;
7. prepare case studies and limitations.

## 6. Attribution definition retained

The project attributes the **earliest blocking lifecycle loss**, not every concurrent downstream loss. F4 intentionally covers both retrieval and rerank. E0 is evaluated before F1–F6 against the benchmark reference answer and Gold Evidence. F6 requires sufficient evidence, all Gold Evidence reaching final context, and an incorrect benchmark-scored answer.

This checkpoint records both the completed engineering progress and the decision to stop scaling until provenance is independently validated.
