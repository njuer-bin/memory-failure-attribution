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

### Follow-up source-path audit: session-level dates were also being dropped

A second inspection found a more specific loss point: `datasets.adapters._locomo_sessions` attaches a session date to the normalized session, but the experiment runner's `_sessions()` previously retained only `session_id` and `messages`. When a LoCoMo message did not have its own timestamp, the runner therefore discarded the session date before `_msg()` could normalize it.

- `experiments/run_oracle_experiments.py` (`8db4df6`): `_sessions()` now retains session-level date/timestamp metadata, and ingestion uses it as the message timestamp only when the message has no timestamp of its own.
- `tests/test_oracle_timestamp_normalization.py` (`ce36d52`): added coverage that normalized session dates are retained.

This strengthens the timestamp-path diagnosis: the bug was not only “string timestamps are rejected”; session-level dates could be lost before timestamp normalization even ran. The actual timestamp is now propagated from the session to messages and normalized to Unix milliseconds, while explicit message timestamps take precedence.

Validation is still pending in the local Windows environment. Run:

```powershell
G:\aconda\python.exe -m pytest -q tests\test_answer_generation.py tests\test_oracle_timestamp_normalization.py
```

Then rerun the n=10 experiment and inspect the exact reference answers and score fields for q0005/q0009. Do not update aggregate claims until those outputs are checked.



## 2026-10-17 — Local regression tests pass after timestamp fixes

The user synchronized the timestamp-normalization changes and ran the targeted Windows test command:

```powershell
G:\\aconda\\python.exe -m pytest -q tests\\test_answer_generation.py tests\\test_oracle_timestamp_normalization.py
```

Observed result: **16 passed in 0.79s**.

This validates the targeted unit-test cases for temporal answer scoring, epoch timestamp anchors, timestamp normalization, and session-level date propagation. It does **not** yet establish that the real LoCoMo n=10 rerun has corrected q0005/q0009 or changed the aggregate answer metrics. The next validation gate is to back up the existing `results/oracle_experiments`, rerun `locomo_refined_public --limit 10`, and inspect the exact reference answer, temporal anchor, `temporal_equivalent`, `correct`, and `answer_failure_type` fields for q0005 and q0009. Treat aggregate accuracy and F6 counts as provisional until that end-to-end check is complete.


## 2026-10-18 — End-to-end rerun isolates multi-date reference scoring bug

The user reran the LoCoMo n=10 experiment after the timestamp changes. The uploaded `comparison.jsonl` excerpt shows the timestamp anchor is now correct, but q0005 and q0009 still score as temporally incorrect:

- **q0005**: prediction `Last Saturday.`; anchor `2023-05-25`; reference `The saturday before 25 May 2023 / May 20, 2023`; `temporal_equivalent=false`, `correct=false`, `answer_failure_type=F6_REASONING`.
- **q0009**: prediction `Last week.`; anchor `2023-06-09`; reference `The week before 9 June 2023 / From May 29, 2023 to June 4, 2023`; `temporal_equivalent=false`, `correct=false`, `answer_failure_type=F6_REASONING`. The same answer is also marked incorrect in Oracle Memory and Oracle Context, even though evidence sufficiency is `sufficient`.

### Diagnosis

This is a scorer limitation exposed by the real rerun, not evidence that the timestamp-anchor fix failed. The scorer previously extracted only the first explicit date from a reference. For q0005 that first date is the anchor date (25 May), while the normalized answer date (20 May) occurs later. For q0009 the first date is 9 June, while the reference's explicit week interval is May 29–June 4. The old comparison logic did not inspect all reference dates or parse the explicit interval.

### Follow-up code and tests committed

- `evaluation/answer_generation.py` commit `5572e72`: added ordered extraction of all explicit dates; relative single-day predictions can match a normalized date anywhere in the reference; relative periods can match an explicit `From DATE to DATE` interval.
- `tests/test_answer_generation.py` commit `727e592`: added regressions using the exact q0005 and q0009 reference strings and epoch-millisecond anchors.

### Validation status

These newest changes are **not yet tested locally**. After syncing the latest branch, run:

```powershell
G:\aconda\python.exe -m pytest -q tests\test_answer_generation.py tests\test_oracle_timestamp_normalization.py
```

If those tests pass, rerun the n=10 experiment and inspect q0005/q0009 in `comparison.jsonl`. The expected result for these two scorer cases is `temporal_equivalent=true` and `correct=true`; verify actual output before claiming the end-to-end issue is resolved. Recompute aggregate metrics and failure attribution only after the rerun completes cleanly.

### Research caution

A false-negative temporal scorer can incorrectly turn supported answers into `F6_REASONING` labels. Do not interpret these F6 counts as model-reasoning failures until the scorer is validated against multi-date and interval-form benchmark references.

## 2026-10-18 — Fix missed single-day relative-period comparison

### Test result and diagnosis

The user ran the new targeted tests and reported **1 failed, 17 passed**. The failing test was `test_last_saturday_matches_normalized_date_in_multi_date_reference`. Inspection of `evaluation/answer_generation.py` identified a gap in the previous patch: `Last Saturday` is resolved by `_temporal_period()` as a one-day period, but the new multi-date check only compared `_relative_date()` results (today/yesterday/tomorrow) against the reference dates. Therefore, the normalized date `May 20, 2023` was extracted correctly but never compared to the resolved weekday.

### Fix committed

- Commit `0297242`: compare a resolved one-day relative period (such as `Last Saturday`) against every explicit date extracted from the reference. This preserves the separate interval comparison for answers such as `Last week`.

### Validation status

The code change is committed, but it has **not yet been run in the user's local environment**. Sync the branch and rerun:

```powershell
G:\\aconda\\python.exe -m pytest -q tests\\test_answer_generation.py tests\\test_oracle_timestamp_normalization.py
```

Only after all tests pass should the n=10 Oracle experiment be rerun. Check q0005 and q0009 in `comparison.jsonl` for `temporal_equivalent`, `correct`, and `answer_failure_type`; do not claim the end-to-end scoring issue is fixed based on the unit test alone.

## 2026-10-18 — Relative-date scorer regression tests pass

### Local validation reported by the user

Command:

```powershell
G:\\aconda\\python.exe -m pytest -q tests\\test_answer_generation.py tests\\test_oracle_timestamp_normalization.py
```

Observed result: **18 passed in 0.45s**. This includes the formerly failing multi-date `Last Saturday` case and the explicit date-range `Last week` case.

### Interpretation and next gate

The targeted unit tests now pass after commit `0297242`. This validates the covered scorer and timestamp-normalization cases, but does not yet establish that the full n=10 experiment's answer scores and failure labels have changed as expected.

