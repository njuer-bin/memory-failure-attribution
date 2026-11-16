# Recursive Status Drift Pilot — Protocol v2.4

**Status:** revised protocol; implementation updated, but this document does not claim a v2.4 model run has occurred.  
**Runner:** experiments/status_drift_recursive_pilot.py  
**Design options:** v2 (crossed design), v3 (crossed design with condition-only final turns)  
**Protocol version emitted by runner:** status_drift_recursive_pilot_v2.4

## 1. Objective and operational definition

Test whether memory transformation changes the epistemic, intentional, or conditional status of an identifiable target proposition without support from later conversational evidence.

A candidate **unsupported status drift** requires all of the following:
1. The target proposition identity is preserved (or sufficiently preserved under a separately reported partial category).
2. The status represented in the memory differs from the gold final status supported by the full dialogue.
3. The difference is not a legitimate, evidence-supported user update.
4. The difference is attributable to the transformation output, not merely to an annotator or judge error.

Do not count proposition omission as status drift. Do not count an evidence-supported change of mind or state as drift.

## 2. Synthetic data design

Design v2/v3 crosses:
- 5 target topics by default;
- 2 trajectory types: stable status and evidence-supported update;
- 3 dimensions: epistemic, intentional, conditional.

This yields 30 trajectories. Current templates use simplified binary states:
- Epistemic: POSSIBLE / CERTAIN.
- Intentional: CONSIDERING / COMMITTED.
- Conditional: CONDITION_ACTIVE / CONDITION_SATISFIED.

These are pilot labels, not a complete ontology. Intentional commitment must not be equated with action execution. Conditional satisfaction must not be inferred from whether the downstream action is considered.

Design v3 changes the final conditional turn to state only condition satisfaction, without restating the downstream action. This reduces one known source of label confounding.

## 3. Experimental conditions

- **Raw:** full original dialogue, no compression.
- **Direct D1/D2/D3/D5:** independently compress the original dialogue using the target depth's character budget.
- **Recursive D1/D2/D3/D5:** compress the full dialogue at D1, then repeatedly compress the previous memory; evaluate at the named depths.
- **Rewrite-matched D1/D2/D3/D5:** repeated rewrite control with the same number of writer calls as the corresponding recursive depth, using the schedule implemented in the runner.

Important: direct, recursive, and rewrite-matched conditions are **not guaranteed to have equal final memory lengths or equal token budgets**. Rewrite-matched controls rewrite-call count more closely; it does not establish token equivalence. Report actual character/byte lengths. Do not interpret differences as a pure recursion effect without a matched-budget follow-up.

## 4. Measurement model

### 4.1 Separate annotation fields

For every output, annotate independently:

- **Topic mention:** lexical appearance of the topic. Weak diagnostic only.
- **Proposition identity:** PRESERVED, PARTIAL, LOST, AMBIGUOUS.
- **Polarity:** POSITIVE, NEGATIVE, MIXED, NOT_APPLICABLE, UNCLEAR.
- **Epistemic status:** POSSIBLE, PROBABLE, CERTAIN, UNKNOWN, EXPLICITLY_UNCERTAIN, NOT_APPLICABLE.
- **Intention status:** NONE, CONSIDERING, INTENDING, COMMITTED, EXPLICITLY_NOT_INTENDED, NOT_APPLICABLE.
- **Action status:** NOT_STARTED, IN_PROGRESS, COMPLETED, ABANDONED, CANCELLED, UNKNOWN, NOT_APPLICABLE.
- **Condition status:** ACTIVE_UNSATISFIED, ACTIVE_UNKNOWN, SATISFIED, INVALIDATED, NOT_APPLICABLE, UNCLEAR.
- **Evidence support:** evidence turn IDs in the original dialogue, or NONE.
- **Unsupported status change:** YES, NO, UNCLEAR.

A single output can preserve the topic while losing the proposition relation. Topic mention must never be substituted for proposition identity.

### 4.2 Metric hierarchy

Report separately, with raw counts and denominators:

