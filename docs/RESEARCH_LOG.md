## Historical progress — before 2026-10-08

### Phase 1 — Research direction and system framing

The project started from the observation that long-term agent memory failures are usually discussed as a single retrieval problem. The research question was reframed as:

> When an agent answers incorrectly, where in the memory lifecycle was the required information lost?

The initial lifecycle decomposition was:

Conversation → Formation → Storage → Evolution → Retrieval → Reranking → Context → LLM

This led to the initial five-stage failure taxonomy:

- F1 Formation Failure — information exists in raw conversation but is not converted into usable semantic memory.
- F2 Storage Failure — extracted memory is not correctly persisted or cannot be recovered.
- F3 Evolution Failure — updates, conflicts, stale information, or temporal changes are handled incorrectly.
- F4 Retrieval Failure — required information exists in memory but is not retrieved.
- F5 Context Failure — retrieved evidence is lost, truncated, or otherwise unavailable to the final model.

A central methodological decision was to attribute a failure to the earliest stage where required evidence becomes unavailable, rather than simply labeling every wrong answer as a retrieval failure.

### Phase 2 — Reusing and extending the agent_memory infrastructure

The memory engine was ported from the AML-oriented njuer-bin/agent_memory project into this research repository.

The reusable engine includes raw conversation storage, atomic fact extraction, entity/relationship memories, timeline/event memories, rule memories, user profiles, hybrid retrieval, reranking, provenance-aware storage, query analysis, and multi-hop support.

The research fork deliberately separates the memory system implementation from the failure diagnosis layer.

### Phase 3 — Provenance tracing

A major engineering problem was that memory artifacts originally did not provide sufficiently precise provenance for lifecycle attribution.

The project therefore added provenance fields connecting:

raw message → semantic memory → retrieval candidate → reranked candidate → final context

Important provenance identifiers include source_raw_id, source_session_id, source_turn_id, and turn_id.

The turn-level provenance matcher was later tightened so that an exact turn identifier takes precedence over session identity. This prevents repeated utterances in the same session from being incorrectly attributed to the wrong turn.

This was a methodological improvement, not merely an implementation detail: reliable failure attribution requires evidence identity to survive the entire pipeline.

### Phase 4 — LongMemEval adapter and evidence normalization

A LongMemEval adapter was added to normalize benchmark evidence into a common internal representation containing evidence ID, evidence text, source/session information, turn ID, timestamp, and role where available.

Gold evidence can therefore be traced through the lifecycle independently of the underlying benchmark format.

### Phase 5 — Formation diagnostics

The first version of formation attribution produced misleading results because the analyzer was initially designed around Chinese-language patterns while LongMemEval contains English conversations.

The project explicitly identified this as a language coverage confound, rather than treating the initial F1 failures as scientific evidence.

Basic English formation patterns were then added for common LongMemEval facts including degree, school, residence, workplace, occupation, likes/dislikes, birthday, name, language, origin, common interpersonal relations, simple rules/preferences, and common life events.

Formation diagnostics were made more explicit by comparing the Gold Evidence turn, semantic memories extracted from the same turn, and semantic memories from the same session.

The diagnostic distinguishes FORMATION_OK, F1a_EXTRACTOR_MISS, F1c_REPRESENTATION_MISMATCH, and F1d_UNKNOWN.

This made F1 measurement more interpretable and prevented benchmark-language limitations from being mistaken for memory failures.

### Phase 6 — Lifecycle stage tracing

The search pipeline was instrumented to expose separate boundaries: retrieval candidates, pre-rerank candidates, reranked candidates, and final context.

This enabled stage-specific evidence matching instead of treating the search result as a single opaque operation.

The lifecycle evaluator then computed stage evidence recall, first-loss stage, and first-loss failure type.

The initial failure mapping was intentionally conservative: formation → F1; storage → F2; evolution → F3; retrieval/rerank → F4; context → F5.

### Phase 7 — Oracle control design

The project introduced three controlled experimental conditions:

1. Real Memory — real conversation is ingested into the memory system and queried normally.
2. Oracle Memory — Gold Evidence is injected or bypassed into the memory-side pipeline to estimate the downstream evidence ceiling.
3. Oracle Context — Gold Evidence is supplied directly to the final answer context, bypassing the memory lifecycle.

The purpose is not to claim that oracle conditions are realistic systems. They are controls for isolating where failures originate.

The core comparison became: Real Memory vs Oracle Memory vs Oracle Context.

### Phase 8 — First evidence-only oracle experiment

Before answer scoring was added, a 10-sample LongMemEval oracle experiment was run successfully.

Results: 10 records, 0 errors, and all 10 samples had evidence-level recall of 1.00 across Formation, Storage, Evolution, Retrieval, Rerank, and Context in the Real Memory condition. First-loss distribution was none: 10. Oracle Memory also preserved all Gold Evidence through its measured downstream stages.

At this stage the project explicitly did not claim answer accuracy. The experiment was correctly described as an evidence-availability control.

This distinction was important because evidence recall and answer correctness are different quantities.

### Phase 9 — Engineering reliability and reproducibility

The repository accumulated regression-oriented improvements around provenance persistence, turn-level evidence identity, LongMemEval role preservation, lifecycle search tracing, oracle experiment output, answer-generation configuration, and local Ollama integration.

