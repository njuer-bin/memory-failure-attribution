# Status Drift in Long-Term Conversational Memory — Research Plan v2.0

**Title:** Status Drift in Long-Term Conversational Memory: Measuring Epistemic and Intentional Fidelity under Recursive Compression  
**Chinese:** 长时对话记忆中的状态漂移：递归压缩下的认知与意图保真度测量  
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

## 6. Key controls

- Same writer model and generation settings across conditions.
- Same judge model and classification schema across conditions.
- Save full dialogue, every intermediate memory, prompts/configuration, raw judge responses, and errors.
- Use the same final-status gold label for all conditions.
- Include legitimate state transitions and test whether the system follows the later evidence.
- Treat LLM judging as provisional; manually adjudicate outputs before scientific claims.
- Record approximate character/token budgets. A strict matched-budget experiment is a later-stage requirement.

## 7. Metrics

- Raw Status Accuracy.
- One-shot Status Accuracy.
- Recursive Status Accuracy by depth.
- Direct-from-source Status Accuracy by target depth.
- Proposition Retention Rate.
- Content-Preserved Status Distortion Rate (CPSD): status errors among outputs judged to retain the proposition.
- Legitimate Transition Accuracy.
- Per-dimension and per-transition confusion counts.
- Recursive-minus-direct paired error difference.

Always report proposition omission separately from status distortion. Never improve CPSD by silently excluding omitted propositions without also reporting the omission rate and denominators.

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

## 10. Research integrity

- No fabricated results or references.
- No universal claims from a single local model.
- No conflation of legitimate user updates with compression drift.
- Preserve raw outputs and failed cases.
- Distinguish official implementations from simplified reproductions.
- Do not claim novelty until full-text and appendix comparison is complete.
