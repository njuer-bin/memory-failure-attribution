# Status Fidelity Under Chained Memory Rewriting: Omission, Distortion, and Downstream Behavior

*Draft v0.1 — 2026-11-18. Numbers are taken from the frozen V3/P4.2 artifacts;
references are draft placeholders and must be verified before submission.*

## Abstract

Long-term conversational agents compress dialogue into memory. The same
proposition can survive compression while the stance attached to it disappears.
We introduce a proposition-controlled diagnostic for **status fidelity**: the
epistemic, intentional, or conditional state attached to a proposition,
measured across paired transformation histories with proposition identity held
fixed. In a 30-trajectory paired study with 330 blind human-labeled memories,
chained rewriting omitted the status of 44-54% of proposition-preserved
memories, while unsupported distortion was rare (3/330). Rewrite-matched and
repeated-direct controls isolate chained re-editing from intermediate budget and
raw call count; giving the writer access to the source removes the omission.
Downstream, distortion robustly raises unauthorized action (P4: 66.7% vs 6.7%;
P4.2: 23.7% and 21.1% vs 0%). Omission's profile is task-dependent: conservative
under-action in a synthetic decision task, but over-action in high-stakes
authorization when the agent fills the missing status from a bare mention or the
current request. Source access is the strongest mitigation; a status-aware
prompt is partial and non-additive. A real-dialogue feasibility audit shows
intentional status is findable and gold-codeable, but the LSF/SSF annotation
instrument fails calibration; we report that as a measurement lesson. The
ingredients are prior work; the contribution is the status-specific,
proposition-controlled diagnostic and the separation of omission from
distortion.

## 1. Introduction

A user says: "I'm still comparing standing desks; the Fully Jarvis is $480, but
I'm not sure yet." A later memory says: "The user mentioned buying the Fully
Jarvis standing desk." The fact survives; the stance does not. An agent that
reads the second memory may order the desk.

Memory evaluation usually asks whether a fact was recalled. It rarely asks
whether the *status* of that fact survived: whether the user was considering,
intending, committed, or conditional; whether a condition was satisfied; whether
the speaker was certain or merely hypothesizing. We call this **status
fidelity**. It is a distinct measurement target from proposition recall, and it
matters whenever a downstream action depends on authorization.

This paper asks three questions. First, when the same dialogue is rewritten
through different memory transformation histories, does the status survive when
the proposition does? Second, if status is lost, is the loss an omission (the
status is absent) or a distortion (the memory asserts an unsupported status)?
Third, do status-only differences change downstream decisions?

We answer with a proposition-controlled paired design. The same evidence is
compressed under direct, recursive, rewrite-matched, repeated-direct, and
source-peek histories; proposition identity is held fixed; two blind annotators
label proposition identity, status, and evidence support. We then construct
memory variants that differ only in status and place them in a sandboxed
downstream decision task.

The main findings are:

- Chained rewriting causes **status omission**: 44-54% of proposition-preserved
  memories lose the status, versus 3.7% for direct compression.
- The mechanism is **repeated re-editing of the writer's own output**, not
  intermediate budget shrinkage or raw call count. Rewrite-matched equals
  recursive; repeated-direct behaves like direct; source access removes the
  omission.
- **Distortion is the robust behavioral harm.** It raises unauthorized action in
  both the synthetic P4 task and the stricter English P4.2 bank. **Omission is
  not a safe failure in general**: it is conservative in P4 but can produce
  over-action in high-stakes authorization when the agent fills the missing
  status.
- **Source access is the strongest mitigation** in the primary model; a
  status-aware prompt is partial and non-additive.
- The real-dialogue arm is a **feasibility and measurement contribution**:
  intentional status is findable and gold-codeable, but the LSF/SSF annotation
  instrument fails calibration and is reported as future work.

The individual ingredients are prior work. State tracking, structured belief
states, recursive-summarization omission, source access, and memory-to-action
effects have all been studied. The contribution is the status-specific,
proposition-controlled combination and the separation of two failure modes that
have opposite behavioral profiles.

## 2. Related Work