Experiment outputs were standardized into comparison.jsonl for per-question traces and summary.json for aggregate metrics.

The repository README was updated throughout the process so the research motivation, architecture, experiment design, and current status remain synchronized with the implementation.

### Overall evolution of the research question

Initial: Where is information lost in a long-term agent memory system?

After lifecycle tracing: At which memory lifecycle boundary does the first loss of required evidence occur?

After oracle controls: Can controlled evidence injection distinguish memory-induced failures from downstream failures?

Current: Across the memory-to-reasoning lifecycle, where does a long-term agent fail, and how can evidence loss be distinguished from answer failures that persist despite complete evidence availability?

This is an extension of the original research direction, not a replacement of it.

# Research Progress Log

This file records reproducible research progress, experimental observations, methodological decisions, and caveats for later paper writing.

## 2026-10-08 — First answer-level failure attribution result

### Research question

The project originally focused on locating where required evidence is lost in the long-term memory lifecycle. The current framework extends this into a broader **memory-to-reasoning failure attribution** problem:

> When a long-term agent gives a wrong answer, did the failure arise because evidence was lost during the memory lifecycle, or did the evidence reach the final context and the downstream reasoner still fail?

The current lifecycle is:

    Conversation
      ↓
    Formation
      ↓
    Storage
      ↓
    Evolution
      ↓
    Retrieval
      ↓
    Reranking
      ↓
    Context
      ↓
    Reasoning
      ↓
    Answer

Failure taxonomy:

- F1 — Formation Failure
- F2 — Storage Failure
- F3 — Evolution Failure
- F4 — Retrieval Failure
- F5 — Context Failure
- F6 — Reasoning Failure

### Experiment

Command:

    G:\aconda\python.exe -u -m experiments.run_oracle_experiments --dataset longmemeval_s_sample10 --limit 10

Dataset: `longmemeval_s_sample10`

Samples: 10

Successful records: 10

Errors: 0

Total runtime: 1295.97 s

Answer model: local Ollama `qwen2.5:7b`

Answer scoring:

- exact match OR token F1 >= 0.5
- deterministic scoring; no LLM judge

### Evidence lifecycle result

For Real Memory:

| Stage | Recall |
|---|---:|
| Formation | 1.00 |
| Storage | 1.00 |
| Evolution | 1.00 |
| Retrieval | 1.00 |
| Rerank | 1.00 |
| Context | 1.00 |

First-loss distribution:

    none: 10

Oracle Memory produced the same 1.00 evidence recall at all measured downstream stages.

Oracle Context intentionally bypasses the earlier evidence stages and supplies Gold Evidence directly to the final context.

### Answer result

| Mode | Correct | Accuracy | Exact Match | Token F1 |
|---|---:|---:|---:|---:|
| Real Memory | 7/10 | 0.70 | 0.40 | 0.6813 |
| Oracle Memory | 5/10 | 0.50 | 0.40 | 0.5808 |
| Oracle Context | 5/10 | 0.50 | 0.40 | 0.5808 |

Model errors: 0 in all three modes.

The preliminary answer-level attribution reported:

    F6_REASONING: 3

### Interpretation

The key observation is that **evidence preservation and answer correctness are not equivalent**.

In these 10 samples, all required Gold Evidence was observed through every measured lifecycle stage in the Real Memory condition, yet only 7/10 answers were classified as correct by the current deterministic scoring rule. Three incorrect cases were therefore candidates for F6 because their required evidence was available through final context.

Oracle Context also achieved only 5/10 under the current scoring protocol. This provides an important control: some failures persist even when Gold Evidence is supplied directly to the answer model.

The unexpected ordering

    Real Memory > Oracle Memory = Oracle Context

should **not** be interpreted as evidence that the real memory system is better than oracle memory. With only 10 samples, possible explanations include additional useful context in the real condition, answer-generation variance, benchmark/reference-answer effects, context-format effects, or limitations of the current token-F1 correctness criterion. This requires per-example inspection before drawing conclusions.

### Methodological significance

The research direction remains consistent with the original thesis, but is now broader:

> **From Memory Formation to Reasoning: Diagnosing Information Loss and Answer Failure Across the Long-Term Agent Lifecycle**

The contribution is a diagnostic framework rather than a claim that one particular retriever or memory architecture is universally superior.

The oracle controls provide a way to separate:

1. failures caused by missing evidence in the memory lifecycle; and
2. failures that remain when evidence is directly available to the reasoner.

### Important caveats

1. `n=10` is a preliminary sanity-check experiment, not a statistically reliable benchmark result.
2. The current answer metric is exact match OR token F1 >= 0.5. It is a first reproducible scoring protocol and requires calibration against LongMemEval answer semantics.
3. F6 should currently be described as an operational/candidate attribution under this scoring protocol, not as a universally proven cognitive reasoning failure.
4. The English analyzer provides basic LongMemEval formation coverage and is not a comprehensive semantic parser.
5. The experiment demonstrates evidence-level preservation on this sample; it does not imply 100% lifecycle performance on LongMemEval as a whole.

### Next experiments

