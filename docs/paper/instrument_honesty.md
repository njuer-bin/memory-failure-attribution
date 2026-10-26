# Draft — Instrument honesty (paper §"Measurement")

Status: draft 2026-10-26. Not submission-ready: the round-3 per-fact gate has
not been run. This section states only what the stored artifacts support, and
marks the one open instrument explicitly.

## 1. Why measurement is part of the contribution

A failure-attribution paper makes two kinds of claim: (i) the answer was wrong,
and (ii) a particular lifecycle boundary was the first point at which the
evidence needed for the reference answer became unobservable. Both rest on
instruments — a semantic judge for (i), an evidence-sufficiency gate for the E0
boundary. If those instruments are not audited, the attribution map is a map of
instrument error. We therefore had two annotators independently label a
200-question stratified sample (100 LoCoMo + 100 LongMemEval) drawn from the
canonical n=200 runs, and adjudicated every disagreement.

The audit produced three results that change how every number in this paper is
reported.

## 2. Human agreement: answer correctness is measurable, the gate is not (yet)

Answer correctness reached kappa 0.92 between annotators (n=177 co-decided).
The round-1 evidence-sufficiency field was degenerate (kappa 0.0: one annotator
never said "no"), and a round-2 derivability checklist still failed
(kappa 0.181, n=177), because one annotator's "missing fact" notes were a
mechanical template that lifted tokens from the reference answer (75/81 quoted
tokens occurred in the reference, 0/81 in the evidence, including function
words such as "she" and "because").

We therefore do not claim a human-validated gate. Round 3 replaces the gestalt
judgement with per-fact binary annotation: each reference answer is decomposed
into atomic propositions and annotators mark, per fact, whether the gold
evidence states it; the row gate is a transparent aggregation (all required
facts present; an any-of group needs one alternative). A fact marked
`uncertain` because a relative date has no usable anchor counts as insufficient
in the primary gate, since the reference is then not derivable from the listed
evidence; an exclude-uncertain variant is reported as sensitivity. Its
acceptance bar is pre-registered at fact-level kappa >= 0.6 and row-level
kappa >= 0.6. Until it clears, **E0 is reported as a relative pattern, never as
a level**.

What survives independently of the gate is the failure-direction base rate: of
60 stored-incorrect rows with a human verdict, 54 (90.0%) are confirmed wrong.
The paper's claim that these runs fail in a particular direction does not rest
on the gate.

## 3. The semantic judge rewards abstention