Next, rerun:

```powershell
G:\\aconda\\python.exe -u -m experiments.run_oracle_experiments --dataset locomo_refined_public --limit 10
```

Inspect q0005 and q0009 in the newly generated `comparison.jsonl` for `temporal_anchor_date`, `temporal_equivalent`, `correct`, and `answer_failure_type`. Confirm whether their temporal answers now score as correct, then recompute aggregate metrics and attribution counts. Keep end-to-end conclusions provisional until those outputs are inspected.

## 2026-10-18 — Evidence-sufficiency gate schema mismatch found and fixed

### Root cause from source inspection

The normalized benchmark adapter and trace layer represent Gold Evidence with a `text` field (`EvidenceItem.text` in `tracing/dataset_trace.py`). However, `evaluation/answer_semantic_eval.py` read only `item["content"]` in all three places used to render evidence for the LLM judge, find lexical anchors, and detect relative-time support.

The runner calls `evaluate_answer(..., gold)` with `gold = [e.__dict__ for e in trace.gold_evidence]`, so the judge received empty evidence text even though `comparison.jsonl` visibly contained non-empty Gold Evidence. This directly explains the contradictory “evidence is missing” rationales, including the q0003 record, and can systematically inflate E0 labels. It also disabled deterministic lexical/temporal safeguards for the normalized `text`-schema evidence.

### Fix and regression coverage

- `evaluation/answer_semantic_eval.py`: accept `content` or `text` consistently in evidence rendering, lexical-anchor matching, and relative-temporal matching.
- `tests/test_answer_semantic_eval.py`: add regression tests for normalized `text` evidence, lexical support, relative-time support, end-to-end deterministic evaluation without a live judge, and backward compatibility with `content` evidence.

### Interpretation and validation gate

This is a concrete schema-integration bug, not merely an LLM judge-quality issue. It is likely to explain multiple false E0 classifications in the n=10 LoCoMo run. The committed tests have not yet been run in the user's local environment; after syncing the branch, run:

```powershell
G:\aconda\python.exe -m pytest -q tests\test_answer_semantic_eval.py tests\test_answer_generation.py tests\test_oracle_timestamp_normalization.py
```

Then rerun `locomo_refined_public --limit 10` and compare all eight former E0 cases. Do not reuse the old E0 distribution or make population-level claims until the end-to-end rerun is inspected. q0004 (identity) and q0007 (relationship status) still require semantic judgment rather than being automatically promoted based only on the current snippets.


## 2026-10-18 — End-to-end validation of the sufficiency-gate fixes (LoCoMo n=10 rerun)

### Local validation

Command:

```powershell
G:\aconda\python.exe -m pytest -q tests\test_answer_semantic_eval.py tests\test_answer_generation.py tests\test_oracle_timestamp_normalization.py
```

First run: 22 passed, 1 failed. The failure was `test_deterministic_support_reads_text_field`: for evidence "We're thinking about going camping next month." and candidate "Next month.", `_deterministic_support` returned `deterministic_lexical` instead of `deterministic_temporal` because the lexical-anchor check ran before the relative-temporal check and "next month" matched as a surface n-gram.

Fix (uncommitted at write time): in `evaluation/answer_semantic_eval.py`, `_deterministic_support` now tries the deterministic temporal path first and only falls back to the lexical anchor. Non-temporal candidates do not satisfy `temporal_equivalent`, so the lexical branch is unchanged for them. All 23 tests then pass.

### Rerun

```powershell
G:\aconda\python.exe -u -m experiments.run_oracle_experiments --dataset locomo_refined_public --limit 10
```

10/10 completed, 0 model errors. Aggregate:

| Mode | correct/10 | accuracy | EM | token F1 |
|---|---:|---:|---:|---:|
| Real Memory | 3 | 0.30 | 0.10 | 0.10 |
| Oracle Memory | 8 | 0.80 | 0.10 | 0.222 |
| Oracle Context | 8 | 0.80 | 0.10 | 0.222 |

Real Memory stage recall: formation 1.0, storage 1.0, evolution 1.0, retrieval 0.75, rerank 0.55, context 0.3. First-loss distribution: none 3, retrieval 3, rerank 2, context 2.

### Former E0 comparison

