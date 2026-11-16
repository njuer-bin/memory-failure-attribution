# V3 Paired Transformation Experiment Protocol
**Status:** Draft protocol for calibration. Freeze version and hash before confirmatory data generation.

## 1. Objective
Estimate whether transformation history changes state fidelity beyond proposition loss and storage budget, and whether the result survives blind human evaluation.

## 2. Experimental unit
One trajectory = source dialogue + target proposition + evidence-bearing turns + gold final state. All applicable conditions are generated from the same trajectory. The trajectory, not each individual memory, is the clustering unit for inference.

## 3. Conditions
A. RAW: original dialogue supplied directly to the evaluator.  
B. DIRECT: one writer call from full dialogue to final memory at target budget B.  
C. RECURSIVE: first write from full dialogue, then rewrite the previous memory for K stages; final target budget B.  
D. REWRITE_MATCHED: same number of writing calls as RECURSIVE, but intermediate target budgets are held at a predeclared constant or schedule matched to the recursive condition. This is a mechanism control, not assumed equivalent by name.  
E. RETRIEVAL: retrieve selected original evidence snippets under a fixed retrieval budget. Treat as a distinct strategy.  
F. STRUCTURED_STATE (optional): explicit structured state representation with evidence links. Keep optional until implementation and evaluation rules are frozen.
G. PATH_REPLICATE: multiple predeclared intermediate schedules under the same condition, same source and final budget. This is the primary unit for within-condition path divergence.
H. SOURCE_PEEK: chained rewriting that can access both the prior memory and the original dialogue. Separates transformation history from source availability.
I. REPEATED_DIRECT: d independent direct compressions of the full dialogue, keeping the last. Matches call count without chaining.

P1b evidence: schedule-only PATH_REPLICATE variation is nearly null (9.1% pairwise divergence), while source access (~50–58%), prompt paraphrase (25–45%), and temperature sampling (27–82%) drive divergence. Treat schedule-only as a near-null control; use SOURCE_PEEK, prompt paraphrase, and deterministic-vs-sampled decoding as the primary path perturbations.

## 4. Controls to record
For every generation:
- trajectory_id, condition, stage, parent_memory_id;
- exact source access (full dialogue / prior memory / retrieved evidence);
- writer model name and version, prompt hash, decoding parameters, seed if supported;
- target budget, actual input/output tokens, tokenizer identifier;
- timestamp, completion status, retry count, error;
- raw prompt, raw completion, and intermediate artifact.
No result may be dropped because it is inconvenient or outside a target token band. Retries and failed generations are retained in an audit log.

## 5. Budget design
Use at least two predeclared budget levels if feasible. Select budgets from pilot distributions before the confirmatory run. The primary analysis is intention-to-treat by assigned budget condition, using actual token count as a covariate or descriptive exposure. A post-hoc matched-token subset may be shown only as sensitivity analysis and must be labeled as selection-conditioned.

Concrete assignment rules (to be frozen in P0):

- Final budget B is fixed per trajectory before generation.
- Each path schedule is predeclared (e.g., 220→180→140→120→100; 220→200→160→130→100).
- The writer receives the same prompt template across schedules; only the intermediate budgets differ.
- Report achieved tokens per stage and per condition; never select outputs into a token band as the primary analysis.
- If a stage fails, keep the failure in the audit log; do not re-roll until a convenient length appears.

## 6. Trajectory composition
Balance across:
- epistemic, intentional, and conditional dimensions;
- stable states and evidence-supported updates;
- positive and negative polarity;
- explicit and paraphrased state cues;
- short and long evidence distance;
- distractor density;
- update types, including cancellation and reversal.
Use templated synthetic trajectories for controlled coverage first. Any real-dialogue extension requires licensing, privacy, and annotation suitability review. Avoid generating all examples from one narrow template family.

## 7. Randomization and blinding
Randomize condition order per trajectory and anonymize outputs with opaque IDs. Annotators must not see condition names, prompts, model names, gold state, evidence-turn IDs, or other annotators' labels. Keep the condition key and gold file access-controlled until annotation is locked.

## 8. Human evaluation
Two independent annotators label proposition identity, represented state, evidence support, status omission, ambiguity, and drift subtype. A third adjudicator resolves disagreements. Annotators may mark UNASSESSABLE and explain why. Do not force a label when evidence is insufficient.

## 9. Primary and secondary outcomes
Primary:
- **joint outcome distribution** of proposition identity × status fidelity (unconditional);
- paired Recursive − Direct difference at each predeclared budget, reported alongside the joint outcomes;
- within-condition **path divergence** among PATH_REPLICATE paths (pairwise state disagreement and dispersion).
Key secondary:
- USDR among PRESERVED propositions (conditioned; not interpreted alone);
- proposition loss and partial identity;
- status omission without a changed state;
- legitimate update accuracy;
- drift subtype by dimension;
- evidence traceability;
- actual token and latency cost.
Report counts and denominators for every condition and dimension.

## 10. Exclusion rules
Predeclare exclusions: corrupted source, missing target proposition in source, irrecoverable generation failure, or malformed artifact that cannot be evaluated. Do not exclude based on observed label, length, condition performance, or model-judge score. Report all exclusions by reason and condition.

## 11. Pilot versus confirmatory
Calibration pilot may change labels, prompts, or conditions. Once protocol is frozen, confirmatory trajectories and analysis code are versioned and not modified based on interim outcomes. If a change is unavoidable, create a new protocol version and separate confirmatory cohort.

## 12. Reproducibility package
Publish synthetic source trajectories where permitted, prompts, config, intermediate memories, final outputs, annotation forms, adjudication records, analysis scripts, package versions, and checksums. Redact secrets and personal data. Record local model runtime and hardware.