1. Inspect all 10 examples at the question/reference/prediction/evidence level.
2. Specifically inspect the 3 candidate F6 cases.
3. Explain the Real Memory > Oracle Context anomaly before scaling.
4. Calibrate answer scoring and threshold.
5. Run a larger LongMemEval sample (50–100+).
6. Add LoCoMo or another complementary long-term memory benchmark.
7. Produce failure-attribution tables, oracle gaps, and confidence intervals for the paper.

### Paper-ready takeaway

A useful current formulation is:

> Long-term agent failures should not be treated solely as retrieval failures. Even when required evidence survives the memory lifecycle and reaches the final context, the answer can still be incorrect. Oracle controls therefore allow memory-induced evidence loss to be separated from downstream answer failures.

This statement is a preliminary research observation and should be validated on larger samples before being presented as a general empirical claim.

## 2026-10-08 — Answer-evaluation calibration: lexical mismatch identified

### Post-hoc inspection

The first 10-sample answer experiment was inspected at the question, Gold Evidence, prediction, and score level.

Three cases were initially classified as F6_REASONING:

- 51a45a95 — “Where did I redeem a $5 coupon on coffee creamer?”
- 58bf7951 — “What play did I attend at the local community theater?”
- f8c5f88b — “Where did I buy my new tennis racket from?”

The inspection showed that the lexical scorer can produce false answer failures.

For 58bf7951, the evidence states that the play was *The Glass Menagerie*, and the model answered “The Glass Menagerie.” The answer is semantically supported, but its token F1 against a longer benchmark-style reference was only 0.36.

For f8c5f88b, the evidence states that the racket was obtained from a sports store downtown, and the model answered “From a sports store downtown.” The answer is semantically supported, but its token F1 was only 0.44.

For 51a45a95, the question asks “Where,” while the available Gold Evidence only states “last Sunday.” This case remains a genuine candidate for downstream answer failure or benchmark/evidence alignment error and requires semantic evaluation.

### Methodological change

The project therefore separates answer evaluation into two layers:

1. Lexical metrics — Exact Match and Token F1, retained for reproducibility.
2. Semantic correctness — an independent judge evaluates whether the candidate answer correctly answers the question and is supported by Gold Evidence without requiring lexical overlap with a long reference sentence.

The revised attribution rule is:

> F6 is only a candidate when all required evidence reaches the final context and semantic answer evaluation judges the answer incorrect.

This prevents lexical reference mismatch from being automatically converted into a reasoning failure.

### New implementation

Added:

- evaluation/answer_semantic_eval.py
- experiments/semantic_calibration.py

The calibration experiment is post-hoc: it reads the existing comparison.jsonl and does not rebuild memory or rerun answer generation.

Command:

    G:\aconda\python.exe -u -m experiments.semantic_calibration

Outputs:

- results/oracle_experiments/comparison_semantic.jsonl
- results/oracle_experiments/semantic_summary.json

### Scientific significance

This result reveals an important methodological dependency:

> Failure attribution is only as reliable as the answer evaluation layer used after evidence tracing.

The current framework therefore distinguishes:

    Evidence Availability
            +
    Semantic Answer Correctness
            ↓
    Failure Attribution

This is a refinement of the original research protocol rather than a change of research direction.

### Current status

The original 3 F6 cases are no longer treated as confirmed reasoning failures. They are retained as F6 candidates pending semantic calibration.

The next experimental gate is semantic calibration on the existing 10 samples. Only after this protocol is stable should larger LongMemEval experiments be run.


## 2026-10-08 — Semantic calibration revealed evaluator and evidence-sufficiency confounds

The 10-sample semantic calibration exposed a second layer of attribution risk: an LLM semantic judge can itself produce false-negative verdicts, and some benchmark Gold Evidence does not fully answer the exact question.

The four apparent F6 candidates were manually inspected:

| ID | Initial semantic verdict | Calibrated interpretation |
|---|---|---|
| e47becba | Incorrect | Evaluator false negative. The candidate "Business Administration" directly answers "What degree did I graduate with?" and the Gold Evidence explicitly states a degree in Business Administration. |
| 58bf7951 | Incorrect | Evaluator false negative. The candidate identifies The Glass Menagerie, exactly matching the Gold Evidence. |
| 6ade9755 | Incorrect | E0 Evidence/Question Mismatch. The evidence mentions Serenity Yoga but does not explicitly establish that the user takes yoga classes there. |
| 58ef2f1c | Incorrect | E0 Evidence/Question Mismatch. The evidence describes volunteering at the "Love is in the Air" fundraising dinner on Valentine's Day, while the question asks about a local animal shelter fundraising dinner. |

Therefore the initial four F6 candidates contain 0 confirmed F6 reasoning failures in this 10-sample calibration.

### Protocol revision

The answer-level attribution protocol was revised from:

    semantic incorrect + evidence reaches context -> F6 candidate

to:

    semantic evaluation
          ↓
    evidence sufficient?
       ├── no  -> E0_EVIDENCE_INSUFFICIENT
       └── yes
             ↓
       evidence reaches context?
       ├── no  -> F1–F5
       └── yes
             ↓
       semantically incorrect with non-low confidence
             -> F6_REASONING_CANDIDATE

An additional EVAL_SEMANTIC_UNCERTAIN category is used when the semantic evaluation itself cannot support a stable attribution.

