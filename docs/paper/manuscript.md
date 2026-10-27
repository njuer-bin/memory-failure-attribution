# Where Do Long-Term Memory Agents Lose Evidence?

**An audited attribution protocol, a corrected oracle ladder, and
architecture-conditional failure localisation**

*Markdown master draft, 2026-10-27. Target: COLING via ACL Rolling Review,
long-paper format (~8 pages of content + references + appendices). Venue
deadline unverified — web access is blocked from the work host. Every number
below was copied from the stored analysis artifacts listed in Appendix A, not
from memory; the label version (auto / abstention-corrected / human-gated) is
stated next to each number. LaTeX conversion, figures, and the bibliography
are pending.*

---

## Abstract

When a long-term memory agent answers incorrectly, accuracy benchmarks cannot
say where the failure happened. We present an attribution protocol that traces
each gold-evidence item through six lifecycle stages — formation, storage,
evolution, retrieval, context assembly, and answer reasoning — and localises
the **first observable evidence-loss boundary** (F1–F6), with an explicit
evidence-insufficiency label (E0) for questions the gold evidence cannot
support. Because an attribution claim is only as good as its instruments, we
audit ours against 200 human-labelled questions: the failure labels are 90%
human-confirmed, but the LLM judge systematically accepts abstention-style
answers (30.3% of sampled stored-correct rows are human-wrong), and the
automatic evidence gate is near-independent of human sufficiency judgements
(Cohen's κ 0.03–0.07) until rebuilt as a per-fact annotation task (κ 0.835).
We also show that the human *stage* annotation task is reliable (κ 0.897)
while the automatic first-loss label is not (human-vs-auto κ 0.59–0.71).
Applying the corrected instruments, we find that (i) the size of the
memory-induced loss is benchmark-dependent: the corrected real → oracle-memory
→ oracle-context ladder is 0.306 → 0.682 → 0.761 on LoCoMo (all rungs
significant) but 0.479 → 0.676 → 0.799 on LongMemEval (last rung not
significant); and (ii) on LoCoMo n=100, three memory systems with
statistically indistinguishable accuracy (0.407/0.423/0.429; paired McNemar
p = 0.736/0.728/0.864) fail at significantly different lifecycle stages
(Stuart–Maxwell, Holm-adjusted p ≤ 2.8e-4 on all three pairs). Two pre-registered architecture
ablations move each system's dominant failure stage in the predicted
direction — but below the pre-registered magnitude bar, so we report the
localisation as **architecture-conditional**, retract the stronger
universal-fingerprint framing, and show that stage-targeted repair does not
beat a no-op placebo. We release the protocol, the audit methodology, and all
analysis artifacts as a resource for studying memory-agent failure honestly.

---

## 1 Introduction

Long-term memory is becoming a standard component of LLM agents: conversation
history is written to a store, retrieved at answer time, and packed into the
model's context. Benchmarks such as LoCoMo and LongMemEval measure how well
such systems answer questions over long histories, but they report end
accuracy. When two systems score the same, accuracy alone cannot distinguish
*where* each one fails — a system that never wrote the fact looks identical to
one that wrote it and never retrieved it. Repair effort, and scientific
understanding, require localising the failure.

This paper asks a measurement question: **can the earliest point at which the
evidence for an answer becomes unobservable be located reliably, and does that
location characterise how a memory system fails?** Our answer is a qualified
yes — with the qualifications being, we argue, the more useful contribution.

We make four contributions:

- **C1 — An attribution protocol (§2).** A frozen pipeline that traces each
  gold-evidence item through six lifecycle stages (formation, storage,
  evolution, retrieval, context, reasoning) and labels every wrong answer with
  the **first observable evidence-loss boundary**: F1 formation, F2 storage,
  F3 evolution, F4 retrieval, F5 context, F6 reasoning-candidate, E0
  evidence-insufficient, or EVAL (instrument uncertainty). The label is an
  observability boundary, not a causal root cause; the protocol is explicit
  about what it does not establish.
- **C2 — A human audit of the instruments (§3).** Two annotators labelled a
  stratified 200-question sample. The failure labels are mostly sound (90%
  confirmed), but the audit surfaces three instrument defects that any
  LLM-judged memory study must handle: judge abstention false positives
  (30.3% of sampled stored-correct rows; a guarded correction rule is 13/13
  precise where a naive rule is 52%), an evidence-sufficiency gate that is
  near-independent of humans (κ 0.03–0.07) until rebuilt as per-fact binary
  annotation (fact κ 0.835, row κ 0.889, after two failed rounds), and a
  reliable human stage-annotation instrument (κ 0.897) against which the
  *automatic* first-loss label is unreliable (κ 0.59–0.71).
- **C3 — A corrected oracle ladder (§4).** Comparing real memory against
  oracle-memory and oracle-context controls quantifies how much of the loss
  memory causes — but only after abstention correction. The corrected ladder
  is steep and fully significant on LoCoMo (0.306 → 0.682 → 0.761) and
  shallower with a non-significant final rung on LongMemEval
  (0.479 → 0.676 → 0.799): the answer is benchmark-dependent, and corrections
  move individual rung conclusions in both directions.
- **C4 — Architecture-conditional stage localisation (§5).** On LoCoMo
  n=100, three memory systems with statistically indistinguishable accuracy
  fail at significantly different lifecycle stages: a fact-extraction system
  loses evidence at formation, a session-summary system at context assembly,
  a raw-turn RAG system at retrieval. Two architecture ablations that remove
  a system's own bottleneck move its dominant failure stage in the
  pre-registered direction (A1: F1 share 0.13 → 0.00, within-system
  Stuart–Maxwell p = 0.0031, accuracy unchanged; A3: F4 share 0.37 → 0.23,
  accuracy +17.6 points) — but both miss the pre-registered ≥20-point
  magnitude bar. The localisation is therefore real but conditional on
  architecture, not a universal invariant of memory agents.

We state three negative results up front, because they delimit what the
positive claims mean. **(N1)** The stronger claim we initially pursued — a
stable, *universal* failure fingerprint of memory agents — is **retracted**:
a pre-registered decision gate designed to test exactly that claim returned a
partial verdict, and the phenomenon is architecture-conditional. **(N2)**
Stage localisation is **not shown to be actionable**: a pre-registered
intervention that repairs the measured retrieval stage moved retrieval recall
0.043 → 0.321 but produced only +7 net answer flips (McNemar p = 0.143,
bootstrap CI [−0.029, +0.441]), inside the noise floor set by a no-op placebo
(9/35 flips). **(N3)** The automatic first-loss label produced by the
pipeline is **not reliable as a per-row instrument** (human-vs-auto κ
0.59–0.71); stage-distribution claims are made on failure labels that the
audit found 90% sound, at distribution level, not on per-row first-loss
reads.

The paper is organised as a measurement study. §2 defines the protocol; §3
audits the instruments and states the reporting rules we adopt; §4 and §5
present the two substantive results; §6 lists limitations; §7 gives
reproducibility detail, and Appendix A maps every claim to the artifact that
supports it.

## 2 The attribution protocol

### 2.1 Conditions

The protocol runs each benchmark question under up to three conditions:

- **Real Memory (RM).** The benchmark conversation is ingested by the real
  memory system; the answer is produced from retrieved context.
- **Oracle Memory (OM).** The gold evidence is written directly into a fresh
  store as raw turns and retrieved through the real retrieval/rerank/context
  path. Formation and storage are controlled (direct write) and reported as
  unmeasured; retrieval, rerank, and context are measured.
- **Oracle Context (OC).** The gold evidence is placed directly in the answer
  context. All stages before context are unmeasured.

The RM → OM → OC ladder isolates how much accuracy is recovered when
upstream stages are progressively perfectioned (§4).

### 2.2 Lifecycle stages and evidence matching

For each question, the benchmark provides gold evidence items with provenance
(session/turn identifiers). The tracer measures, at each stage, the recall of
the gold evidence in that stage's artifacts:

**formation → storage → evolution → retrieval → rerank → context.**

A gold item is matched by exact normalized text, or by token-overlap
similarity ≥ 0.55, among provenance-compatible artifacts. Provenance is a
constraint, not proof: an artifact whose turn conflicts with the gold
provenance cannot satisfy the item; a match in an artifact without provenance
is reported separately rather than hidden. Evolution (F3) is measured only on
datasets whose adapter exposes an atomic-fact store with supersession
(currently a controlled evolution probe); on the benchmark runs reported here
the stage is skipped and F3 cannot fire.

### 2.3 First observable evidence-loss boundary

*Terminology.* We report the **first observable evidence-loss boundary** —
the earliest stage at which the evidence required for the reference answer
stops being observable along the traced pipeline. We deliberately do **not**
call this a causal root cause: the boundary says where evidence became
unobservable, not which internal mechanism counterfactually caused the wrong
answer. (Where "first-loss" appears in code and artifacts it is shorthand for
this boundary.)

### 2.4 Answer evaluation and failure labels

Model answers are judged semantically against the benchmark reference, with
deterministic floors around the judge: pre-judge lexical support, post-judge
repair restricted to question-related candidates (never refusals), and a
false-overturn *ordering-refutation* layer for two-option ordering questions
whose evidence resolves the dates. Failure attribution then assigns, in
order:

1. semantically correct → no failure;
2. no semantic verdict → `EVAL_SEMANTIC_UNCERTAIN`;
3. evidence gate insufficient → `E0_EVIDENCE_INSUFFICIENT`;
4. gate not sufficient / low confidence → `EVAL`;
5. Oracle-Context mode → `RC_REASONING_CONTROL_FAILURE`;
6. no gold evidence ids → `E0`;
7. first measured stage missing gold → `F1`/`F2`/`F4`/`F5`;
8. all evidence present in context → `F6_REASONING_CANDIDATE`.

The evidence-sufficiency gate (E0) is judged **against the benchmark
reference answer, never the model prediction**, so it is non-circular. F6 is
a *candidate*: it means the evidence reached the context and the answer was
still wrong, which is consistent with a reasoning failure but also with
evaluation error — the audit of §3 quantifies both.

### 2.5 Label versions and reporting discipline

The audit (§3) shows the raw automatic labels carry measurable instrument
error. We therefore track three label versions and state, for every number,
which version it uses:

- **auto** — the stored automatic judge/gate labels;
- **abstention-corrected** — auto labels with the human-validated abstention
  rule applied (§3.3); used for all accuracy-level claims;
- **human-gated** — abstention-corrected labels with the E0 gate replaced by
  the two-annotator consensus gate on annotated questions (§3.4); used to
  re-attribute E0 on covered questions.

Accuracy is reported as *semantic accuracy on judged rows* (rows with a
judge verdict), never as the fraction of all rows marked correct, which
understates accuracy. E0 is reported only as a relative pattern across
conditions, never as an error-rate level, except where the human gate covers
the question.

### 2.6 What the protocol does not establish

Three boundaries are stated in the protocol itself: (i) labels are
observability boundaries, not causal mechanisms; (ii) F6 is a candidate
class, not a measured reasoning failure; (iii) per-row first-loss reads are
not validated as a per-row instrument (N3) — stage claims are made at the
distribution level, on labels whose failure direction the audit found 90%
sound.

## 3 Auditing the instruments

An attribution paper makes two kinds of claim: that an answer was wrong, and
that a particular lifecycle boundary was where the evidence first became
unobservable. Both rest on instruments — a semantic judge and an
evidence-sufficiency gate — and if those instruments are not audited, the
attribution map is a map of instrument error. This section reports the audit;
it absorbs and supersedes our earlier standalone instrument note
(`docs/paper/instrument_honesty.md`).

### 3.1 Audit design

Two annotators independently labelled a stratified 200-question sample (100
LoCoMo + 100 LongMemEval) drawn from the canonical n=200 runs, blind to the
stored verdicts; every disagreement was adjudicated. Fields: answer
correctness and evidence sufficiency. A separate 40-question package (two
further annotators) measured the reliability of *stage* annotation against
the automatic first-loss label (§3.5).

### 3.2 Answer correctness is measurable; failure labels are mostly sound

Inter-annotator agreement on answer correctness is high (κ = 0.92, n = 177
co-decided; the 7 disagreements were paraphrase/equivalence cases,
adjudicated correct). Against the adjudicated labels, the automatic judge
reaches precision 0.697 / recall 0.885 / F1 0.780 overall (κ = 0.591), with a
large per-benchmark gap: LoCoMo F1 0.605 (κ 0.369) vs LongMemEval F1 0.880
(κ 0.747).

The base rate that every stage claim rests on survives review: of 60
stored-incorrect rows with a human verdict, **54 (90.0%) are confirmed
wrong**. The direction of the failure labels does not rest on the gate.

### 3.3 The judge rewards abstention; a guarded rule corrects it

Of 66 sampled rows the judge stored as semantically correct, **20 (30.3%) are
human-adjudicated wrong**, and 13 of the 20 are abstention-style answers
("Not mentioned", "Cannot be determined") that the judge accepted. Left
uncorrected, semantic accuracy is inflated wherever a model declines to
answer — and the oracle conditions are inflated most, because they abstain
least often for the wrong reason.

The correction is label-only and human-validated. A naive rule ("a
stored-correct abstention is wrong") is only **52% precise** on the 25
sampled abstentions, because 12 are LongMemEval `_abs` questions whose
reference answer is itself an abstention. Guarding on the reference (flip
only when the reference is a concrete proposition) identifies **all 13
human-wrong abstentions and preserves all 12 human-correct ones** (precision
and recall 1.00 on the abstention subset). On the full 77-row stored-correct
sample the rule flips 13 of 31 human-wrong rows (recall 0.42); the remaining
18 are non-abstention judge errors the rule does not address — we do not
claim otherwise.

### 3.4 The evidence gate needed three rounds to become an instrument

The round-1 sufficiency field was degenerate (κ = 0.0: one annotator never
said "no"; all 20 disagreements adjudicated against the lenient side). A
round-2 derivability checklist still failed (κ = 0.181, n = 177): one
annotator's "missing fact" notes were a mechanical template lifting tokens
from the reference answer — 75/81 quoted tokens occur in the reference, 0/81
in the evidence, including function words ("she", "because"). Round 3 changed
the task shape: each reference answer is decomposed once into atomic
propositions (276 facts over 200 questions), and annotators mark one binary
fact-presence judgement per row; the row gate is a transparent aggregation.
This instrument cleared its pre-registered bar (κ ≥ 0.6 on both levels):

| measure | value | bar |
|---|---|---|
| fact-level κ (n = 234 co-decided) | **0.835** (agreement 0.970) | 0.6 |
| row-level κ, uncertain → insufficient (n = 200) | **0.889** | 0.6 |
| row-level κ, excluding uncertain (n = 172) | 0.830 | 0.6 |

Against the 200 adjudicated labels (178 consensus rows), the consensus gate
reaches precision 0.837 / recall 1.000 / F1 0.911, versus the stored gate's
0.244 / 0.528 / 0.333 on the same rows. Because the fact decomposition was
authored with access to the adjudicated labels, we treat the inter-annotator
κ as the independent validation and the adjudication comparison as
corroboration.

The stored automatic gate is near-independent of humans (κ 0.03–0.07). In the
direction that matters for E0, it **falsely marks 65 sufficient rows
insufficient** (28 LoCoMo, 37 LongMemEval — the latter dominated by `_abs`
questions, whose reference is itself an abstention) and **misses 17
truly-insufficient rows** (all LoCoMo): the error is dominated by
over-flagging. Consequently, E0 counts from the automatic gate are biased
upward and are used only for relative comparison across conditions of the
same question (one shared gate per question); on annotated questions we
re-attribute with the consensus gate, which removes 5–10 E0 rows per mode
(human-gated vs corrected labels: LoCoMo real 56 → 51, OM 40 → 30, OC 30 →
25; LongMemEval real 13 → 5, OM 13 → 8, OC 15 → 8), converting them to
F1/F4/F6/RC. Questions outside the annotated sample keep the stored gate and
the caveat.

### 3.5 The human stage instrument is reliable; the automatic first-loss label is not

A separate two-annotator package asked humans to assign the first
evidence-loss stage on 40 LoCoMo questions from the n=100 fingerprint run,
with full retrieval/context previews and an explicit "preview absence = stage
missing" rule. After a failed v1 (κ = 0.685 on valid rows; 13/40 rows used an
unmeasured label), the v2 instrument passed its pre-registered bar:
agreement 0.925, **multiclass κ = 0.897** (bar 0.70), no uncertain rows.

Against the human labels, the automatic first-loss label reaches only
κ = 0.705 (annotator a) and κ = 0.590 (annotator b). The disagreements
concentrate on E0 (humans call 4 rows E0 where the automatic trace assigns
formation/retrieval) and on rerank (humans see 3 rerank losses the automatic
label calls retrieval). **The human stage instrument is reliable; the
automatic first-loss label is not a per-row instrument.** All
stage-distribution claims in §5 are therefore made at the distribution level
on failure labels (90% human-confirmed, §3.2), not on per-row first-loss
reads.

### 3.6 Reporting rules we adopt and recommend

Three rules, which we follow throughout and suggest for any LLM-judged
memory-failure study:

1. **Floor first.** Ship deterministic, auditable rules for label dimensions
   that admit one (temporal equivalence, ordering refutation, abstention
   detection) before trusting a judge.
2. **Report the κ.** Every judge-derived dimension is reported with its human
   agreement; a dimension below the pre-registered bar is marked non-citable
   (for us: automatic E0 levels and per-row first-loss labels).
3. **Report both label versions.** Auto and corrected numbers appear
   together; the corrected number is the headline and the delta is the
   measurement error.

## 4 How much of the loss is memory? The corrected oracle ladder

The RM → OM → OC ladder (§2.1) quantifies how much accuracy is recovered when
formation/storage (OM) and then everything upstream of the answer (OC) are
perfectioned. Table 1 reports semantic accuracy on judged rows, n = 200 per
benchmark, on both label versions (§2.5).

**Table 1 — Oracle ladder, auto vs abstention-corrected labels (n = 200).**

| benchmark | labels | RM | OM | OC | RM→OM p | RM→OC p | OM→OC p |
|---|---|---|---|---|---|---|---|
| LoCoMo | auto | 0.405 | 0.832 | 0.852 | <1e-3 | <1e-3 | 0.541 |
| LoCoMo | corrected | **0.306** | **0.682** | **0.761** | 4.3e-12 | 2.3e-17 | **0.0146** |
| LongMemEval | auto | 0.521 | 0.691 | 0.821 | 0.004 | <1e-3 | 0.041 |
| LongMemEval | corrected | **0.479** | **0.676** | **0.799** | 1.6e-4 | 4.2e-7 | **0.078 (n.s.)** |

(p values: exact McNemar on discordant pairs. On corrected labels, paired
bootstrap CIs exclude 0 for every contrast except LongMemEval OM→OC, whose CI
reaches 0. Judged rows: LoCoMo 173/173/176; LongMemEval 163/139/134.)

Three observations:

- **The correction moves individual conclusions in both directions.** On
  LoCoMo, counting abstentions as wrong makes the final OM→OC rung
  *significant* (0.541 → 0.0146); on LongMemEval it makes the same rung
  *non-significant* (0.041 → 0.078). Oracle modes absorb the most new E0 rows
  (LoCoMo OM +25, OC +16), because they abstain least often for the wrong
  reason — the auto ladder flattered them.
- **The size of the memory-induced loss is benchmark-dependent.** On LoCoMo,
  real memory loses two-thirds of the judged accuracy that oracle memory
  recovers, and perfecting the context still adds a significant rung — after
  gold is in memory, the remaining loss is retrieval/context. On LongMemEval,
  the real→OM recovery is smaller and the last rung does not separate. A
  single "memory costs X points" number would be an artifact of benchmark
  choice.
- **The ladder is a control, not a ceiling.** OM/OC absorb E0 (43% of LoCoMo
  questions are gate-insufficient under the automatic gate), so ladder rungs
  are reported alongside the gate caveat of §3.4 and are never read as error
  rates.

## 5 Failure-stage localisation is architecture-conditional

### 5.1 Three systems with known bottlenecks

We run three memory systems through the same questions, judge, gate,
deterministic floors, and 6000-character context budget:

- **semantic** — an LLM extracts atomic facts per turn (provenance-carrying),
  with governance superseding stale facts; retrieval over the fact store.
  *Designed bottleneck:* formation (extraction can drop or distort facts).
- **summary** — one LLM summary per session, no per-fact provenance.
  *Designed bottleneck:* context (compression loses detail).
- **verbatim** — raw conversation turns, cosine retrieval (windowed RAG).
  *Designed bottleneck:* retrieval (raw-turn similarity ranks poorly).

We name the bottlenecks explicitly because they matter to the interpretation:
the systems were *authored* with these bottlenecks, so a stage difference is
evidence about architecture, not about memory agents in general (§5.4).

### 5.2 Same accuracy, different failure stage (LoCoMo n = 100)

Table 2 reports the one-batch run (100 questions × 3 systems, shared
per-question gate, errors 0; auto labels; accuracy = semantic accuracy on
judged rows).

**Table 2 — Cross-system fingerprint, LoCoMo n = 100, auto labels.**

| system | acc (judged) | formation / retrieval / context recall | failure distribution |
|---|---|---|---|
| semantic | 0.407 (91) | 0.473 / 0.424 / 0.303 | none 42, E0 21, **F1 18**, F4 14, F5 1, EVAL 4 |
| summary | 0.423 (97) | 0.990 / 0.990 / 0.258 | none 42, E0 23, **F5 21**, F4 10, F6 1, EVAL 3 |
| verbatim | 0.429 (98) | 0.990 / **0.197** / 0.162 | none 43, E0 19, **F4 35**, F6 1, EVAL 2 |

End accuracy is statistically indistinguishable across all pairs (exact
McNemar p = 0.736 / 0.728 / 0.864; paired bootstrap CIs all include 0). The
failure-stage distributions are significantly different for **all three
pairs**: Stuart–Maxwell p = 7.4e-5 (semantic vs summary), 2.7e-4 (semantic vs
verbatim), 5.0e-5 (summary vs verbatim); Holm-adjusted ≤ 2.8e-4 throughout;
the paired max-abs permutation test agrees (p = 0.0045 / 0.0007 / < 0.0001).
Per-label paired bootstrap CIs isolate the pattern: semantic's F1 share is
+0.18 over both others (CI [0.11, 0.26]), summary's F5 share +0.21 over
verbatim (CI [0.13, 0.29]; −0.20 vs semantic, CI [−0.29, −0.12]), verbatim's
F4 share +0.21 over semantic (CI [0.12, 0.30]) and +0.25 over summary (CI
[0.15, 0.35]).

### 5.3 The distribution result does not depend on E0 or on the automatic gate

Two sensitivity results, both pre-registered as Stage A of the decision plan:

- **E0-excluded.** Dropping the 42 questions whose shared gate is not
  sufficient (58 used), all three pairs remain significant: p = 2.0e-5 /
  7.5e-5 / 2.7e-5, Holm-adjusted ≤ 7.6e-5. The headline does not depend on
  the (upward-biased, §3.4) E0 class.
- **Human instrument.** The human stage-annotation instrument is reliable
  (κ = 0.897, §3.5); the automatic label's per-row unreliability (κ
  0.59–0.71) is why claims are made on distributions of 90%-confirmed failure
  labels, and the E0-excluded variant removes the class where human and
  automatic labels disagree most.