**State tracking versus recall.** StateMem/StateMemBench frames state tracking
as distinct from recall and studies current versus superseded state, including
five failure modes and human plus judge labels (arXiv:2608.19652). Our unit is
similar—a proposition plus its current state—but we hold proposition identity
fixed and vary the transformation history. StateMem does not test rewriting
histories or a status tuple.

**Structured state and belief revision.** ProgMem studies structured memory
programs for temporal updates, plan changes, and uncertainty (Findings of AACL
2026). BELIEFMEM studies AGM belief revision with a history-preserving belief
base (Findings of EMNLP 2026). Both establish that structured state
representation and belief revision are prior work. We do not claim the state
tuple or belief revision as a method contribution; we measure whether a
status survives ordinary compression.

**Recursive summarization and chained rewriting.** ABBEL diagnoses omission and
incorrect updates under recursive summarization into natural-language belief
states (arXiv:2512.20111). ReSum studies periodic recursive context
summarization (arXiv:2509.13313); LightMem studies a compression lifecycle with
topic-aware short-term memory and sleep-time consolidation (arXiv:2510.18866);
Supersede rewrites a bounded notes memory per session and shows that failure
grows with conversation length rather than compression ratio
(arXiv:2606.27472). Recursive-summary omission and chained-rewriting harm are
therefore prior work. Our claim is status-specificity: the proposition survives
while the stance is dropped, and omission is separated from unsupported
distortion.

**Source access and raw history.** LiveCtx preserves raw history and retrieves
evidence at query time (Discover Computing, 2026). Source access is not a novel
idea. We use it as a mechanism control and as a mitigation: if exposing the
source during rewriting removes status omission, the loss is a property of
chained re-editing, not of compression per se.

**Stale state and memory-to-action.** STALE studies implicit stale state and
downstream policy adaptation (arXiv:2605.06527); StateAuditor studies
state-to-draft transition verification and response repair
(arXiv:2608.01619); MemTX studies transactional belief commit and action-safety
gating (arXiv:2607.23929); EAL-Bench measures false authority formed in memory
and propagated to unauthorized action (arXiv:2609.01836). Memory state → action
is prior work. Our downstream study is a controlled status-only intervention:
the proposition, evidence, request, rule, and length are fixed; only the
represented status changes.

**Interventions.** TWIST evaluates intervention quality at belief change points
with human validation (arXiv:2609.28575). We do not claim to introduce
belief-change intervention. Our mitigation comparison (prompt versus source
access) is a practical question about where to intervene in a rewriting
pipeline.

**Position.** The paper is a controlled diagnostic, not a new architecture. The
closest prior work already covers state tracking, structured state, recursive
summarization, source access, and memory-to-action effects. The defensible
contribution is the combination: a status tuple measured across paired
transformation histories with proposition identity fixed, blind human labels,
an omission/distortion split, a status-only downstream intervention, and a
second-model replication.

## 3. Definitions and Measurement

### 3.1 Unit of analysis

For each item we define:

- `P`: the target proposition, a testable claim about the speaker's own action,
  state, or belief.
- `E`: the minimal evidence span in the source dialogue (session and turn ids,
  with surrounding turns needed to interpret `P`).
- `H`: the transformation history applied to `E` (direct, recursive,
  rewrite-matched, repeated-direct, source-peek, raw reference).
- `M`: the resulting memory text shown to the annotator or the agent.
- `t`: the evaluation time. The gold status is the latest state supported by `E`
  up to `t`, including legitimate updates.

A status change supported by later evidence is a legitimate update, not drift.
The gold status is not "the first thing said."

### 3.2 Status tuple

We reuse the typed state:

`S(p,t) = (epistemic, intentional, conditional, action, polarity, scope, time)`

The three dimensions studied here are:

- **Epistemic**: `UNKNOWN`, `POSSIBLE`, `PROBABLE`, `SUPPORTED`, `ESTABLISHED`,
  `REJECTED`.
- **Intentional**: `NOT_EXPRESSED`, `CONSIDERING`, `INTERESTED`, `INTENDING`,
  `COMMITTED`, `EXECUTING`, `COMPLETED`, `CANCELLED`, `NOT_INTENDED`.