The former 8-case E0 cluster collapsed to a single E0 (conv-26#q0001). Per-question:

- q0001 — E0 stands: Gold Evidence ("You'd be a great counselor!...") genuinely does not answer "When did Melanie paint a sunrise?". Same verdict under Oracle Context. This is the one legitimate E0 in the sample.
- q0004 (identity) — now evidence-sufficient, real-memory first failure F4_RETRIEVAL; Oracle Context answer still wrong (RC_REASONING_CONTROL_FAILURE). No automatic promotion; it stayed an F-label only because the gate passed and the answer scored incorrect.
- q0007 (relationship status) — now evidence-sufficient and scored correct; no failure label.
- q0005 — "Last Saturday." now scores `temporal_equivalent: true` under the fixed scorer; no failure label in any mode.
- q0009 — "Last week." likewise scores `temporal_equivalent: true`; no failure label in any mode.

First answer-failure distribution: F6_REASONING 1 (q0000), E0 1 (q0001), F4_RETRIEVAL 3, F5_CONTEXT 2.

### Interpretation and next gate

Both targeted scorer fixes are validated end-to-end: the `text`-schema sufficiency bug is gone (E0 8→1, and the survivor is a genuine mismatch), and relative-period answers (q0005 "Last Saturday", q0009 "Last week") now score correctly instead of being marked F6/EVAL.

The n=10 protocol is now consistent. Next gate per the standing plan: freeze this protocol, scale to n=50 LongMemEval samples, then inspect before larger runs and LoCoMo cross-benchmark validation. Conclusions remain sample-level (n=10), not population-level.

## 2026-10-18 — LongMemEval n=50 first scaled run (provisional, with open anomalies)

### Run

```powershell
G:\aconda\python.exe -u -m experiments.run_oracle_experiments --dataset longmemeval_oracle --limit 50
G:\aconda\python.exe -u -m experiments.semantic_calibration
```

50/50 completed, 0 model errors.

### Evidence lifecycle

Real Memory and Oracle Memory both show stage recall 1.0 at every stage; first-loss distribution is `none` for all 50 samples. Unlike LoCoMo, this LongMemEval oracle configuration produces **zero memory-side evidence loss**, so every answer failure must be attributed downstream (F6/E0), and the F1-F4 stages are uninformative in this setting.

### Answer scoring, lexical layer

| Mode | correct/50 | EM | token F1 |
|---|---:|---:|---:|
| Real Memory | 21 | 0.10 | 0.364 |
| Oracle Memory | 18 | 0.16 | 0.361 |
| Oracle Context | 18 | 0.16 | 0.364 |

Lexical first-failure distribution: F6 26, E0 3.

### Answer scoring, semantic layer (calibrated)

| Mode | semantically correct/50 |
|---|---:|
| Real Memory | 40 |
| Oracle Memory | 36 |
| Oracle Context | 35 |

Real Memory semantic failure distribution: **F6 candidates 8, E0 2**, evaluation-uncertain 0. Of the lexical layer's 26 F6 labels, 18 were repaired by semantic evaluation — the spot-checked case `gpt4_2655b836` ("GPS system glitch on 3/22, which required replacement" vs reference "GPS system not functioning correctly", token F1 0.129 < 0.5) confirms these are threshold artifacts, not reasoning failures.

### Open anomalies — do not quote these numbers as findings yet

1. **Real Memory > Oracle Context inversion (40 vs 35)** persists at n=50. Hypothesis to test: the oracle paths supply only the (sometimes context-poor) Gold Evidence, while Real Memory's context retains additional relevant turns that help the answer model. Needs a controlled comparison of the actual final contexts.
2. **Judge-vs-benchmark disagreement inside F6 candidates**: e.g. `0bb5a684` — benchmark reference says 3 days, but Gold Evidence states the workshop was January 10th and the meeting January 17th (7 days). The judge ruled the reference wrong. If the evidence genuinely fails to establish the reference answer, such cases are E0, not F6. Each of the 8 F6 candidates needs per-case adjudication before the F6 count is publishable.
3. **E0 accounting gap**: the lexical layer flagged 3 E0, the semantic layer 2. Reconcile which case flipped and why.

### Status

The scaled pipeline runs end-to-end without errors and the conservative gate behaves as designed. However, the F6/E0 distribution above is **provisional**: the 8 F6 candidates are candidates only, and the three anomalies above must be resolved (per-case F6 adjudication, inversion analysis, E0 reconciliation) before any population-level claim. Next actions: (a) adjudicate the 8 F6 candidates individually; (b) diff Real Memory vs Oracle Context final contexts; (c) reconcile E0 counts.

## 2026-10-18 — Per-case adjudication of the 8 LongMemEval F6 candidates

Method: each candidate was compared against the benchmark reference answer and the Gold Evidence dates directly (deterministic day arithmetic), independent of the judge verdict. Full record: `results/oracle_experiments/f6_adjudication_n50.json`.

### Result: 6 confirmed F6, 2 judge false negatives

Confirmed F6 (evidence supports the reference; candidate answer wrong):

| qid | evidence dates | correct | candidate |
|---|---|---:|---:|
| 0bb5a684 | workshop Jan 10 → meeting Jan 17 | 7 | 3 |
| 08f4fc43 | mass Jan 2 → Ash Wednesday Feb 1 | 30 | 20 |
| 2a1811e2 | Holi Feb 26 → mass Mar 19 | 21 | 31 |
| dcfa8644 | shoes Jan 10 → laces broke Jan 24 | 14 | 6 |
| a3045048 | gift Apr 15 → birthday Apr 22 | 7 | 15 |
| gpt4_4cd9eba1 | accepted Mar 20 → orientation Mar 27 | 1 wk | 3 wks |

Judge false negatives (candidate equals reference; NOT F6):

- `bbf86515` — candidate "4" = reference "4 days"; the judge's own reason says "the difference is 4 days" but the verdict was incorrect (reason/verdict contradiction).
- `c8090214` — candidate "7 days" = reference "7 days"; the judge computed 7 days then overrode it with a confused objection that it "should be 0 days".

### Interpretation

1. The provisional F6 count of 8 revises to **6/50 (12%)**.
2. All 6 confirmed F6 are temporal-reasoning day-arithmetic questions — with a perfect-recall memory pipeline, the only observed reasoning failure mode in this sample is date arithmetic by qwen2.5:7b.
3. The semantic judge (same qwen2.5:7b) exhibits its own failure modes: date-arithmetic error (`08f4fc43`: computed 20 instead of 30), reason/verdict contradiction (`bbf86515`), reference misquotation (`a3045048`), and a garbled-but-correct-enough verdict (`gpt4_4cd9eba1`). In this run the judge's *false negatives* were repairable (candidate = reference is deterministically checkable), but a judge that cannot do day arithmetic cannot reliably adjudicate day-arithmetic F6 candidates in general. This strengthens the case for deterministic temporal scoring as the primary attribution instrument and the LLM judge as a fallback.

## 2026-10-18 — Anomaly resolution: RM>OC inversion is a judge artifact; E0 counts reconciled

### Anomaly 1: Real Memory > Oracle Context inversion — resolved as judge artifact

Deterministic rescore of all 150 stored answers (reference-match + temporal rules, no judge):

| Mode | deterministic correct/50 | + possible lexical false negatives |
|---|---:|---:|
| Real Memory | 20 | ~3 |
| Oracle Memory | 19 | ~1 |
| Oracle Context | 21 | ~1 |

The inversion disappears: OC (21) >= RM (20), within noise at n=50. The semantic layer's RM 40/50 was inflated by the judge accepting refusals ("The evidence does not provide...") and wrong answers (RM "3" vs ref 14; RM "0" vs ref 4) as correct, while rejecting exact matches from OC (d01c6aa8: OC "27" == ref "27" judged incorrect). All 5 RM-correct/OC-incorrect discordant pairs are temporal-reasoning cases. Structural note: `run_oracle_experiments.py` feeds the identical `oracle` context to both oracle_memory and oracle_context scoring (lines 414-415), so those two modes are currently duplicates by construction — they should be differentiated or merged.

### Anomaly 2/3: E0 reconciliation — 1 genuine E0; 3 gate/judge false positives reclassified to F6

- `b9cfe692` — **genuine E0** (only one): evidence gives per-book durations but cannot establish the combined 5.5-week figure. Both layers agree.
- `2c63a862` — gate false positive. Evidence: started with Rachel 2/15, house found 3/1 → 14 days = reference. Evidence is sufficient; the gate judge failed the date arithmetic. RM refusal → F6.
- `e4e14d04` — gate false positive. Evidence: joined 3 weeks ago, meetup last week → 2-week membership = reference. RM answered "Three weeks" (no subtraction) → F6.
- `6613b389` — semantic-E0 false positive. Evidence: engagement May 15, anniversary July 22 → ~2 months = reference. Gate was right; RM "5 months" → F6.

### Corrected n=50 attribution (real_memory)

- F6: 6 (from candidate adjudication) + 3 (reclassified) = **9/50**
- E0: **1/50**
- Judge-flagged incorrect was 10; deterministic incorrect is ~30 with ~3 lexical false negatives — the qwen2.5:7b judge both over-accepts wrong answers and over-rejects correct ones. Judge-based counts at this model scale are unreliable in both directions; deterministic evidence tracing and reference matching remain the trustworthy instruments.

### Standing conclusion for the paper (provisional, n=50 LongMemEval oracle config)

With a perfect-recall memory pipeline (all gold evidence reaches final context), essentially all answer failures concentrate in F6 reasoning — and specifically in temporal day-arithmetic — plus a small genuine E0 tail. The methodological contribution stands: lexical thresholding overestimates F6 ~3x, and an LLM judge of the same scale as the answer model cannot reliably adjudicate temporal F6 candidates.

## 2026-10-18 — CORRIGENDUM: earlier n=50 F6/E0/inversion conclusions are withdrawn

The entries above (F6 candidate adjudication, "anomaly resolution", the "standing
conclusion for the paper") were produced before the instrumentation repairs from the
same-day audit were implemented. They must not be cited as findings.

What was wrong in the instrument (now fixed, see the audit items):

- **Attribution used lexical correctness.** F6 was driven by a token/EM scorer and a
  broad lexical override, so both F6 candidates and E0 counts depended on a scorer the
  audit had already shown to be unreliable (C1, C5). Attribution now consumes the
  semantic verdict; a lexically "correct" score cannot suppress a semantically incorrect
  answer, and a missing/-low-confidence verdict becomes EVAL instead of F6.
- **Evidence matching counted provenance as availability.** A memory from the gold turn
  with unrelated content was counted as found, inflating recall to 1.00 at every stage
  (C3). Matching now requires provenance agreement *and* content agreement, reports
  `provenance_only` as missing, and separates `unverified_provenance`.
- **Evolution recall was a copy of formation** (C4). It is now excluded from first-loss
  attribution and reported as unmeasured rather than as a numeric recall.
- **Oracle Memory and Oracle Context shared one code path** (C6). Oracle Memory now
  writes Gold Evidence directly into a fresh store and still exercises retrieval/rerank/
  context; Oracle Context bypasses memory entirely. The Oracle Memory ingestion also
  dropped the session-granularity Gold Evidence through a `source` vs `source_id` key
  mismatch; this is fixed.

Consequently:

1. The corrected F6 = 9/50 and E0 = 1/50 figures are **withdrawn**. They were derived
   from a limited candidate subset plus manual adjudications, on top of a judge that
   produced both false positives and false negatives, and approximately 30 deterministic
   errors that were never fully attributed.
2. The "Real Memory > Oracle Context inversion is resolved" claim is **withdrawn**. The
   inversion analysis established serious judge artifacts, not a final comparative
   ranking; the deterministic rescore (RM 20 / OM 19 / OC 21) does not reconcile with the
   original 21/18/18 totals because it used different timestamp contexts.
3. The claim that F6 concentrates in day arithmetic may still hold, but it is currently
   unverified: the earlier F6 set was selected with the broken override and judged by the
   same model family as the answer model.

All stored artifacts from that period are preserved under
`results/archive/n50_lexical_2026-10-18/` as a negative result. The n=50 numbers will be
regenerated from scratch with the repaired instrumentation before any paper claim.

## 2026-10-18 — Regenerated n=50 LongMemEval (clean run under the frozen protocol)

Run: `results/oracle_experiments_n50_final/`, `resumed_records: 0`, `errors: 0`,
commit `ff4f411` (dirty tree), dataset `longmemeval_oracle` sha256_16 `5a6a52e1a98f85eb`.

**Why a fresh run was required.** The intermediate run `results/oracle_experiments_n50_repaired/`
carried `resumed_records: 38`: 38 of its 50 rows were inherited by `--resume` from output
written before the audit fixes. Its traces and gate verdicts are therefore mixed-protocol
and an offline rescore cannot repair them. The earlier `__rescored` diff is retained only
as an instrument comparison, not as a result.

**Lifecycle (deterministic instrument; identical to the intermediate run to 4 dp).**

- Real Memory: formation 0.503, storage 1.00, retrieval 1.00, rerank 0.993, context 0.880;
  first-loss {formation 36, context 1, none 13}.
- Oracle Memory: retrieval 1.00, rerank 1.00, context 0.982; first-loss {none 48, context 2}.
- Oracle Context: context 1.00.

**Answer failure attribution (semantic verdict consumed by the unified module).**

| mode | none | F1 | F5 | F6 | E0 | RC | EVAL |
|---|---|---|---|---|---|---|---|
| real_memory | 30 | 12 | 1 | 5 | 2 | — | 0 |
| oracle_memory | 32 | 0 | 1 | 14 | 2 | — | 1 |
| oracle_context | 32 | 0 | 1 | 0 | 2 | 15 | 1 |

Gate: sufficient 46, insufficient 3, error 1. Semantic accuracy: RM 21/41 (0.512),
OM 24/41 (0.585), OC 24/41 (0.585). Paired McNemar exact across conditions is
non-significant (RM vs OM p=0.6875, RM vs OC p=1.0000, OM vs OC p=1.0000); paired
bootstrap CIs all straddle 0. The previously reported "Real > Oracle inversion" does not
reproduce.

**Reading (provisional, n=50).** With perfect recall the residual failures concentrate in
F6 reasoning (14/50 = 28%); with real memory the dominant failure source is F1 formation
(12/50), with F6 suppressed to 5/50 because those questions never reach reasoning with full
evidence. No condition separation is statistically supported at this sample size.

**Judge reliability remains the binding constraint.** `gpt4_2487a7cb` is reproduced as a
confident judge false positive in all three modes: the reference order is webinar (two
months ago) before workshop (last Saturday), yet the judge states "last Saturday ... earlier
than ... two months ago" and marks the wrong answer correct at high confidence. A false
positive of this kind suppresses F6, so 14/50 is not an upper bound and the F6 count is not
yet usable as a paper claim. Cross-model re-judgment (`gemma3:12b`, via
`experiments/judge_reliability.py`) is the next required step; it was deferred because host
memory was at 97% (0.4 GB free) with `qwen2.5:7b` resident.

---

## 2026-10-19 — Judge reliability measured; deterministic ordering refutation added

**Self-consistency (qwen2.5:7b).** `judge_reliability.py` over the canonical n=50 run
(`judge_reliability_self.json`): 123 answer verdicts + 50 gate re-checks, zero flips,
kappa 1.0. The judge is deterministic at temperature 0; same-model re-judgment is
uninformative.

**Cross-model (gemma3:12b).** `judge_reliability_gemma3.json`: `correct_verdict`
agreement 0.927 / kappa 0.849 with 9 flips (all in gemma3's favor: False→True —
gemma3 is the looser judge). `raw_judge` agreement 0.710 / kappa −0.028: the two
models' raw verdicts are near-independent. Both models reproduce the
`gpt4_2487a7cb` ordering false positive. **An LLM judge alone cannot support a
paper-grade F6 count.**

**False-positive audit.** 45 stored rows have `semantic_correct=True` while the
answer differs lexically from the gold. 33 are two-option ordering questions
("Which ... first, A or B?"); triaging them (`manual_triage_ordering.json`) shows
30 are provable false positives — the candidate names the option that is NOT the
gold, and the evidence resolves the order. The remaining rows were left to the
judge (conservative).

**Instrument fix.** `evaluation/answer_semantic_eval.py` gains
`_ordering_refutes_judge`: a post-judge false-override layer for exactly this
question shape. Flip requires (1) a two-option ordering tail in the question,
(2) the candidate naming exactly one option, (3) resolvable dates on both
options' supporting sentences with the pick strictly later — otherwise the judge
stands. Added explicit month-day date parsing (year from the turn timestamp) and
word-number "N units ago" phrase resolution. Hooked into `evaluate_answer`
(adjudication `ordering_refutation`) and into offline rescoring via
`experiments/rescore_answers.py --apply-ordering-refutation`. 18 tests added;
123 passed.

**Effect on the canonical n=50 numbers.** Five stored verdicts flip
(`gpt4_2487a7cb` ×3, `gpt4_1a1dc16d` ×2); attribution after the
rescore (`results/oracle_experiments_n50_orderrefuted/`):

| mode | none | F1 | F5 | F6 | E0 | RC | EVAL |
|---|---|---|---|---|---|---|---|
| real_memory | 28 | 14 | 1 | 5 | 2 | — | 0 |
| oracle_memory | 30 | 0 | 1 | 16 | 2 | — | 1 |
| oracle_context | 31 | 0 | 1 | 0 | 2 | 16 | 1 |

Semantic accuracy: RM 19/41, OM 23/42, OC 25/43. Paired McNemar unchanged in
conclusion: non-significant everywhere (p = 0.7266, 0.4531, 1.0000); CIs straddle 0.
F6 rises (14→16 OM; 12→14 F1 RM) — the earlier F6 counts were lower bounds with a
measurable judge-induced floor.

**Limitations recorded.** (1) 21 of the 33 ordering false-positive rows are not yet
refuted because binding an option to a date requires the date and the option in the
same sentence; cross-sentence binding ("for my sister" separated from "necklace") is
left to the judge rather than risking overreach. (2) Self-consistency proves nothing
about correctness — the cross-model disagreement is the pin.

---

## 2026-10-19 — CCF-B publication route planned

Target: a CCF-B venue on long-term-memory / LLM-agent QA (candidates: CIKM,
COLING, ECIR, NLPCC). Publication-route doc lives in `docs/PUBLICATION_ROADMAP.md`
(single planning source; STATUS.md remains the resume point for daily work).

---

## 2026-10-19 — LoCoMo n=50 cross-benchmark run (DeepSeek-v4.1-flash via gateway)

Backend: `ANSWER_API_STYLE=anthropic`, opencode zen gateway, `deepseek-v4.1-flash`
for both answer and judge. Embedding stayed local (bge-m3). Run interrupted once by
host memory and resumed (`resumed_records: 33`, same protocol, same model); `errors: 0`;
4/147 judge calls still failed after the empty-response retry and are recorded as
`semantic_error`, not silently repaired.

**Gate:** sufficient 32 / insufficient 17 / error 1. Semantic accuracy RM 28/49
(0.571), OM 37/49 (0.755), OC 37/47 (0.787).

| mode | none | F1 | F4 | F5 | F6 | E0 | RC | EVAL |
|---|---|---|---|---|---|---|---|---|
| real_memory | 28 | 5 | 3 | 1 | 2 | 10 | — | 1 |
| oracle_memory | 37 | 0 | 1 | 0 | 5 | 6 | — | 1 |
| oracle_context | 38 | 0 | 0 | 0 | 0 | 6 | 4 | 2 |

**Cross-benchmark contrast.** Stage recall differs structurally: LongMemEval's
bottleneck is formation (0.503) with retrieval perfect; LoCoMo is recall-limited at
retrieval (RM 0.560; OM 0.810) and context (RM 0.360; OM 0.805), and 17/50 questions
fail the evidence-sufficiency gate. If this holds at n=200, the paper's claim becomes
benchmark-conditional rather than universal: "the first-loss stage is a property of
the memory system × workload pair, not of memory agents in general." That is a
stronger and more defensible story than a single-stage headline.

**Instrument notes.** Three gateway defects fixed this session: text-block extraction
across thinking blocks, `max_tokens` 1024→4096, and retrying thinking-only responses.
Same-question before/after retry: 3/12 → 0/15 judge errors.

---

## 2026-10-19 — LongMemEval n=200: the oracle ladder now separates

Backend: deepseek-v4.1-flash (answer + judge) via the opencode gateway; embedding
local (bge-m3). Run dir `results/oracle_experiments_longmemeval_n200/`:
200 records, `errors: 0`, `resumed_records: 0`, 17 answer-level semantic errors
(recorded, not repaired).

**Gate:** sufficient 153 / insufficient 41 / error 6. Semantic accuracy:
RM 85/163 (0.521), OM 96/139 (0.691), OC 110/134 (0.821).

**Paired statistics (McNemar exact + paired bootstrap):**

| contrast | n01 | n10 | p | diff | 95% CI |
|---|---|---|---|---|---|
| RM vs OM | 20 | 5 | 0.0041 | −0.117 | [−0.195, −0.047] |
| RM vs OC | 29 | 5 | <0.0001 | −0.205 | [−0.299, −0.111] |
| OM vs OC | 15 | 5 | 0.0414 | −0.083 | [−0.158, −0.017] |

All three CIs exclude zero. This is the statistical result the n=50 run could not
produce; the "no separation" conclusion of 2026-10-18 was a power artifact, not a
negative finding.

**Attribution (n=200):**

| mode | none | F1 | F4 | F5 | F6 | E0 | RC | EVAL |
|---|---|---|---|---|---|---|---|---|
| real_memory | 116 | 61 | 1 | 1 | 3 | 10 | — | 8 |
| oracle_memory | 151 | 0 | 0 | 20 | 10 | 11 | — | 8 |
| oracle_context | 174 | 0 | 0 | 0 | 0 | 13 | 10 | 3 |

Lifecycle recall: RM formation 0.427, retrieval 1.00, rerank 0.990, context 0.896;
OM retrieval 1.00, context 0.951; OC context 1.00. RM first-loss: formation 155,
context 4, rerank 2, none 39.

**Reading.** Formation is the dominant first-loss stage under real memory
(77.5% of questions), and the OM→OC gap (p=0.041) shows a measurable
context/reasoning cost even with perfect retrieval. F6 is small (OM 10/200 = 5%),
so the earlier F6-centered narrative is weaker than the formation narrative at
scale. The LoCoMo n=200 run will test whether the retrieval-heavy profile
persists.

## 2026-10-20 — First-loss is not the repair target (P2 intervention)

**Offline reanalysis of the n=200 real-memory answer failures.** Of the 61 rows
labelled `F1_FORMATION`, only 35 have formation as the *last* missing stage: in
those rows every later stage — including the final context — already contains
all gold evidence, and the answer is still wrong. The other 26 divide into 21
where context assembly drops the item and 5 where reranking drops it. In other
words, the first-loss label is a statement about the semantic layer, not about
what blocks the answer: raw verbatim storage recovers the evidence downstream.

Routing the 66 attributable real-memory failures by the evidence path gives:
reasoning 38 (35 F1 + 3 F6), context 22 (21 F1 + 1 F5), retrieval 6
(5 F1 + 1 F4). Repairing formation therefore cannot move the majority of the
answers the protocol attributes to formation. This is an instrument-validity
finding for claim C2 and must be reported, not papered over.

**Implementation (no numbers yet).** `experiments/interventions.py` +
`experiments/run_interventions.py` compare three routing arms on the same
question set under one answer model, judge, gate and deterministic floors:

- `first_loss`: repair the stored attribution label
  (F1→formation write-through, F4→wider candidate pool, F5→wider context,
  F6→answer self-check).
- `path`: repair the stage that actually blocks the answer; if context is
  complete, route to reasoning.
- `agnostic`: apply formation write-through + context widening + self-check to
  every attributable failure.

Repairs are deterministic except the reasoning self-check (one extra
temperature-0 answer call). The formation repair writes a provenance-carrying
verbatim event for every turn the extractor left unrepresented; it never reads
gold. The context repair raises `top_k` 10→20 and EvidenceBuilder's per-type cap
3→8. Results are paired per question with exact McNemar and a paired bootstrap.

**Blocked on execution:** `ANSWER_API_KEY` is not set in this shell and the host
has 0.8 GB RAM free, so neither the gateway nor a local qwen2.5:7b run is
currently possible. Tests: 139 passed.

**Power note before running the intervention.** Exact McNemar depends only on
the discordant pairs: with zero losses, the smallest outcome reaching p<0.05 is
6 net gains (p = 0.031). On the LongMemEval n=200 routing that is 15.8 points on
the 38-row reasoning subset, 9.1 points on the 66-row attributable set, and 3.0
points on all 200 questions. The roadmap gate "≥5 points with CI excluding 0" is
therefore not reachable on the reasoning subset by a 5-point effect; either the
repair must also flip non-target rows, or the claim should be stated on the full
paired set with the subset reported descriptively. Pre-register this before the
run so the gate is not reinterpreted after seeing the numbers.

## 2026-10-20 — Embedding backend audit: all recent runs used the hash fallback

While resuming LoCoMo n=200 the embedding path was checked instead of assumed.
`memory_engine/vector.py` defaults to `qwen3-embedding:4b`, which is not
installed; the exception is swallowed and the deterministic 384-dim hash
embedder serves every call. Stored vectors confirm it: databases from
2026-10-08 to 2026-10-10 11:41 are 2560-dim (qwen3-embedding:4b), and every
database from 2026-10-10 13:51 onward — including the canonical n=50 run, the
LongMemEval n=200 run and the first LoCoMo rows — is 384-dim.

Consequences: (1) the earlier description of runs as "embedding stayed local
(bge-m3)" is incorrect and is corrected in STATUS/PROTOCOL; (2) the canonical
results are internally consistent because every condition used the same
fallback; (3) switching to bge-m3 now would break comparability, so the study
stays on `hash:384` and the paper must disclose it. `run_metadata` now stores a
probe of the actual backend and the runner logs a warning on fallback. The
LoCoMo run was stopped and restarted from row 4 with no rows discarded.

## 2026-10-20 — LoCoMo n=200: retrieval-limited, and the oracle ladder's top rung vanishes

Backend: deepseek-v4.1-flash (answer + judge) via the opencode gateway; embedding
`hash:384` (see the backend audit above). Run dir
`results/oracle_experiments_locomo_n200/`: 200 records, `errors: 0`,
`resumed_records: 178` across four memory-pressure interruptions. Analysis:
`results/analysis_locomo_n200.txt`.

**Gate:** sufficient 106 / insufficient 86 / error 8. LoCoMo's refined-public
gold/question pairing is much weaker than LongMemEval's: 43% E0 versus 20.5%.
Semantic accuracy RM 70/173 (0.405), OM 144/173 (0.832), OC 150/176 (0.852).

| contrast | n01 | n10 | p | diff | 95% CI |
|---|---|---|---|---|---|
| RM vs OM | 73 | 6 | <0.0001 | −0.432 | [−0.523, −0.348] |
| RM vs OC | 78 | 7 | <0.0001 | −0.452 | [−0.541, −0.357] |
| OM vs OC | 14 | 10 | 0.5413 | −0.025 | [−0.081, 0.037] |

Stage recall: RM formation 0.335, storage 0.995, retrieval 0.669, rerank 0.543,
context 0.322; OM retrieval/rerank/context 0.872/0.872/0.867.

**Reading.** The RM→OM jump is 1.9× larger than on LongMemEval and the OM→OC
contrast is no longer significant: once gold evidence is written directly into
memory, LoCoMo's remaining loss is retrieval and context assembly, not reasoning.
LongMemEval keeps a small but significant OM→OC gap (p=0.041), so the *top* rung
of the oracle ladder is workload-dependent as well. C2 now has n=200 evidence on
both benchmarks: formation-dominated on LongMemEval, retrieval/context-limited on
LoCoMo. The 43% E0 rate bounds every cross-benchmark accuracy comparison and must
be reported; the per-question attribution subset, not the raw accuracy, is the
right unit for the stage claim.

## 2026-10-25 — n=50 fingerprint completed, tested, and human-calibrated

This session resumed the paused LoCoMo fingerprint (43→50) and closed the
measurement loop around it. Commits `07f72b9`, `5802ca1`, `1bd309e`,
`77dfb7a`, `4f48541`, `c53ac29`.

**1. n=50 fingerprint complete.** `results/systems_locomo_n50_fixedgate/`,
50×3 rows, `errors: 0`. The first 43 rows reproduce the n=43 numbers exactly
(0.488/0.465/0.465), so the resume introduced no drift. Attributed accuracy
semantic 0.480 / summary 0.420 / verbatim 0.400; paired McNemar p≥0.48.

**2. Stage-distribution tests added and significant.**
`evaluation/stage_distribution_tests.py`: Stuart–Maxwell marginal homogeneity
with a Jacobi pseudo-inverse (the reduced-block shortcut dies when a category
carries no off-diagonal mass), per-label paired bootstrap CIs, and a max-abs
paired permutation test. Hand-verified on a classic 3-category example
(chi2=2.4915, p=0.2877). All three system pairs differ: SM p=0.0052/0.0201/
0.0344, Holm-adjusted all survive.

**3. Human annotation exposed two instrument failures.** Two annotators,
200 rows. Answer correctness kappa 0.92; evidence sufficiency kappa 0.0
(degenerate — one annotator never said "no" because the instruction invited
topical matching). Against adjudicated labels the judge has 20/66 (30.3%)
false positives among stored-correct rows, 13 of them abstention-style
answers ("Not mentioned", "Cannot be determined") accepted as correct; the
gate is near-independent of humans (kappa 0.03–0.07, recall 0.564). The
stored failure labels themselves are sound: 54/60 (90%) stored-incorrect
rows confirmed wrong.

**4. The fingerprint survives correction and sharpens.** Applying the
human-validated abstention rule to the stored answers flips 28 rows across
the three systems; corrected accuracy is 0.260/0.280/0.200 with paired
accuracy still null (p≥0.45), while the stage-distribution signal gets
stronger: Stuart–Maxwell p=0.00096/0.00524/0.00568 (Holm 0.0029/0.0105/
0.0105), per-label CIs excluding 0 for F1 (+0.18 semantic), F5 (+0.20/0.22
summary) and F4 (−0.30/−0.22/−0.40 verbatim). The paper reports both label
versions side by side.

**5. Round-2 gate package.** `README_round2.md` replaces the round-1
instruction with a derivability checklist, ships five worked `no` examples
from the round-1 disagreement rows, and a gate-only worksheet with the
model answer removed. Pre-registered bar: kappa ≥ 0.6 on the gate field
before the gate instrument is considered human-validated.

**Also this session:** F3 probe v2 (`evolution_probe_v2`) with 8 topical
distractor sessions per scenario; smoke shows semantic 5/5, verbatim 0/5,
summary 3/5 — the degeneracy is gone, but 15 turns vs top-10 leaves gold
recall at 1.0, so the full run needs a tighter context budget before any
stage-distribution claim.

## 2026-10-26 — Round-2 gate annotation fails; abstention correction generalized to n=200

**1. Round-2 gate annotation cleared nothing.** Two sheets returned; kappa
0.181 (agreement 0.627, n=177) against the pre-registered bar of 0.6.
Marginals differ sharply: annotator 1 said yes 99 / no 101 / uncertain 0;
annotator 2 said yes 155 / no 22 / uncertain 23. The decisive diagnostic is
that 81 of annotator 1's 101 "no" notes are the same sentence, "Missing fact:
`<token>` is not stated in the evidence", where the token is lifted from the
reference answer (75/81) and absent from the evidence (0/81). The tokens
include "she", "because", "likely", "herself". That is not the derivability
checklist applied fact by fact; it is a template that treats any unseen token
as a missing fact. Verdict: the human gate is still not operational; E0 levels
remain non-citable, and the round-2 instruction rewrite is not the fix. A
third attempt should change the task shape (per-fact binary rows, or a
deterministic decomposer validated on the 200 adjudicated rows), not the
wording.

**2. Abstention correction: from ad-hoc to reproducible and guarded.**
The committed n=50 correction had no script. `experiments/abstention_correct.py`
now reproduces it exactly: 28 flips, accuracy 0.260/0.280/0.200, and every
`answer_failure_type` identical to `results/_corrected_comparison_n50.jsonl`
(0 diffs across all 150 mode-cells). The flip is label-only and recomputes the
failure type with the frozen `evaluation.attribution.attribute_failure` path.

**3. The naive rule is only 52% precise; the reference-answer guard fixes it.**
Human adjudication sampled 25 abstention-style stored-correct rows. Twelve are
human-correct, and all twelve are LongMemEval `_abs` questions whose reference
answer is itself an abstention ("The information provided is not enough. ...").
So "abstention ⇒ wrong" mislabels half the sample. Guarding on the reference
answer — flip only when the gold answer is concrete — gives 13/13 precision and
12/12 preservation on the sample (precision and recall 1.0). The guard is now
in the script and covered by tests.

**4. Corrected n=200 tables (no API, label-only).** Using canonical semantic
accuracy on judged rows: LoCoMo real 0.405→0.306, oracle_memory 0.832→0.682,
oracle_context 0.852→0.761; E0 43→56, 15→40, 14→30. LongMemEval: real
0.521→0.479, oracle_memory 0.691→0.676, oracle_context 0.821→0.799; E0 10→13,
11→13, 13→15. The LoCoMo oracle ladder survives correction but the oracle rungs
absorb most of the extra E0 (14/25 and 16/28 new insufficient-evidence rows),
which is the cleanest statement yet that abstention inflated oracle accuracy.
Correction changes two paired conclusions: LoCoMo OM→OC goes from p=0.5413 to
p=0.0146 (last rung becomes significant), while LongMemEval OM→OC goes from
p=0.0414 to p=0.078 (last rung becomes non-significant). Stage-distribution
tests remain strong on corrected labels (all pairs p ≤ 0.0052 LoCoMo, ≤ 2.1e-7
LongMemEval).

**Artifacts:** `results/_corrected_comparison_{locomo,longmemeval}_n200.jsonl`,
`results/analysis_abstention_corrected_{locomo,longmemeval}_n200.json`,
`results/analysis_annotations_round2_diagnostic.json`. New code:
`experiments/abstention_correct.py`, `experiments/diagnose_gate_annotations.py`,
`tests/test_abstention_correct.py`. 197 tests pass.

### Round 3 — per-fact gate package (same session)

Two gestalt rounds failed for the same reason: the unit of judgement was the
whole row. Round 3 moves the unit to the atomic fact. `experiments/fact_specs.py`
decomposes each of the 200 reference answers into 276 facts (mean 1.38), with
alternative phrasings of the same value grouped as any-of (21 groups). Authoring
conventions: decompose the answer to the question, not incidental elaboration;
compound measures stay one fact; LongMemEval `_abs` golds become a positive
"evidence mentions X" fact plus a negative "evidence does not mention Y" fact.

Why this should fix the kappa failure: presence of a concrete proposition in a
fixed evidence block is an objective judgement, and the row gate is a transparent
aggregation (all required facts present; an any-of group needs one alternative).
The annotator never has to weigh "enough information" as a gestalt.

Design audit: among the 221 fact rows whose question was adjudicated sufficient,
only 6 have zero content-word overlap with the evidence; all six are either
negative facts (zero overlap expected) or paraphrase cases the README explicitly
accepts. One ambiguity was fixed before packaging (`locomo-038` "two cats" →
"cats", because the evidence names three cats — the missing item that matters is
the dog).

Artifacts: `round3_fact_presence.csv` (blinded), `round3_key.csv` (stored and
adjudicated labels for scoring only), `README_round3.md` (five worked examples).
Builder `experiments/build_fact_package.py`, scorer
`experiments/score_fact_annotations.py`, 9 tests. Acceptance: fact-level kappa
≥ 0.6 AND aggregated row-level kappa ≥ 0.6. 206 tests pass.

### Label-only ladder statistics and metric audit (2026-10-26, continued)

Added `experiments/analyze_ladder.py`, a no-call wrapper that combines the
per-mode summaries and stage-distribution tests already in `analyze_systems`
with paired McNemar/bootstrap on the same rows. Ran it on both label versions of
both n=200 runs.

The run exposed a metric error in the earlier corrected table: the canonical
headline is *semantic accuracy on judged rows* (the definition used by every
n=200 table in this log), not the fraction of all rows with
`semantic_correct == True`. The latter counts unjudged rows as wrong and
understated the corrected accuracies. Canonical corrected numbers: LoCoMo
0.306 / 0.682 / 0.761 (auto 0.405 / 0.832 / 0.852); LongMemEval 0.479 / 0.676 /
0.799 (auto 0.521 / 0.691 / 0.821). The E0 counts are unchanged.

Corrected paired contrasts: LoCoMo OM→OC p=0.0146 (auto 0.5413), LongMemEval
OM→OC p=0.078 (auto 0.0414); real→OM and real→OC remain highly significant on
both. Stage-distribution tests on corrected labels: all pairs p ≤ 2.1e-4
(LoCoMo) and ≤ 2.1e-7 (LongMemEval).

Also added `experiments/validate_abstention_rule.py`, which regenerates the
rule-validation numbers from the adjudicated sample: naive abstention rule
precision 0.52 / recall 0.42 on the 77 stored-correct rows; guarded rule
precision 1.00 / recall 0.42. On the 25 abstention-style rows the guard flips
13/13 human-wrong and preserves 12/12 human-correct. Recall on the full sample
is bounded at 0.42 because the other 18 human-wrong stored-correct rows are
non-abstention judge errors outside this rule's scope.

Drafted `docs/paper/instrument_honesty.md` with a number→artifact table. It
states the two failed gate rounds, the abstention correction and its validated
precision, the gate's near-independence from humans (kappa 0.07, recall 0.564,
the `_abs` 14/15 systematic error), and a three-rule reporting protocol. It
explicitly leaves the round-3 gate unvalidated.

## 2026-10-26 — Corrigendum: gate-vs-human confusion polarity

The 2026-10-25 report (and the STATUS/paper draft derived from it) said the
evidence gate "misses 65 truly-insufficient rows and calls 17 sufficient rows
insufficient". That is backwards. The eval artifact's positive class was
*sufficiency*, so its tp=84 / fp=17 / fn=65 read as: 17 gate-sufficient rows
that humans called insufficient (the gate MISSED 17), and 65 gate-insufficient
rows that humans called sufficient (the gate FALSELY FLAGGED 65). With
insufficiency as the positive class the matrix is tp=20, fp=65, fn=17, tn=84.

Correct statement: the gate **misses 17 truly-insufficient rows (all LoCoMo)**
and **falsely marks 65 sufficient rows insufficient (28 LoCoMo, 37 LongMemEval,
the latter dominated by `_abs`)**. Its dominant failure is over-flagging, so E0
is biased upward, not downward. Sufficiency-positive precision 0.832 / recall
0.564 remain correct as stated, and kappa 0.03–0.07 is unchanged.

Authoritative, regenerable artifact:
`results/analysis_gate_confusion_n200.json` via
`python -m experiments.analyze_gate_confusion`. Corrected in STATUS.md and
`docs/paper/instrument_honesty.md`; a regression test pins the polarity.

## 2026-10-26 — Round-3 per-fact gate passes; re-attribution with the human gate

Both round-3 sheets arrived complete (276 rows each). Pre-registered scoring
(`experiments.score_fact_annotations`):

- fact-level kappa **0.835** (agreement 0.970, n=234 co-decided; 42
  uncertain/blank)
- row-level kappa **0.889** with unresolved dates mapped to insufficient
  (n=200), **0.830** excluding them (n=172)
- both clear the 0.6 bar → **accepted**.

Consensus gate vs the 200 adjudicated labels: precision 0.837 / recall 1.000 /
F1 0.911 on 178 consensus rows, against the stored gate's 0.244 / 0.528 / 0.333
on the same rows. By benchmark the fact gate's F1 is 0.972 on LoCoMo (stored
0.450) and 0.286 on LongMemEval (stored 0.059); LongMemEval precision is low
only because the positive class is a single row in 88 — in absolute terms the
fact gate flags 5 false-insufficient rows vs the stored gate's 32. The
decomposition was authored with access to the adjudicated labels, so the
inter-annotator kappa is the independent evidence; the adjudication comparison
is corroboration.

`experiments.regate_with_human_gate` then re-attributes failures using the
consensus gate on covered questions and the stored gate elsewhere. Coverage is
98/100 LoCoMo and 94/100 LongMemEval annotated questions (the remaining 8 are
row-level annotator disagreements). E0 (already abstention-corrected) moves:
LoCoMo real 56→51, OM 40→30, OC 30→25; LongMemEval real 13→5, OM 13→8, OC 15→8.
The removed E0 rows become F1/F4/F6 or RC, with the largest shift on
LongMemEval `_abs`, as the audit predicted. The n=50 fingerprint has only 20/50
questions covered, so its re-gated E0 is a sensitivity check (semantic 18→16,
summary 16→17, verbatim 16→17), not a replacement; the fingerprint's
stage-distribution claim rests on failure labels and is unaffected.

Artifacts: `results/analysis_annotations_round3.json`,
`results/analysis_regate_{locomo,longmemeval}_n200.json`,
`results/analysis_regate_locomo_n50.json`. Tests: 214 pass.