### 5.4 Ablations and the pre-registered gate: partial, not passed

Stage B of the frozen decision plan tests whether the fingerprint tracks
architecture: turn off a system's own bottleneck and check whether its
dominant failure stage moves. The pre-registered pass rule requires, for
**at least two of three** systems, (i) the dominant-stage share moves
**≥ 20 percentage points** and (ii) the within-system Stuart–Maxwell
p < 0.05 survives Holm. Two conditions were run (A2, the summary-bottleneck
condition, was deferred before any run because a smoke test showed context
assembly, not summary lossiness, binds). Each ablation is a self-contained
paired n = 100 batch with its own shared gate; baseline numbers therefore
differ slightly across batches and are never compared cross-batch.

**A1 — remove the formation bottleneck** (semantic vs `semantic_rawwrite`
write-through verbatim storage). The mechanism responds exactly as
pre-registered: formation recall 0.473 → 0.990, F1 13 → 0 rows, and retrieval
failures double (F4 12 → 24) as the loss relocates downstream. Per-label
paired bootstrap: F1 +0.13 (CI [0.07, 0.20]), F4 −0.12 (CI [−0.22, −0.03]).
The within-system Stuart–Maxwell is significant (χ² = 19.75, df = 6,
**p = 0.0031**, Holm 0.0031; permutation p = 0.0394) — the first ablation
condition where the stage-distribution test itself clears α. Accuracy is
unchanged (0.500 vs 0.430, McNemar p = 0.392, CI [−0.054, +0.185]): the same
system, the same accuracy, a different failure location. **But the largest
share move is 13 points — below the 20-point bar.**