### Semantic judge robustness

The semantic evaluator now returns:

- correct
- evidence_sufficient
- confidence
- reason
- adjudication

A conservative lexical-anchor adjudicator repairs only obvious semantic-judge false negatives when:

1. the judge says the evidence is sufficient;
2. the judge confidence is not low; and
3. the candidate contains a meaningful exact phrase shared with the evidence.

This specifically protects against errors such as:

- "Business Administration" being judged as not specifying the degree;
- "The Glass Menagerie" being judged as a different play.

The lexical-anchor rule is deliberately not applied when evidence is insufficient, so cases such as "Serenity Yoga" are not incorrectly promoted to correct answers merely because the entity name appears in the evidence.

### New attribution categories

The current protocol distinguishes:

- F1_FORMATION
- F2_STORAGE
- F3_EVOLUTION
- F4_RETRIEVAL
- F5_CONTEXT
- F6_REASONING_CANDIDATE
- E0_EVIDENCE_INSUFFICIENT
- EVAL_SEMANTIC_UNCERTAIN

This is a methodological improvement: answer failure, evidence insufficiency, and reasoning failure are no longer conflated.

### Current scientific conclusion

The 10-sample experiment does not yet demonstrate a confirmed F6 reasoning failure.

Instead, it demonstrates two important methodological facts:

1. lexical and LLM-based answer evaluation can both create attribution artifacts;
2. Gold Evidence must be checked for sufficiency against the exact question before a downstream reasoning failure can be claimed.

This strengthens the research framing:

> Memory-to-reasoning failure attribution requires both lifecycle evidence tracing and an explicit answer-evaluation/evidence-sufficiency layer.

The experiment should remain at n=10 until this revised protocol is rerun and inspected. Only then should LongMemEval be scaled to 50–100+ samples.


## 2026-10-08 — Semantic calibration protocol stabilized on n=10

The revised 10-sample calibration was rerun after strengthening the evidence-sufficiency adjudication rule.

Command:

    G:\\aconda\\python.exe -u -m experiments.semantic_calibration

Results:

- records: 10
- semantic evaluation errors: 0
- F6 candidates: 0
- E0 evidence-insufficiency cases: 1
- evaluation-uncertain cases: 0

Real Memory: semantic correct 9/10; semantic incorrect 1/10; F6 candidates 0; E0 cases 1.

Oracle Memory: semantic correct 10/10; semantic incorrect 0/10.

Oracle Context: semantic correct 9/10; semantic incorrect 1/10.

The remaining non-correct case is 58ef2f1c, which is now correctly classified as E0 rather than F6. Its Gold Evidence describes volunteering at the “Love is in the Air” fundraising dinner on Valentine’s Day, while the question asks about a local animal shelter fundraising dinner. The evidence therefore does not establish the requested event.

### Protocol outcome

The revised calibration successfully removed the four previously observed false F6 pathways: two semantic-judge false negatives were repaired by the narrow lexical-anchor adjudicator, and two evidence/question mismatches were prevented from becoming F6 through the evidence-sufficiency guard.

The current 10-sample protocol therefore produces:

    F6_REASONING_CANDIDATE = 0
    E0_EVIDENCE_INSUFFICIENT = 1
    EVAL_SEMANTIC_UNCERTAIN = 0

This is the first stable calibration point for the revised attribution protocol.

### Important interpretation

The result does not mean that the memory system is perfect or that reasoning failures do not exist. It means only that this 10-sample calibration set contains no case that currently satisfies all conditions required for a conservative F6 attribution.

The difference between Real Memory 9/10 and Oracle Memory 10/10 should not yet be interpreted as a quantified memory failure rate. The sample is too small, and the E0 case highlights that benchmark evidence quality itself can affect answer-level scoring.

Oracle Context remains 9/10 because the same E0 benchmark/evidence mismatch is still present when Gold Evidence is passed directly to the answer model. This is expected under the current protocol: Oracle Context is a control for memory-side evidence loss, not a repair mechanism for deficient Gold Evidence.

### Research gate

The semantic calibration gate is now passed at n=10:

1. lexical false negatives are explicitly handled;
2. evidence/question mismatch is separated as E0;
3. uncertain semantic judgments are separated as EVAL;
4. F6 is reserved for evidence-sufficient, context-complete, semantically incorrect cases.

The next stage is to scale the same frozen protocol to a larger LongMemEval sample, starting with n=50. The protocol should not be changed after inspecting individual 50-sample outcomes except for pre-registered implementation bugs or clearly documented evaluator failures.


## 2026-10-08 — LoCoMo n=50 integration failure identified and adapter fix implemented

The previous 50-record LoCoMo-Refined run completed with 0 execution errors, but its 49/50 formation loss and 0/50 answer accuracy across all three modes are scientifically implausible. Oracle Memory recovered Gold Evidence for 50/50, so the run is invalid for failure attribution and is retained only as a methodological negative result.

Root cause: the LoCoMo adapter did not reliably resolve benchmark evidence references to the same turn identifiers used by MemoryEngine, which persists provenance as session_id:turn_index. The adapter also did not consistently pass the loaded conversation into normalization, and list-valued answers were not normalized for the existing lexical scorer.