1. **Topic Mention Rate** — lexical diagnostic only.
2. **Proposition Identity Retention** — human-adjudicated proportion labelled PRESERVED; report PARTIAL separately.
3. **Status Fidelity** — status matches the dialogue's gold final state, among outputs with proposition identity PRESERVED.
4. **Unsupported Status Drift Rate (primary)** — among outputs with proposition identity PRESERVED, proportion labelled unsupported_status_change=YES.
5. **Omission Rate** — proposition identity LOST; report independently, never hide it in the drift denominator.
6. **Legitimate Update Accuracy** — whether the output follows a later evidence-supported update.
7. **LLM-judge provisional metrics** — diagnostic only, clearly named as judge-derived.

The runner's cpsd_judge_provisional is conditioned on the LLM judge's own proposition_retained flag. It is **not confirmatory CPSD** and must not be used as the primary research result. The lexical status_error_given_topic_mention is also diagnostic only.

The rule-based conditional marker check is a sanity check, not a semantic gold label. Its output is explicitly named condition_marker_heuristic_*.

### 4.3 Human annotation

Use the annotation guide and CSV template in this directory. Two annotators independently label a stratified set of outputs before adjudication. Recommended initial reliability set: all 30 trajectories under Raw, Direct D5, Recursive D5, and (if enabled) Rewrite-matched D5. This yields 120 or 150 items per annotator. Expand to all depths only after the guide is stable.

Calculate agreement separately for proposition identity, each applicable status dimension, and unsupported drift. Use Cohen's kappa for two annotators on nominal labels; report raw agreement and class prevalence as well. If missing labels or more annotators are used, consider Krippendorff's alpha. Do not hide low agreement behind adjudicated scores.

## 5. Implementation safeguards

- Each run writes a canonical configuration fingerprint.
- Resume is refused if the existing configuration fingerprint differs. Use a fresh out-dir for a different design, seed, model, dimension set, limit, writer style, or rewrite-matched setting.
- Per-memory Unicode character and UTF-8 byte lengths are stored. These are not token counts.
- The lexical topic detector is named as topic mention, not proposition retention.
- Judge-derived proposition retention is explicitly marked provisional.
- Recursive-minus-direct deltas are computed as recursive error rate minus direct error rate. Positive values mean recursive has more errors.
- Failed or unparseable judgments must be reported; do not silently count them as correct.

## 6. Recommended commands

Smoke test:
~~~bash
python -m experiments.status_drift_recursive_pilot --design v3 --limit 6 --writer-model qwen2.5:7b --judge-model qwen2.5:7b --out-dir results/status_drift_v2_pilot/v24_smoke
~~~

Full 30-trajectory synthetic pilot:
~~~bash
python -m experiments.status_drift_recursive_pilot --design v3 --limit 30 --writer-model qwen2.5:7b --judge-model qwen2.5:7b --rewrite-matched --out-dir results/status_drift_v2_pilot/v24_full
~~~

Use a separate judge model if available. If writer and judge are the same model, all judge metrics remain exploratory. Preserve raw outputs locally; do not commit private dialogue data.

## 7. Decision gates

The pilot is ready for human review only if:
- all requested trajectories complete without unreported errors;
- resume fingerprint checks work;
- all memory outputs and size diagnostics are present;
- the status labels are applicable and interpretable;
- the annotation guide can distinguish intention from action and condition satisfaction from downstream action.

A phenomenon-level pilot passes only if human-adjudicated examples demonstrate proposition identity preservation alongside unsupported status change, with evidence-turn review. A recursion hypothesis passes only if paired comparisons support it under appropriate budget controls. A null recursion effect is a valid result.

## 8. Limitations

- Synthetic templates have clearer status markers than natural conversation.
- Five topics are not five independent populations; 30 trajectories are not sufficient for broad generalization.
- Character and byte lengths do not guarantee token-matched conditions.
- The runner's LLM judge and lexical/rule-based checks are diagnostics, not human gold.
- No downstream agent action or mitigation claim is tested in this pilot.
- No claim of paper-level novelty follows from passing this pilot.