**A3 — remove the retrieval bottleneck** (verbatim vs hybrid ranking).
Retrieval recall 0.197 → 0.402; F4 share 0.37 → 0.23 (14 points); accuracy
improves 0.351 → 0.527 (McNemar p = 0.014). The within-system Stuart–Maxwell
is p = 0.066 (permutation p = 0.0087). **14 points, below the bar; the
distribution test does not clear Holm.**

**Verdict: partial.** 0 of 2 evaluated conditions pass both criteria, and the
decision gate returns *partial* (`results/decision_gate_b.json`). Two
protocol facts are recorded with the verdict and must travel with it:
(i) with A2 deferred, only two of three systems were evaluable, so the
"≥2 of 3" rule **could not** return a pass under the executed design; and
(ii) the 20-point bar couples to base rate — F1 was 13% of rows in the A1
batch, so *eliminating* formation failure could move that share by at most 13
points. The direction criterion was met in both conditions; the magnitude
criterion was not. Per the frozen decision plan, we therefore **narrow the
claim**: the localisation phenomenon is reported as architecture-conditional,
and the universal-fingerprint framing is retracted (N1). We do not restate
the bar after the fact.

### 5.5 Cross-benchmark check: qualitative only

On the only locally available full-haystack LongMemEval sample (n = 10, ~50
sessions per record), the failure labels again differ across systems
(verbatim: 4 retrieval losses; summary: retrieval/context losses; semantic:
no retrieval losses). At n = 10 this is a sanity check, not evidence; §6
lists the missing second-benchmark replication as a limitation.