Fix implemented: LoCoMo normalization now loads the matching conversation, flattens turns into canonical provenance, maps benchmark dialogue/message IDs to MemoryEngine session:turn identifiers, preserves the original benchmark turn ID, resolves evidence by benchmark ID/engine ID/source/text, marks unresolved evidence explicitly, normalizes list/dict answers, and passes the conversation into normalize_locomo_refined.

The previous n=50 LoCoMo result must not be used as a paper result. Re-run validation with:

    G:\\aconda\\python.exe -u -m experiments.run_oracle_experiments --dataset locomo_refined_public --limit 50

Do not run semantic calibration until the new lifecycle and answer-alignment checks pass.

## 2026-10-08 — LoCoMo adapter fix v2: nested session structure

The first provenance fix did not change the anomalous n=50 result. Code inspection identified a second, more specific adapter defect: LoCoMo's `conversation` field is session-structured (11 sessions), while the adapter's turn normalizer treated the session list itself as a flat message list. Consequently, no canonical turn records were produced for most evidence matching, leaving 49/50 cases at the formation boundary.

The adapter has now been corrected to explicitly flatten:

    conversation -> sessions -> messages

and construct canonical provenance per message:

    <session_id>:turn_<message_index>

while preserving the benchmark `dia_id/message_id` separately. Conversation lookup was also hardened with a conversation-index fallback.

The previous two LoCoMo n=50 runs remain invalid for scientific attribution. A fresh n=50 run is required before any semantic calibration.

## 2026-10-09 — LoCoMo provenance indexing fix after repeated n=50 anomaly

A third LoCoMo n=50 run again produced 49/50 F1_FORMATION and only 2% lifecycle evidence recall. This remains an invalid integration result and is not evidence that the memory engine has a 98% formation failure rate.

A code-level indexing discrepancy was identified in the adapter: _locomo_turns() generated canonical turn IDs from the original message-list index, while MemoryEngine._add_claimed() increments its persisted turn_counter only for messages actually ingested. Empty messages are skipped before the engine receives AddMessage, so the two counters can diverge after any empty message in a session.

The adapter now uses a separate engine_turn_idx that advances only for non-empty message content, matching the ingestion rule, while preserving the original benchmark turn ID for lookup. This is a targeted provenance-alignment fix, not yet a validated benchmark result.

### Validation gate before another full run

Do not treat the earlier LoCoMo n=50 runs as paper results. Before spending another ~50 minutes on n=50, validate a single question and inspect:
- normalized Gold Evidence turn/session IDs and resolution status;
- matching raw message IDs and persisted source_turn_id;
- semantic memories sharing the source turn/session;
- Oracle Context prediction, reference answer, and scoring components.

The answer results from the previous run (Real Memory 6%, Oracle Memory 4%, Oracle Context 4%) also fail the benchmark-validity gate. In particular, Oracle Context's low score means answer/reference alignment and answer generation must be inspected separately; it must not be interpreted as evidence of reasoning failure.

### 2026-10-09 — Provenance regression tests pass

The local regression suite for the latest adapter indexing change was run from the repository root:

    G:\\aconda\\python.exe -m pytest tests/test_locomo_turn_provenance.py -q

Result: **2 passed in 0.04s**. The tests cover (1) empty/whitespace messages not consuming the engine turn index while benchmark IDs remain preserved, and (2) turn-index reset for each session.

This verifies the adapter's indexing contract for the covered fixtures only. It does not yet validate persisted MemoryEngine provenance, Gold Evidence resolution on a real LoCoMo record, or Oracle Context answer/reference scoring. The single-record end-to-end validation gate above remains open; do not rerun n=50 yet.



## 2026-10-16 — LoCoMo q0002 case study: confirmed formation-origin failure

A concrete LoCoMo-Refined result was inspected after the provenance-alignment fix:

- Question: `conv-26#q0002`
- Question: “What fields would Caroline be likely to pursue in her education?”
- Gold answer: “Counseling or mental health”
- Gold evidence: `D1:turn_8` and `D1:turn_10`
- `D1:turn_10` explicitly states Caroline is interested in counseling or working in mental health.

### Evidence trace

Real Memory:

- Formation: both Gold Evidence items missing.
- Formation diagnostics: both classified as `F1a_EXTRACTOR_MISS`.
- Raw storage: both evidence items are present and matched by provenance with score 1.0.
- Semantic memory inventory: 21 memories in total (fact=1, relation=0, event=15, rule=4, profile=1), but no semantic memory was associated with either Gold Evidence turn.
- Retrieval candidates: both missing.
- Reranking: both missing.
- Final context: both missing.
- Real answer: “Counseling”; token F1=0.4, below the 0.5 correctness threshold; attributed failure: `F1_FORMATION`.

Oracle Memory:

- Both Gold Evidence items are injected and preserved through the downstream stages.
- Final context contains both Gold Evidence items.
- Answer: “counseling, mental health”; token F1≈0.857; semantically correct.

### Interpretation

This example is consistent with a formation-origin failure rather than a storage or retrieval failure. The raw conversation is preserved, but the extractor does not produce a usable semantic memory for the relevant turns. Because the evidence never enters the semantic-memory layer, downstream retrieval cannot recover it.