Of 66 sampled rows the judge stored as semantically correct, 20 (30.3%) are
human-adjudicated wrong; 13 of the 20 are abstention-style answers ("Not
mentioned", "Cannot be determined") that the judge accepted as correct. Left
uncorrected, this inflates accuracy wherever a model declines to answer, and
inflates the oracle conditions most because they abstain least often for the
wrong reason.

We correct this label-only, with a rule derived from — and validated against —
the human sample. The naive rule "stored-correct abstention is wrong" is only
52% precise on the 25 sampled abstentions, because 12 are LongMemEval `_abs`
questions whose reference answer is itself an abstention ("The information
provided is not enough. ..."). Guarding on the reference answer — flip only
when the reference is a concrete proposition — identifies all 13 human-wrong
abstentions and preserves all 12 human-correct ones on the sampled abstention
subset (13/13, 12/12). On the full stored-correct sample the rule flips 13 of
31 human-wrong rows (recall 0.42); the other 18 are non-abstention judge errors
that this rule does not address, and we do not claim otherwise.

Effect on the Real → Oracle-Memory → Oracle-Context ladder (semantic accuracy
on judged rows, n=200 per benchmark; corrected labels in bold):

| benchmark | real | oracle memory | oracle context |
|---|---|---|---|
| LoCoMo, auto | 0.405 | 0.832 | 0.852 |
| LoCoMo, corrected | **0.306** | **0.682** | **0.761** |
| LongMemEval, auto | 0.521 | 0.691 | 0.821 |
| LongMemEval, corrected | **0.479** | **0.676** | **0.799** |

The correction lowers the oracle rungs most on LoCoMo (OM -0.150, OC -0.091 vs
real -0.099) and adds 25 / 16 E0 rows to OM / OC. Two paired conclusions move:
on LoCoMo the OM→OC contrast becomes significant (p 0.5413 → 0.0146) once
abstentions stop counting as correct; on LongMemEval it becomes non-significant
(p 0.0414 → 0.078). The real→OM and real→OC contrasts remain highly significant
on both benchmarks. We report both label versions side by side in every table;
no accuracy comparison between systems is quoted on auto labels alone.

## 4. The automatic gate is near-independent of humans

Against adjudicated labels, the stored gate reaches kappa 0.07 overall (0.026
LoCoMo, 0.031 LongMemEval). With sufficiency as the positive class it has
precision 0.832 and recall 0.564. Stated in the direction that matters for E0,
the gate **misses 17 truly-insufficient rows** (all in LoCoMo) but **falsely
marks 65 sufficient rows insufficient** (28 LoCoMo, 37 LongMemEval). The error
is dominated by over-flagging, not under-detection, and it is systematic: for
the 15 LongMemEval `_abs` questions the gate called 14 insufficient while
humans called all 15 sufficient, because it reads "evidence does not state a
concrete answer" as "reference not established" rather than "the reference
answer is itself an abstention". (An earlier internal report swapped these two
counts; `results/analysis_gate_confusion_n200.json` is authoritative.)

Consequences we adopt:

1. E0 counts are used only to compare conditions, never as error rates. Because
   the dominant gate error is false insufficiency, E0 is biased upward; the
   relative comparison stays defensible only because one shared gate is applied
   to all conditions of the same question.
2. Any claim about "how much of the loss is memory" is stated on the abstention-
   corrected labels and accompanied by the gate caveat.
3. Stage-distribution claims (F1…F6) are made on the failure labels, which the
   audit shows are 90% sound, not on E0.

## 5. Recommended reporting protocol

We suggest three rules for any agent-memory failure study that uses an LLM
judge:

1. **Floor first.** Ship a deterministic, auditable rule for the label dimensions
   that admit one (temporal equivalence, ordering, exact abstention detection)
   before trusting a judge.
2. **Report the kappa.** Every judge-derived dimension is reported with its
   human agreement; a dimension below the pre-registered bar is marked
   non-citable.
3. **Report both label versions.** Auto and corrected numbers appear together;
   the corrected number is the headline and the delta is the measurement error.

## 6. Limitations

- The audit sample is 200 questions from two benchmarks; failure-direction base
  rates and abstention rates may differ elsewhere.
- Adjudication was a single project-lead pass over two annotators; the
  answer-correctness kappa (0.92) supports it, the gate labels do not.
- The abstention correction is a validated rule on the sample, not a per-row
  human label for all 200 or for the full n=200 runs; its n=200 application is
  an inference whose direction and magnitude — not its exact row set — are what
  we cite.
- Judge reliability across model families is measured elsewhere (cross-model
  raw-judge kappa ≈ 0.03); this section concerns within-judge label validity.

## 7. Number provenance

| claim | source artifact |
|---|---|
| answer kappa 0.92; gate kappa 0.0; adjudication rules | `results/analysis_annotations_adjudicated_n200.json` |
| evaluator vs human: answer P/R/F1/kappa; gate P/R/F1/kappa | `results/analysis_annotations_eval_vs_adjudicated.json` |
| 54/60 stored-incorrect confirmed; 20/66 judge false positives; 13 abstentions | `results/analysis_annotations_adjudicated_n200.json` |
| round-2 gate kappa 0.181, template pathology | `results/analysis_annotations_round2_diagnostic.json` |
| abstention rule 52% naive vs guarded 13/13, 12/12 | `results/analysis_abstention_rule_validation.json` |
| corrected n=200 accuracy, E0, failure distribution | `results/analysis_abstention_corrected_{locomo,longmemeval}_n200.json` |
| paired accuracy and stage-distribution tests, both label versions | `results/analysis_ladder_{bench}_n200_{auto,corrected}.json` |
| `_abs` gate failure (14/15) | `results/analysis_annotations_eval_vs_adjudicated.json`; `round3_key.csv` |
| gate confusion with explicit polarity (misses 17, false-insufficient 65) | `results/analysis_gate_confusion_n200.json` |
| round-3 gate instrument and acceptance bar | `results/annotation_package/README_round3.md` |