### 5.6 Stage localisation is not shown to be actionable (N2)

The pre-registered intervention repaired the measured retrieval stage on the
35 F4 questions of the n = 100 run (hybrid candidate widening). The mechanism
worked (retrieval recall 0.043 → 0.321), but the paired outcome did not
clear the decision rule (≥ 6 net flips **and** bootstrap CI lower bound
> 0): net **+7** flips, McNemar p = 0.143, bootstrap diff +0.206, 95% CI
**[−0.029, +0.441]**. A no-op placebo that simply re-asks the question
flipped 9/35 (≈ 26%) of the same subset — the +7 net sits inside that retest
noise. A stage-agnostic composite arm reaches 0.563 overall accuracy (vs
0.429 baseline) but is *worse* on the 65 non-F4 questions (42 → 38 correct),
so the repair is not stage-exclusive. Contribution: a measured stage is not,
at this power, an actionable repair target; Stage C of the decision plan is
not started.

## 6 Limitations

- **Single-benchmark headline.** C4 rests on LoCoMo n = 100; the second
  real-haystack benchmark is an n = 10 qualitative pilot (§5.5). External
  validity is open.
- **Embedding backend.** Every reported run uses the deterministic in-process
  `hash:384` embedding fallback; comparisons are valid only within that
  backend. The retrieval bottleneck is not an embedding artifact: on the 35
  F4 questions, a real 1024-d embedding (bge-m3, served locally) raises dense
  recall only 0.043 → 0.100 and hybrid recall 0.321 → 0.343, while overall
  dense recall is not higher (0.106 under bge-m3 vs 0.205 stored hash).