The case also demonstrates why “retrieval failure” should not be used as the root-cause label when an earlier lifecycle boundary has already lost the evidence.

This is a case study, not yet a population-level conclusion. The next task is to determine whether similar `F1a_EXTRACTOR_MISS` cases share a systematic linguistic/semantic pattern.

### Immediate research implication

Do not modify the memory extractor yet. First perform the planned LoCoMo n=50 formation diagnostic and manually inspect a stratified sample of `F1a_EXTRACTOR_MISS` and `F1c_REPRESENTATION_MISMATCH` cases. The goal is to separate:

1. genuine extractor misses;
2. representation/provenance matching artifacts; and
3. benchmark evidence/question mismatches.

Only after this diagnostic gate is stable should extractor improvements be evaluated as an intervention.

## 2026-10-17 — LoCoMo n=10 rerun after stable turn-provenance fix

### Run configuration

- Dataset: `locomo_refined_public`
- Command: `G:\\aconda\\python.exe -u -m experiments.run_oracle_experiments --dataset locomo_refined_public --limit 10`
- Samples: 10; completed records: 10; runtime errors: 0
- Local code revision tested: `89c085a` (`Fix stable LoCoMo session turn provenance`); this revision was present locally when the run was executed.

### Lifecycle evidence recall

| Stage | Real Memory | Oracle Memory | Oracle Context |
|---|---:|---:|---:|
| Formation | 1.00 | 1.00 | 0.00* |
| Storage | 1.00 | 1.00 | 0.00* |
| Evolution | 1.00 | 1.00 | 0.00* |
| Retrieval | 0.75 | 1.00 | 0.00* |
| Rerank | 0.55 | 1.00 | 0.00* |
| Context | 0.30 | 1.00 | 1.00* |

\* Oracle Context is a direct-context control, so upstream lifecycle stage recalls are not applicable; the report serializes them as zero. Its Context recall is 1.00.

Real Memory first-loss distribution: none=3, retrieval=3, rerank=2, context=2. Oracle Memory: none=10. Oracle Context: not_applicable=10.

### Answer results

| Mode | Accuracy | Exact Match | Token F1 |
|---|---:|---:|---:|
| Real Memory | 0.00 | 0.00 | 0.0000 |
| Oracle Memory | 0.50 | 0.10 | 0.2222 |
| Oracle Context | 0.50 | 0.10 | 0.2222 |

The evidence-sufficiency gate classified 8/10 samples as `E0_EVIDENCE_INSUFFICIENCY` and 2/10 as sufficient. First answer-failure labels were E0=8 and F6_REASONING=2. The run completed without model errors.

### Interpretation and limitations

This is a small n=10 diagnostic run, not a population-level benchmark result. The stable session-level source prefix and engine turn indexing now pass the focused provenance regression tests (12 tests passed across the three targeted test modules), but this run alone does not establish that every Gold Evidence mapping is correct.

The observed Real Memory evidence recall falls from 1.00 through Formation/Storage/Evolution to 0.75 at Retrieval, 0.55 at Rerank, and 0.30 at Context. This points to downstream retrieval, reranking, and context selection as measurable loss boundaries in this sample. However, the answer-level gate labels eight questions E0 because Gold Evidence is judged insufficient for the reference answer; those cases must not be interpreted as memory-lifecycle failures or used to support F1–F6 attribution without case-level adjudication.

The two F6 cases (`conv-26#q0005` and `conv-26#q0009`) are the most useful initial reasoning-control cases because the current protocol reports sufficient evidence and complete Gold Evidence delivery to context. Inspect their questions, Gold Evidence, final context, generated answers, references, and scoring details before making any reasoning claim. Also inspect an E0 case such as `conv-26#q0000` to verify that the evidence-sufficiency gate is correct.

### Next actions

1. Audit the per-question artifacts for `conv-26#q0000`, `conv-26#q0005`, and `conv-26#q0009`.
2. Manually adjudicate a sample of E0 cases against the exact question and reference answer; record whether each is a genuine evidence/question mismatch or an evaluator false negative.
3. Keep this n=10 result as a diagnostic/negative result. Do not claim generalization or tune the extractor from this run alone.
4. After the gate and provenance checks are stable, run the broader evaluation and compare per-stage recall and answer metrics using the same protocol.

### 2026-10-17 — Case audit: E0 gate contradiction in conv-26#q0000

Inspected the full `comparison.jsonl` record for `conv-26#q0000` (question: “When did Caroline go to the LGBTQ support group?”). Gold Evidence is the turn text: “I went to a LGBTQ support group yesterday and it was so powerful.” The same evidence is found by Real Memory at Formation, Storage, Evolution, Retrieval, Rerank, and final Context; the provenance points to `D1:turn_2`. Real Memory and both oracle controls answer “Yesterday.”; the oracle answer scorer marks both oracle answers correct (with temporal equivalence anchored to 2023-05-08), yet the evidence-sufficiency judge labels the evidence insufficient and claims it says nothing about the event/date. That rationale directly contradicts the evidence text. This case is therefore a strong candidate for an E0-gate false negative / evaluator inconsistency, not a demonstrated memory-formation or retrieval failure. Reconcile the timestamp/date anchor carefully before converting “yesterday” into a calendar date.