- **Conditional**: condition state (`UNKNOWN`, `ACTIVE_UNSATISFIED`,
  `SATISFIED`, `FAILED`, `WAIVED`, `NOT_APPLICABLE`) and action state stored
  separately.

A satisfied condition does not imply a committed action. A conditional memory
can preserve the condition and lose the action, or the reverse.

**Table 1. Status tuple and reported outcomes.**

| Component | Values / definition |
|---|---|
| Epistemic | UNKNOWN / POSSIBLE / PROBABLE / SUPPORTED / ESTABLISHED / REJECTED |
| Intentional | NOT_EXPRESSED / CONSIDERING / INTERESTED / INTENDING / COMMITTED / EXECUTING / COMPLETED / CANCELLED / NOT_INTENDED |
| Conditional | condition state + action state, stored separately |
| Proposition identity | PRESERVED / PARTIAL / LOST / AMBIGUOUS |
| Status fidelity | correct / status omission / unsupported distortion / legitimate update / ambiguous |
| Downstream | EXECUTE / CONFIRM / REFUSE / DEFER / OTHER |

### 3.3 Outcomes

We report the joint distribution of proposition identity and status fidelity;
we never merge them into a single drift score.

- **Proposition identity**: `PRESERVED`, `PARTIAL`, `LOST`, `AMBIGUOUS`.
- **Status fidelity conditional on `PRESERVED`**: correct, status omission,
  unsupported distortion, legitimate update, ambiguous.
- **Unsupported Status Drift Rate (USDR)**: unsupported status changes among
  proposition-preserved outputs.
- **Proposition Loss Rate (PLR)**: identity lost or materially incomplete,
  reported separately.
- **Legitimate Update Accuracy (LUA)**: correct representation of an
  evidence-supported state transition.
- **Downstream Decision Error (DDE)**: unauthorized action, under-action,
  clarification, or abstention in a sandboxed task.

### 3.4 Controls

The paired design uses the same source trajectories, writer family, and
predeclared budgets across conditions:

- **Direct**: one compression of the original dialogue.
- **Recursive**: repeated rewriting of the previous memory, with a shrinking
  budget schedule.
- **Rewrite-matched**: repeated rewriting with constant intermediate budgets,
  separating chaining from budget shrinkage.
- **Repeated-direct**: independent direct compressions, keeping the last;
  matches writer-call count without chaining.
- **Source-peek**: chained rewriting with access to both the previous memory and
  the original dialogue.
- **Raw**: full dialogue reference, not a compressed-memory condition.

### 3.5 Human labels and reliability

Two annotators label proposition identity, status, evidence support, and
ambiguity under a calibrated guide. Model judges are diagnostic only; they are
never the primary instrument. The P3 annotation used a collapsed ontology after
a calibration round; primary-judgment agreement is reported with Cohen's kappa,
and disagreements are adjudicated. For the real-dialogue arm, the gold-coding
calibration passes after third-person adjudication; the LSF/SSF instrument is
reported as failed calibration, not as a reliability claim.

## 4. Study 1: Chained Rewriting Omits Status

### 4.1 Design

We generated 30 trajectories across five topics and three status dimensions,
with stable and updated variants. Each trajectory was generated under ten
conditions plus a raw reference:

`raw`, `direct`, `recursive`, `rewrite_matched`, `repeated_direct`,
`source_peek`, `para`, `temp1`, `temp2`, `path_s2`, `retrieval`.

The writer was `qwen2.5:7b` with a neutral prompt and a final budget of 100
characters; seeds were 42 and 43. The generation gate required 30/30
trajectories, 300/300 generated conditions, zero errors, and no empty finals.
The P3 blind set contains 330 items: 30 trajectories × (10 generated conditions
+ raw), balanced across dimensions, gold statuses, and conditions.

*[Figure 1 about here: design, conditions, and the status tuple.]*

### 4.2 Main result: omission, not distortion

Two independent annotators labeled every item. Primary-judgment raw agreement
was 0.967 with Cohen's kappa 0.944; proposition identity 0.991/0.943;
action status 0.961/0.924; expressed status 0.991/0.989; evidence support
0.988/0.972; primary dimension 1.000.