- **Single judge.** One model (DeepSeek-v4.1-flash, temperature 0) produced
  every answer, judgement, and gate decision; no second-model protocol was
  approved. Within-judge self-consistency is perfect (κ = 1.0); the
  cross-family robustness of judge verdicts is unmeasured here, and earlier
  exploratory cross-model reads (quarantined) are not cited.
- **Instrument caveats travel with the numbers.** Fingerprint labels come
  from the automatic gate (E0 biased upward; §3.4); failure labels are 90%
  human-confirmed; the abstention correction is a validated rule, not per-row
  human labels on the full runs; the human consensus gate covers 200 of the
  400 n = 200 questions.
- **Stage B evaluated two of three conditions** (A2 deferred), and the gate's
  pass rule was arithmetically unreachable under the executed design (§5.4).
- **Evolution (F3)** is measured only on a controlled probe, not on the
  benchmark runs; nothing here quantifies evolution-stage loss in the wild.

## 7 Reproducibility

- **Frozen configuration.** Commit `b8b1f6e`, branch
  `fix/formation-diagnostics-evidence-based`; freeze document
  `docs/PROTOCOL_FREEZE.md`; every post-freeze change is logged in
  `docs/PRE_REGISTRATION_CHANGELOG.md` before the affected run.
- **Models.** DeepSeek-v4.1-flash for answer, judge (temperature 0), and gate
  (temperature 0); embedding backend recorded per run in `run_metadata`.