A partial audit of `conv-26#q0005` (“When did Melanie run a charity race?”) shows the event text “I ran a charity race for mental health last Saturday...” is present in final Context and the model answers “Last Saturday.” The current record labels it F6, but the answer is a plausible direct extraction of the context. The pasted record also references “The Saturday before 25 May 2023” / May 20, 2023 in the sufficiency rationale, so the exact reference answer, remaining scoring fields, and temporal normalization must be inspected before accepting F6. Treat this as an unresolved potential scoring/temporal-normalization issue, not a confirmed reasoning failure.

#### Updated interpretation and next steps

- The n=10 aggregate's eight E0 labels cannot be taken at face value until sampled cases are manually audited; at least `conv-26#q0000` shows an explicit evidence-vs-judge contradiction.
- Keep evidence-sufficiency adjudication separate from lifecycle stage recall. A case can have complete retrieval/context evidence and still be misclassified by the answerability gate.
- For temporal questions, audit question, exact reference answer, source turn timestamp/date anchor, model output, temporal-equivalence rule, and gate rationale together. Do not infer a reasoning failure solely from token F1 or a failed temporal rule.
- The `conv-26#q0005` classification remains provisional until its full record and reference answer are checked; `conv-26#q0009` also remains unaudited in this pass.
- This is case-level diagnostic evidence only; do not generalize from n=10 or change the memory extractor based on these cases alone.

### 2026-10-17 — Follow-up audit: F6 labels confounded by temporal scoring

Inspected the targeted-field output for `conv-26#q0005` and `conv-26#q0009`.

- **q0005** asks “When did Melanie run a charity race?” Gold evidence at `D2:turn_0`, timestamped 1:14 pm on 25 May 2023, says “I ran a charity race for mental health last Saturday”. Real Memory, Oracle Memory, and Oracle Context all answer “Last Saturday.” The current scorer reports token F1 0.0 and `temporal_equivalent=false` for all modes; Oracle Memory/Context use anchor date `2023-05-25`. The sufficiency judge's rationale says the reference is supported by “The Saturday before 25 May 2023”, equivalent to May 20, 2023. This strongly suggests the scorer fails to align a correct relative-time phrase with the reference's normalized date (or otherwise mishandles this reference), so F6 is not currently a trustworthy reasoning attribution.
- **q0009** asks “When did Caroline meet up with her friends, family, and mentors?” Gold evidence at `D3:turn_10`, timestamped 7:55 pm on 9 June 2023, says “Here's a pic from when we met up last week”. All three modes answer “Last week.”; all have token F1 0.0 and `temporal_equivalent=false`, despite Oracle Memory/Context containing the gold evidence. The evidence-sufficiency judge calls the evidence sufficient. This is a second concrete warning that temporal answer evaluation can mark a directly supported relative phrase wrong.
- **q0000** remains a separate E0-gate contradiction: its evidence explicitly says “I went to a LGBTQ support group yesterday”, while the sufficiency judge claims the evidence says nothing about the event/date; Oracle scoring treats “Yesterday.” as temporally equivalent/correct.

#### Updated conclusion

The observed F6 cases cannot yet be interpreted as confirmed reasoning failures. For q0005 and q0009, answer strings match the relative-time expressions in the evidence, but the temporal-equivalence rule fails and token F1 is zero. Because the oracle controls are also marked wrong, these results point to a potential evaluation/scoring confound rather than a failure unique to the real memory pipeline. The n=10 answer accuracy and F6 counts should be treated as provisional until this is resolved.

#### Next actions

1. Inspect the dataset's exact reference answers for q0005 and q0009 and the implementation of `token_f1_plus_temporal_phrase_rules`; identify why relative phrases are not recognized against the references.
2. Add unit tests for `yesterday`, `last Saturday` (anchor 2023-05-25 -> 2023-05-20), and `last week` (anchor 2023-06-09), including the benchmark's actual reference-answer format. Be explicit about locale and week-boundary conventions.
3. Keep answer correctness, evidence sufficiency, and lifecycle stage recall as separate measurements. Do not relabel F6 or report corrected aggregate accuracy until scoring behavior is validated against reference answers.
4. Review the other n=10 cases, especially all E0 labels, with the same evidence-vs-judge consistency check. These observations are case-level diagnostics, not population-level proof.

## 2026-10-17 — LoCoMo q0005/q0009: temporal scoring confound in apparent F6

### Source inspection

Inspected the committed implementation on `fix/formation-diagnostics-evidence-based`:

- `experiments/run_oracle_experiments.py`: `_answer_failure_type` assigns F6 when the evidence-sufficiency gate says sufficient, the answer is marked incorrect, and Gold Evidence is found at every lifecycle stage.
- `evaluation/answer_generation.py`: deterministic correctness depends on exact match, token F1 >= threshold, `_temporal_equivalent`, or a contained phrase match.
- `datasets/adapters.py`: LoCoMo message timestamps can be strings; `_msg` in the runner only forwards timestamps that are integers. Thus the Real Memory ingestion path can lose the original date anchor, while normalized Gold Evidence preserves the timestamp string.

### Manually inspected examples from the n=10 `locomo_refined_public` run