Among the 300 proposition-preserved items, 88 are status omissions (29%).
Unsupported distortion is 3/330 (0.9%); on the 300 preserved items the USDR is
1.0%. The dominant failure is therefore omission, not distortion.

Table 2 reports omission among preserved items by condition.

**Table 2. Status omission among proposition-preserved items, by condition
(P3; 330 blind items, primary κ 0.944).**

| Condition | Omission among preserved |
|---|---:|
| Raw | 0.0% |
| Direct | 3.7% |
| Repeated-direct | 3.7% |
| Source-peek | 0.0% |
| Retrieval | 33.3% |
| Recursive | 44.4% |
| Rewrite-matched | 46.2% |
| Paraphrase | 54.2% |
| Temperature 1 | 42.3% |
| Temperature 2 | 51.9% |
| Path schedule 2 | 53.8% |

*[Figure 2 about here: omission among preserved items by condition, with paired
intervals.]*

The dimension breakdown among preserved items is conditional 27.6%, epistemic
33.0%, and intentional 27.3%. The earlier v2 pattern that intentional commitment
cues are uniquely vulnerable does **not** replicate in the V3 blind human
labels.

### 4.3 Mechanism: chaining, not budget or call count

We predeclared three controls. Rewrite-matched holds intermediate budgets
constant and recovers the same degradation as the shrinking schedule
(paired omission difference 0.000 [−0.167, 0.167]). Repeated-direct matches the
writer-call count but behaves like direct (−0.367 [−0.567, −0.167]).
Source-peek, which exposes the original dialogue at every rewrite, removes the
omission (−0.400 [−0.567, −0.233]). The mechanism is therefore repeated
re-editing of the writer's own output, not intermediate budget shrinkage or raw
call count.

This is also why the paper does not claim schedule-level "path dependence." A
within-condition schedule pilot was near-null (S1–S2 pairwise divergence 9.1%);
heterogeneous paths diverge mainly when they change information access or
decoding, not when they change the budget schedule. The robust contrast is
chained rewriting versus direct compression.

*[Figure 3 about here: paired mechanism contrasts (rewrite-matched vs
recursive, repeated-direct vs direct, source-peek vs recursive).]*

### 4.4 What is omitted

Omission is not random. The characteristic failure is a memory that keeps the
topic and the action but drops the stance: "confirming the laptop purchase" can
become "buying a laptop"; "decided to move to Shanghai" can become "mentioned
moving to Shanghai"; "I'll start learning Japanese" can become "learning
Japanese." The proposition survives; the commitment does not.

Unsupported distortion is rare but distinct. It includes strengthening a
consideration into a commitment, or treating an unsatisfied condition as
satisfied. Because the event count is small (3/330), condition-level contrasts
for distortion are uninformative; the behavioral study below is designed to
isolate its downstream effect.

### 4.5 Legitimate updates and proposition loss

A status change supported by later dialogue is a legitimate update, not drift.
The P3 adjudication contains 27 `LEGITIMATE_UPDATE` items, 30
`PROPOSITION_LOSS` items, and 3 unsupported distortions. Proposition loss is
reported separately: chained conditions lose 10-20% of propositions, so status
omission is not explained by proposition loss alone, but the joint distribution
must be reported.

## 5. Study 2: Downstream Behavior

### 5.1 P4: synthetic decision task

P4 uses 30 P2 trajectories and four memory variants: `present`, `omitted`,
`distorted`, and `no_memory`. The agent chooses `PROCEED`, `CONFIRM`, `ABSTAIN`,
or `OTHER` in a sandboxed task. The evidence supports execution only for
`COMMITTED` in the intentional dimension and `CERTAIN/ESTABLISHED` in the
epistemic dimension.

**Table 3. P4 downstream decisions (30 trajectories × 4 variants; qwen2.5:7b).**

| Variant | Unauthorized | Evidence-consistent | Clarify |
|---|---:|---:|---:|
| Present | 6.7% (2/30) | 93.3% (28/30) | 60.0% |
| Omitted | 0.0% (0/30) | 66.7% (20/30) | 100% |
| Distorted | 66.7% (20/30) | 0.0% (0/30) | 33.3% |
| No memory | 0.0% (0/30) | 66.7% (20/30) | 43.3% |