- **Statistics.** Exact McNemar on discordant pairs; paired bootstrap
  (5,000–10,000 repeats, seed 42); Stuart–Maxwell with Holm correction across
  the three-pair family; max-abs paired permutation (10,000 repeats, seed
  42). Wilson CIs for accuracy.
- **Code and tests.** The protocol, tracer, evaluator, systems, runners, and
  all analysis scripts are in the repository; 227 unit tests pass. Every
  analysis number in this paper regenerates from stored rows by
  label-only re-computation (no model calls) via the scripts named in
  Appendix A.
- **Data.** LoCoMo (refined public split) and LongMemEval are public
  benchmarks; the annotation packages (blinded worksheets, keys, adjudicated
  labels) and all `results/analysis_*.json` artifacts are released with the
  repository. Raw per-row model outputs are reconstructable from the recorded
  run metadata.
- **Compute.** All runs are CPU-only apart from the answer/judge/gate API;
  the largest batch (n = 200 × 3 conditions) runs on a single workstation.

## Ethical considerations

The study uses two public benchmarks and internally produced annotations; no
new human-subject data was collected beyond task annotation carried out
within the project. Annotator disagreement data is reported in aggregate.
Because the paper's subject is the *unreliability of automated
instrumentation*, we flag the residual risk that our corrected labels still
carry the errors quantified in §3, and we release the annotation packages so
the corrections can themselves be re-audited.

