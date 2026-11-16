# Status Drift in Long-Term Conversational Memory — Research Plan v2.1

**Title:** Status Drift in Long-Term Conversational Memory: Measuring Epistemic, Intentional, and Conditional Fidelity under Recursive Compression  
**Chinese:** 长时对话记忆中的状态漂移：递归压缩下的认知、意图与条件保真度测量  
**Status:** Research proposal; hypotheses are untested.  
**Current phase:** Literature audit and small-scale pilot.  
**Branch:** `research/status-drift-v2-pilot`

## 1. Research objective

This project studies whether repeated compression and consolidation of multi-turn conversational histories changes the epistemic, intentional, or conditional status attached to a proposition.

We call a transformation **Conversational Memory Status Drift** only when:
1. the proposition remains identifiable (fully or substantially);
2. its epistemic, intentional, or conditional status changes; and
3. the change is not supported by later conversational evidence.

A genuine user update is a legitimate state transition, not a compression error.

The project does not claim that uncertainty preservation, belief-state memory, provenance tracking, or plan lifecycle management are new. Closely related work includes HELM, ProgMem, BELIEFMEM, and Answer Bubbles. Their full methods and appendices must be checked before making a novelty claim.

## 2. Research questions

- **RQ1 — Measurement:** Is status drift measurable separately from proposition omission under conversational memory compression?
- **RQ2 — Recursion:** Does recursively compressing an existing memory produce additional drift compared with compressing the complete original dialogue once?
- **RQ3 — Behavioral impact:** Can a controlled change to status, while holding proposition content fixed, alter downstream agent decisions?

## 3. Scope

Primary dimensions:
- **Epistemic status:** possible / probable / certain / unknown (pilot currently uses possible vs certain).
- **Intentional status:** considering / intending / committed / explicitly not intended (pilot currently uses considering vs committed).
- **Conditional structure:** active unsatisfied-or-unknown condition vs condition explicitly satisfied.

Provenance is an auxiliary evidence variable, not a primary dimension in the first pilot.

## 4. Hypotheses (not findings)

- **H1:** Compression strategies differ in status preservation.
- **H2:** Recursive compression may add status drift beyond one-shot compression.
- **H3:** Proposition retention does not guarantee status retention.
- **H4:** Status-only corruption may independently alter downstream decisions.

Null results are valid and must be reported.

## 5. Pilot design

The initial pilot uses controlled Chinese multi-turn trajectories generated from fixed templates. It is a pipeline and phenomenon check, not a confirmatory benchmark.

Each trajectory contains:
- a target proposition;
- an initial status statement;
- unrelated conversational distractors;
- either no status update or an explicit evidence-supported update;
- a gold final status and evidence-turn identifiers.

Conditions:
1. **Raw:** classify the full original dialogue.
2. **One-shot:** compress the full dialogue once.
3. **Recursive D1/D2/D3/D5:** compress the full dialogue once, then repeatedly compress the previous memory.
4. **Direct-from-source control:** for each target depth, generate a final memory directly from the full original dialogue. This helps separate recursive effects from the effect of simply running a writer multiple times.

The initial runner defaults to six trajectories (two per dimension) for a smoke test. Expand to 30 trajectories only after inspecting the prompts, outputs, and labels. Do not infer population-level effects from this pilot.

## 6. Key controls (revised in protocol v2.4)

- Same writer model and generation settings across direct and recursive conditions.
- Save full dialogue, every intermediate memory, prompts/configuration, raw judge responses, errors, and per-memory character/UTF-8-byte lengths.
- Use the same evidence-supported final-state gold label across conditions.
- Include stable trajectories and legitimate state updates; never count an evidence-supported update as compression drift.
- Keep topic mention, proposition identity, polarity, epistemic status, intention, action execution, and condition satisfaction as separate annotation fields.
- Treat LLM-judge outputs and lexical/rule-based checks as diagnostics. Human adjudication is required for primary status-drift claims.
- The runner now fingerprints run configuration and refuses incompatible resume operations.
- Character/byte lengths are recorded, but token-matched budgets are not yet implemented. Direct, recursive, and rewrite-matched results must not be interpreted as a pure recursion effect without further budget control.

## 7. Metrics (revised in protocol v2.4)

- Status accuracy and legitimate-update accuracy by condition and dimension.
- Topic Mention Rate (lexical diagnostic only).
- Human-adjudicated Proposition Identity Retention, with PRESERVED, PARTIAL, LOST, and AMBIGUOUS reported separately.
- Human-adjudicated Status Fidelity among outputs whose proposition identity is PRESERVED.
- **Unsupported Status Drift Rate (primary):** proportion of proposition-preserved outputs whose status differs from the evidence-supported final state without later dialogue support.
- Omission Rate, reported separately.
- Paired recursive-minus-direct error differences, with raw counts and denominators.
- LLM-judge provisional status-error metrics, explicitly labelled as provisional and never substituted for the primary human-adjudicated measure.

The runner's cpsd_judge_provisional is not confirmatory CPSD because its denominator depends on the same LLM judge's proposition_retained decision. The lexical status_error_given_topic_mention metric is also not semantic proposition retention. See docs/STATUS_DRIFT_PILOT_PROTOCOL.md and docs/STATUS_DRIFT_V2_4_ANNOTATION_GUIDE.md.

## 8. Decision gates

Proceed to a larger pilot only if:
- outputs are parseable and the pipeline is reproducible;
- manual review confirms that the judge can distinguish the labels;
- at least some candidate cases retain the proposition while changing status;
- results are not dominated by omission or judge failure.

If recursive compression does not add drift over direct compression, revise or reject H2. If apparent drift disappears after manual adjudication, revise the measurement method. If the effect appears only for one model/prompt, narrow the claim.

## 9. Later stages

### Stage A — Benchmark
Expand to 300–500 high-quality multi-turn trajectories, subject to annotation cost and power analysis. Include real dialogue data only after checking licenses and suitability. Use at least two annotators and adjudication.

### Stage B — Controlled behavioral intervention
Compare Gold Memory, Status-corrupted Memory, and Naturally Compressed Memory on simulated actions only. Separate historical-state inference from current authorization. Candidate actions: mock purchase, mock appointment, mock email, mock cancellation. No real-world side effects.

### Stage C — Mitigation
Only after the phenomenon is established, test evidence-anchored status preservation. Compare against schema-only and verbatim-evidence-retention baselines under matched storage/token budgets.

## 10. Revision history

- **v2.4:** separates topic mention from proposition identity; defines human-adjudicated unsupported status drift as the primary outcome; adds an annotation guide/template; labels LLM-judge CPSD as provisional; adds run-configuration fingerprint checks and per-memory character/byte logging. This is a protocol/code revision, not a claim that v2.4 experiments have been run.

## 11. Research integrity

- No fabricated results or references.
- No universal claims from a single local model.
- No conflation of legitimate user updates with compression drift.
- Preserve raw outputs and failed cases.
- Distinguish official implementations from simplified reproductions.
- Do not claim novelty until full-text and appendix comparison is complete.