Paired vs present: omitted unauthorized −0.067 [−0.167, 0.000],
evidence-consistent −0.267 [−0.467, −0.067]; distorted unauthorized +0.600
[0.433, 0.767], evidence-consistent −0.933 [−1.000, −0.833]. In this task,
omission is conservative: the agent asks instead of acting, and the cost is
under-action. Distortion is harmful: the agent executes an unauthorized action
in two thirds of cases. The asymmetry replicates on `gemma3:12b` (distorted
20/30, present 0/30).

A separate agent-side failure appears under present status: 2/10 conditional
memories were read as decided and produced `PROCEED`. This is a conditional
collapse in the agent, not a memory-generation error, and is reported
separately.

### 5.2 P4.2: high-stakes authorization bank

P4.2 is a stricter, English, high-stakes replication. The bank contains 40
curated scenarios across money, health, authorization, and commitments; 36
over-commitment scenarios (26 intentional, 10 conditional) and 4
authorized-execution controls. Each scenario has `present`, `omitted`,
`distorted`, and `no_memory` variants. Proposition identity is checked by shared
content terms; length is matched with a neutral filler (token spread ≤3); the
authorization rule makes the expected decision determinate.

Two blind humans validated the bank. Pooled means were realism 4.113, status
clarity 4.975, rule clarity 4.950, distortion plausibility 4.250, and stake
severity 3.350; `only_status_differs` was 38/40 (0.950). Two scenarios were
excluded because the distorted variant changed scope, not only status
(`AUT-01`, `AUT-05`). The frozen bank has 38 scenarios and 152 items; the run
used 38 × 4 × 2 models = 304 calls on `qwen2.5:7b` and `gemma3:12b`.
Completeness was 152/152 per model, parse rate 1.000, and the four
authorized-execution controls executed 4/4.

**Table 4. P4.2 unauthorized execution by variant (38 scenarios; 304 calls).**

| Variant | qwen | gemma |
|---|---:|---:|
| Present | 0/38 | 0/38 |
| Omitted | 6/38 (15.8%) | 5/38 (13.2%) |
| Distorted | 9/38 (23.7%) | 8/38 (21.1%) |
| No memory | 0/38 | 0/38 |

*[Figure 4 about here: P4 and P4.2 unauthorized action, with the
over-commitment-only P4.2 inset.]*

Paired vs present: omitted +0.158 [0.053, 0.289] / +0.132 [0.026, 0.237];
distorted +0.237 [0.105, 0.368] / +0.211 [0.079, 0.342]. Under-action is zero
in both models because the authorized controls execute.

The pooled omission rate is inflated by the four controls: qwen executes 4/4
and gemma 2/4 when the omitted memory says only "the user mentioned X." In the
34 over-commitment scenarios, omitted is 2/34 and 3/34 (intervals touch zero),
distorted is 9/34 and 8/34, and distorted-minus-omitted is +0.206 [0.088, 0.353]
/ +0.147 [0.029, 0.265]. Conditional omission is 0/10 in both models;
conditional distorted execution is 2/10 (qwen) and 3/10 (gemma).

A control-wording probe replaced the four controls' omitted variants with
topic-only wording (no date, no request). Present remained 4/4 and distorted
0/4; omission over-action persisted at qwen 1/4 and gemma 3/4. The v1 control
effect is therefore not only lexical, but the imperative request remains a
confound.

### 5.3 Mechanism of unauthorized action

We coded all 32 unauthorized records from the reason text. Seventeen distorted
cases follow an explicitly authorizing memory (`D1_FOLLOWED_DISTORTED_MEMORY`).
The 15 omission cases assert an unstated commitment (`O1`, 6), upgrade a
mention (`O2`, 3), or use the current request as authorization (`O3`, 6). No
omission case executes while acknowledging that the memory lacks a status. The
two failure modes are mechanically different: distortion is following a false
memory; omission over-action is status fabrication.