## References

*Placeholder — to be completed before submission (network access from the
work host is blocked, so the bibliography has not been verified). Anchors:*

- LoCoMo benchmark (Maharana et al., 2024); LongMemEval (Wu et al., 2024).
- Retrieval-augmented generation (Lewis et al., 2020); memory-agent systems
  in the Mem0 / A-MEM line (cited as related architectures, not evaluated
  here).
- McNemar (1947); Stuart (1955) & Maxwell (1970) for the paired
  marginal-homogeneity test; Cohen (1960) for κ; Holm (1979) for multiple
  comparisons; Wilson (1927) for score intervals.
- LLM-as-judge reliability literature (to be surveyed in the related-work
  section of the LaTeX draft).

---

## Appendix A — Claim → artifact map

Every quantitative claim in this paper regenerates from the stored artifacts
below (all under `results/`, label-only recomputation unless noted). Raw
`comparison*.jsonl` rows are local by policy; the analysis artifacts and the
generating scripts are tracked.

| claim | artifact(s) | script |
|---|---|---|
| Protocol semantics, label versions, decision order | `docs/PROTOCOL.md`, `docs/PROTOCOL_FREEZE.md` | `evaluation/attribution.py` |
| Answer κ 0.92; gate κ 0.0; judge P/R/F1; 54/60 failure labels confirmed; 20/66 abstention FPs | `results/analysis_annotations_adjudicated_n200.json` | `experiments/score_annotations.py` |
| Stored gate near-independent (65 false-insufficient / 17 missed) | `results/analysis_gate_confusion_n200.json` | `experiments/analyze_gate_confusion.py` |
| Round-2 gate failure (κ 0.181; template pathology) | `results/analysis_annotations_round2_diagnostic.json` | `experiments/diagnose_gate_annotations.py` |
| Round-3 fact gate (κ 0.835 / 0.889; P/R/F1 0.837/1.000/0.911) | `results/analysis_annotations_round3.json` | `experiments/score_fact_annotations.py` |
| Abstention rule: naive 52% vs guarded 13/13 & 12/12 | `results/analysis_abstention_rule_validation.json` | `experiments/validate_abstention_rule.py` |
| Corrected ladder (Table 1), both label versions | `results/analysis_ladder_{locomo,longmemeval}_n200_{auto,corrected}.json` | `experiments/analyze_ladder.py` |
| Human-gated E0 re-attribution | `results/analysis_regate_{locomo,longmemeval}_n200.json` | `experiments/regate_with_human_gate.py` |
| Human stage annotation κ 0.897; human-vs-auto κ 0.705 / 0.590 | `results/analysis_round5_pilot_v2.json` | `experiments/score_stage_annotations.py` |
| n = 100 fingerprint (Table 2), paired tests, stage-distribution tests | `results/analysis_ladder_locomo_n100_fixedgate.json` | `experiments/analyze_ladder.py` |
| E0-excluded stage tests | `results/analysis_stage_excluding_e0_locomo_n100.json` | `experiments/analyze_stage_excluding_e0.py` |
| A1 ablation (formation recall 0.473 → 0.990; SM p = 0.0031) | `results/analysis_ablation_a1_n100.json` | `experiments/analyze_ladder.py` on `results/systems_ablation_n100_a1/` |
| A3 ablation (recall 0.197 → 0.402; SM p = 0.066) | `results/analysis_ablation_a3_n100.json` | `experiments/analyze_ladder.py` on `results/systems_ablation_n100_a3/` |
| Gate-B verdict and pre-registered criteria | `results/decision_gate_b.json` | `experiments/emit_decision_gate.py` |
| Route decision, claim re-scope, retractions | `results/route_decision_2026-10-27.json` | (decision record) |
| Intervention null (+7 net, p = 0.143, CI [−0.029, +0.441]; placebo 9/35) | `results/retrieval_intervention_locomo_n100/summary.json` | `experiments/retrieval_intervention.py` |
| bge-m3 embedding check | `results/embedding_backend_check_locomo_n100.json{,l}` | `experiments/check_embedding_retrieval.py` |
| LongMemEval full-haystack pilot (n = 10) | `results/analysis_ladder_longmemeval_sample10_fixedgate.json` | `experiments/analyze_ladder.py` |
| Adversarial review motivating the decision plan | `docs/reviews/2026-10-26-direction-kill-argument.md` | — |
| Governing decision plan, gates A–D | `docs/CCF_B_DECISION_PLAN_2026-10-26.md` | — |

## Appendix B — Gate-B decision artifact (verbatim criteria)

The pre-registered rule evaluated by `results/decision_gate_b.json`:

> **Pass:** for at least two of the three systems, turning off its bottleneck
> (1) changes that system's dominant-stage share by ≥ 20 percentage points,
> and (2) the within-system Stuart–Maxwell p < 0.05 survives Holm across the
> three tests. **Fail:** all three knobs leave the dominant-stage share
> within ±10 points and no within-system test is significant. **Between:**
> reported as partial; the claim is narrowed to the systems/conditions where
> the stage moved.

Evaluated: A1 (13-point move, Holm p = 0.0031 → criterion 2 met, criterion 1
not) and A3 (14-point move, Holm p = 0.066 → neither criterion). A2 deferred
before any run. Verdict: **partial**; claim narrowed to
architecture-conditional localisation; universal fingerprint retracted;
route switched to the analysis/resource paper (this manuscript). Recorded in
`results/route_decision_2026-10-27.json` and the pre-registration changelog
entry of 2026-10-27.