**conv-26#q0005 — “When did Melanie run a charity race?”**

Gold Evidence says Melanie “ran a charity race ... last Saturday”; its timestamp metadata is 1:14 pm on 25 May 2023. The model answered “Last Saturday.” in Real Memory, Oracle Memory, and Oracle Context. All three were marked incorrect by the lexical/temporal scorer. The evidence-sufficiency judge itself states that the Saturday before 25 May 2023 is 20 May 2023 and marks the evidence sufficient.

**conv-26#q0009 — “When did Caroline meet up with her friends, family, and mentors?”**

Gold Evidence says “Here's a pic from when we met up last week!”; its timestamp metadata is 7:55 pm on 9 June 2023. The model answered “Last week.” in all three modes. All three were marked incorrect even though the same Gold Evidence was directly supplied in Oracle Context and the sufficiency gate marked it sufficient.

### Interpretation and code-level concern

These two examples are **not reliable evidence of F6 reasoning failures yet**. They expose a likely temporal answer-scoring/normalization problem: natural-language relative times in the evidence and prediction are treated as wrong when compared with the benchmark reference, despite the sufficiency judge independently accepting the evidence as temporally supportive.

There is also a concrete anchor-path inconsistency to investigate. `_context_anchor_date` only extracts dates from context metadata strings; the LoCoMo ingestion helper `_msg` forwards a timestamp only when its type is `int`. When the source timestamp is a human-readable string, the real-memory context may instead carry an ingestion-time integer, which is not parsed as a date. Oracle controls preserve the normalized timestamp string, so the three modes can receive different temporal-anchor information.

The exact reference-answer strings were not included in the pasted per-question excerpt, so this log does **not** claim a confirmed single root cause (for example, ordinal-date parsing) for the Oracle score. The raw reference strings must be inspected before changing parser behavior.

### Required follow-up

1. Print the exact `answer` reference field and all context timestamp values for q0005/q0009 from `comparison.jsonl`.
2. Add unit tests for `last Saturday` relative to 2023-05-25 and `last week` relative to 2023-06-09, including benchmark reference formats actually observed in the dataset.
3. Preserve source/session dates through LoCoMo ingestion instead of silently dropping string timestamps; keep event time distinct from ingestion time.
4. Re-run the existing 10 records after scorer/anchor fixes and compare answer correctness and attribution labels across Real Memory, Oracle Memory, and Oracle Context.
5. Until these checks pass, report these two cases as **temporal-scoring / anchor-path audit cases**, not confirmed F6 failures.

### Scope limitation

This is a two-example debugging observation from a 10-record pilot, not a benchmark-level performance claim. The n=10 aggregate should be re-computed after the evaluation protocol is corrected.

## 2026-10-17 — Implement timestamp preservation and temporal scorer regression coverage

### Code changes committed

- `experiments/run_oracle_experiments.py` (`d204fcf`): added `_timestamp_ms` to normalize integer epoch seconds, epoch milliseconds, ISO datetimes, and LoCoMo human-readable timestamps such as `1:56 pm on 8 May, 2023`. `_msg` now checks message timestamp, session date-time, and date rather than discarding all non-integer timestamp strings. Parsed naive benchmark dates are treated as UTC to avoid machine-local timezone drift.
- `evaluation/answer_generation.py` (`a128cbd`, `a566d82`): `_context_anchor_date` now understands MemoryEngine Unix timestamps as well as human-readable timestamps; numeric epoch conversion is explicitly UTC. Explicit date parsing now accepts ordinal day suffixes (e.g. `May 20th, 2023`).
- `tests/test_answer_generation.py` (`2c46c99`): added regression tests for “Last Saturday” relative to 2023-05-25, “Last week” relative to 2023-06-09, ordinal date references, and epoch-millisecond context anchors.
- `tests/test_oracle_timestamp_normalization.py` (`90f4542`): added tests for LoCoMo-style timestamp normalization, ISO datetime and epoch seconds, and conservative handling of unrecognized strings.

### Why this is needed

The previous ingestion helper only passed through integer timestamps. LoCoMo session/message timestamps are often readable strings, so the real-memory path could silently replace benchmark event time with the engine's current ingestion time. The scorer, meanwhile, only extracted dates from readable strings and did not recognize epoch-millisecond timestamps emitted by the engine. These mismatched timestamp representations made relative-time scoring vulnerable to losing the benchmark date anchor.

### Validation status and next action

The regression tests have been added to the repository, but they have **not yet been executed in the user's local Windows environment** from this GitHub-only workflow. Do not describe the fix as test-passing until the user runs:

```powershell
G:\aconda\python.exe -m pytest -q tests\test_answer_generation.py tests\test_oracle_timestamp_normalization.py
```

Then rerun the n=10 pilot and inspect q0005/q0009 exact reference answers and their new `temporal_anchor_date`, `temporal_equivalent`, `correct`, and `answer_failure_type` fields. If they remain wrong in Oracle Context, inspect the exact reference string and relative-week convention before expanding the parser further.

### Research interpretation

This is a targeted correctness fix for timestamp normalization and known date formats, not evidence that all temporal scoring issues are solved. The n=10 aggregate and F6 counts remain provisional until the tests and rerun confirm behavior.