### 5.4 Do not pool P4 and P4.2

P4 and P4.2 are different task families. P4 is a synthetic decision task with
short Chinese templates; P4.2 is a curated English authorization bank with
positive controls and matched length. The robust claim across both is that
distortion raises unauthorized action. The omission claim is task-dependent and
must be stated as such: omission is conservative in P4 but can produce
over-action in P4.2, concentrated in the controls and a few over-commitment
cases.

## 6. Mitigation

P5 asks which writer mitigation preserves status at matched budget. The
confirmatory design is a 2×2 crossing of prompt (neutral vs status-aware) and
source access (memory-only vs memory+source) on 30 P2 trajectories.

**Table 5. P5 confirmatory faithful status (30 trajectories; primary κ 0.974).**

| Condition | Faithful | Budget vs neutral |
|---|---:|---:|
| Neutral | 14/26 (0.54) | 1.00× |
| Status-aware prompt | 27/30 (0.90) | 1.05× |
| Source access | 30/30 (1.00) | 1.23× |
| Status-aware + source | 28/30 (0.93) | 1.38× |

*[Figure 5 about here: P5 faithful status by condition and the interaction.]*

Paired vs neutral: status-aware +0.433 [0.267, 0.600]; source access +0.533
[0.367, 0.700]; interaction −0.500 [−0.667, −0.333]. Source access is the
stronger mitigation; the prompt is partial; the combination is not additive.
In a gemma3:12b writer replication, the ranking shifts toward the prompt
(source 10/12, status-aware 11/12, combined 12/12). Report the model boundary,
not a universal mitigation.

## 7. Real-Dialogue Feasibility and Measurement Attempt

The real-dialogue arm asks whether the phenomenon can be studied outside
synthetic templates. A rule-based screen over LoCoMo and LongMemEval produced
2,135 candidate spans (intentional 1,123, epistemic 981, conditional 31); 725
are re-mentioned in a later session and 269 contain a potential change cue.
Intentional status is the viable real-dialogue dimension; epistemic is thin;
conditional is scarce.

A 40-item gold-coding calibration was built from a fresh set of items.
Two independent annotators labeled dimension and status. The unadjudicated
result passed dimension raw agreement but failed the kappa gate on three
boundary items; a third-person adjudication resolved them (instruction to the
assistant; past/emotional musing; completed action vs factual claim).
Adjudicated agreement is `gold_dimension` 1.000 / κ 1.000 and `gold_status`
0.975 / κ 0.969.

We then built a 45-memory LSF/SSF calibration sheet: 15 gold items (14
intentional, 1 epistemic) × direct/recursive/source-peek. LSF/SSF calibration
failed twice. Run 2, after fixing a target-turn focus bug and adding a cue
lexicon and SSF decision tree, reached LSF 0.800 / κ 0.689, SSF 0.756 / κ 0.625,
and proposition identity 0.800 / κ 0.607. The blocker is proposition identity:
memories replace the target speech act ("write" → "ask for advice"). LSF and SSF
are close to their gates, but the instrument is not reliable enough for a
confirmatory real-dialogue claim.

We therefore scope the real-dialogue arm to the feasibility audit and the
gold-coding calibration. The LSF/SSF failure is reported as a measurement
lesson and future work, not as evidence about memory systems. We do not claim
natural-dialogue replication or conditional reliability.

## 8. Discussion

**Two failure modes, two mechanisms.** Status omission is a representation
failure: the proposition is kept, the stance is dropped. Unsupported distortion
is a false-memory failure: the memory asserts a stance the evidence does not
support. They have different behavioral profiles. Distortion is the robust harm:
an agent that follows a false memory executes unauthorized actions. Omission is
the common failure, but it is not uniformly safe. In a synthetic decision task,
the agent asks instead of acting; in a high-stakes authorization task, the agent
can fill the missing status from a bare mention or the current request and
execute anyway.

**Why "omission is conservative" is not a law.** The P4 result was a
task-specific finding, and the P4.2 result shows the boundary. The relevant
variable is whether the task and request let the agent infer authorization from
something other than the memory status. When the request itself is imperative
and the memory retains the action, a missing status can become an implicit
authorization. Papers that report a single "status drift" effect would miss
this.

**Measurement.** Fact recall is not enough. A memory evaluation should report
proposition identity and status fidelity jointly, separate omission from
distortion, and state the task family for any downstream claim. The real-data
calibration shows that stance annotation is hard: cue lexicons, predicate
identity, and the distinction between underspecified and distorted need
explicit rules.

**Design.** Source access at rewrite time is the strongest mitigation in the
primary model. A status-aware prompt helps, but it is partial and can introduce
escalations when the source is available. The practical recommendation is to
expose the source during rewriting, and to treat prompting as a fallback.

## 9. Limitations

- The synthetic study uses templates and local 7B/12B models; it is a mechanism
  study, not a model-ranking claim.
- Unsupported distortion is underpowered in the rewriting study (3/330); P4.2
  has 17 unauthorized distorted cases. The "rare but harmful" framing depends on
  this event count.
- Human-label provenance is unrecorded; the real-data gold adjudication is
  third-person but not provenance-complete. Report reliability as
  annotator-unspecified where applicable.
- The real-dialogue LSF/SSF instrument failed calibration; the real-data arm is
  a feasibility and measurement appendix, not a confirmatory study.
- The conditional dimension is thin in real dialogue and is deferred.
- P4 and P4.2 are different task families; they are reported separately and
  must not be pooled.
- No formal power claim; the paired intervals describe precision at the
  observed sample sizes.

## 10. Conclusion

Status fidelity is a distinct measurement target for long-term memory. Chained
rewriting omits the status of a proposition while keeping the proposition
itself; distortion is rarer but behaviorally dangerous. Omission is common and
sometimes safe, but it is not a general guarantee: in high-stakes authorization,
a missing status can be filled by the agent and produce unauthorized action.
Source access is the strongest mitigation; prompting is partial. Real-dialogue
stance annotation remains an open measurement problem, and we report our failed
LSF/SSF calibration as a step toward it.

## References (draft; verify authors and venues)

- StateMem / StateMemBench. arXiv:2608.19652.
- ProgMem. Findings of AACL 2026.
- BELIEFMEM. Findings of EMNLP 2026.
- STALE. arXiv:2605.06527.
- StateAuditor. arXiv:2608.01619.
- MemDerive. arXiv:2610.25373.
- ABBEL. arXiv:2512.20111.
- Supersede. arXiv:2606.27472.
- LiveCtx. Discover Computing, 2026.
- ReSum. arXiv:2509.13313.
- LightMem. arXiv:2510.18866.
- MemTX. arXiv:2607.23929.
- EAL-Bench. arXiv:2609.01836.
- TWIST. arXiv:2609.28575.
- LongMemEval and LoCoMo (benchmarks; add full citations).

## Appendix A. Conditions and prompts

Describe the neutral writer prompt, the status-aware prompt, the source-peek
condition, and the downstream decision prompt. Include the exact prompts from
`experiments/status_drift_recursive_pilot.py` and
`experiments/v3_p4_2_bank.py`.

## Appendix B. Annotation guides and reliability

Summarize the V3 annotation guide, the P3 reliability table, the P4.2 validation
gates, the 40-item gold calibration, and the LSF/SSF failed calibration.
Include the say/do-not-say list from the novelty audit.

## Appendix C. P4.2 scenario examples

Include one over-commitment example and one authorized-execution control, with
the present/omitted/distorted variants and the expected decisions.

## Figure and table plan

- Fig. 1: design and conditions.
- Fig. 2: P3 omission by condition.
- Fig. 3: P3 mechanism contrasts.
- Fig. 4: P4 and P4.2 unauthorized action.
- Fig. 5: P5 mitigation.
- Table 1: status tuple and outcomes.
- Table 2: P3 omission by condition.
- Table 3: P4 decisions.
- Table 4: P4.2 unauthorized execution.
- Table 5: P5 faithful status.

*Numbers in this draft are taken from the frozen artifacts; before submission,
run a number audit against `research-state.yaml`, `findings.md`, and the run
notes. References require author/venue verification.*
