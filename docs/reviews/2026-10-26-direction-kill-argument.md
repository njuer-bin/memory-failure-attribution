# Kill Argument — direction reassessment after the intervention null

**Date**: 2026-10-26
**Method**: adversarial attack → independent adjudication, two fresh reviewers.
The skill's default Codex backend was not used (project policy: DeepSeek-only,
no model switch without approval); the same fresh-thread protocol was run with
two independent Claude reviewers reading the artifacts.
**Subject**: whether the current framing (cross-system failure fingerprint +
actionable stage-targeted attribution) is CCF-B viable, or whether to pivot to
the pre-registered analysis/resource paper.
**Verdict (current framing): FAIL** — 2 critical points still unresolved, 3
partially answered, 0 answered. The analysis/resource pivot remains viable.

## Attack memo (verbatim)

> This direction measures its own construction, and its one causal test fails.
>
> The headline — null end accuracy (0.407/0.423/0.429; McNemar
> p=0.736/0.728/0.864) paired with "significantly different" failure
> fingerprints (Stuart–Maxwell, Holm ≤2.7e-4;
> `results/analysis_ladder_locomo_n100_fixedgate.json`) — is in substance a
> restatement of how the three baselines were built. A fact-extraction engine
> loses at formation (F1 18, formation recall 0.473); a session summarizer loses
> at context (F5 21, context recall 0.258); a raw-turn retriever loses at
> retrieval (F4 35, recall 0.197) — because each was authored with exactly that
> bottleneck. On a single benchmark, over 100 questions, this is a taxonomy of
> the authors' own pipeline choices, not a phenomenon about memory systems. The
> lone LongMemEval replication is n=10 with degenerate oracle retrieval; the
> round-3 human gate covers 48/100 of the headline questions.
>
> The test that would turn a taxonomy into a finding is the intervention, and
> the project's own pre-registration records it as failed. Retrieval recall on
> the 35 F4 questions rises 0.043→0.321, yet accuracy yields +7 net flips on 34
> paired questions, McNemar p=0.143, bootstrap 95% CI [−0.029,+0.441]
> (`results/retrieval_intervention_locomo_n100/summary.json`). A no-op placebo
> re-ask alone flips 9/35 wrong→correct. When repairing the measured stage is
> statistically indistinguishable from re-asking the question, the attribution
> carries no demonstrated actionable value. That is diagnostics without utility
> — and it is the project's own stated kill line.

## Adjudication

### P1 — Construction-confounded fingerprint — **still_unresolved (critical)**
The stage↔system mapping is exactly the architectures' storage designs
(`experiments/memory_systems.py`: raw-turn cosine retrieval, one lossy session
summary, fact extraction). No artifact runs a black-box/third-party system or an
architecture ablation that decorrelates stage from design. The F3 k=5 probe
shows the stage moving with workload under a synthetic probe, not on the
headline. Fix: run a Mem0/A-MEM-class system and/or an extraction-vs-raw
ablation; reframe as *architecture-conditional failure localization*.

### P2 — Single benchmark / weak replication — **partially_answered (major)**
Correction to the memo: the n=10 pilot is the **full-haystack** variant
(`longmemeval_s_sample10`), not the degenerate oracle run; verbatim retrieval
recall is 0.60. But the pilot does **not** reproduce the null-accuracy premise
(summary 0.125 vs semantic/verbatim ≈0.56), so only stage direction replicates.
The single-benchmark limitation stands. Fix: scale to n=50–100 or scope the
paper to LoCoMo.

### P3 — Human gate covers 48/100 — **partially_answered (major)**
Confirmed 48 covered / 52 uncovered. Re-gating preserves the pattern on covered
rows (F1 18→20, F5 21→21, F4 35→35; E0 21→18/23→18/19→21). But the
Stuart–Maxwell test was not rerun on human-gated labels, E0 is one of its
categories, and the "90% sound" defense validates answer direction, not the
stage labels themselves. Fix: rerun stage tests with E0 excluded or on the 48
human-gated rows; add a human audit of stage attribution.

### P4 — Intervention failed its pre-registered rule — **still_unresolved (critical)**
Confirmed: placebo 9 vs repair 16 on 34 paired questions; net +7; McNemar
p=0.143; CI [−0.029,+0.441]; `decision.success: false`. The mechanism moved
(recall 0.043→0.321) but accuracy did not separate, and the agnostic arm is
worse on non-F4 (42→38). The design's own falsifier (placebo moves ≥3/35) was
triggered at 9/35. Fix: do not scale the same design blindly — cut retest
variance, human-verify F4 labels, then test the ~70-question n=200 subset under
a fresh pre-registration; or demote contribution 4 to null.

### P5 — Placebo floor kills actionable value — **partially_answered (major)**
The "no demonstrated actionable value" inference is fair; "statistically
indistinguishable" overstates a failed-to-reject at n=34 (underpowered is
honest). "Kill line" is imprecise: the CCF-B kill line does not cleanly trigger,
while the publication roadmap explicitly pre-registers the analysis-paper
fallback. The ~26% retest instability also weakens the F4 label base rate, not
just the intervention. Fix: execute the pre-registered pivot; treat
actionability as dead until a powered repair beats the floor.

## Net assessment

On current artifacts the direction would not survive as the paper it is
currently framed to be — a cross-system "failure fingerprint" phenomenon plus
actionable attribution. The two load-bearing attacks are correct and unrebuted:
the LoCoMo fingerprint is largely entailed by the three architectures' storage
designs, and the one stage-targeted intervention missed its pre-registered rule
while a no-op re-ask moved 9/35. An independent confound the memo does not name:
every run uses the deterministic `hash:384` embedding fallback, which
manufactures the verbatim retrieval bottleneck (recall 0.197); the retrieval
stage is partly an embedding artifact rather than a general property of
raw-turn RAG. The pilot also fails the null-accuracy premise (summary 0.125 vs
~0.56), which weakens external validity.

What survives is a credible instrument/resource paper: the attribution protocol,
the human-audit methodology (answer kappa 0.92; abstention rule 13/13 and 12/12;
judge-abstention false positives 20/66), and the corrected oracle ladder
(LoCoMo 0.306→0.682→0.761, all rungs significant; LongMemEval 0.479→0.676→0.799,
two of three rungs significant). That is the project's own pre-registered
fallback (COLING/NLPCC) and it is publishable.

Writing-level fixes (retitle "architecture-conditional", scope LongMemEval as a
pilot, demote contribution 4, stop quoting E0 as a level) are necessary to stop
overclaiming but cannot alone clear the CCF-B bar for the phenomenon paper.
Research-level gaps: (a) black-box/third-party system or architecture ablation
to break the construction confound; (b) a powered intervention that beats the
retest floor; (c) fully human-gated headline labels plus a human audit of stage
attribution; (d) a second real-haystack benchmark at n≥50; (e) a real embedding
backend and a second judge model. Without at least (a) and (b), this is an
analysis paper.

## Top action items

1. **Break the construction confound (critical).** Run a black-box/third-party
   memory system (Mem0/A-MEM class) and/or an architecture ablation; reframe as
   architecture-conditional failure localization.
2. **Resolve contribution 4 honestly (critical).** Repeat arms and human-verify
   F4 labels, then re-test the n=200 (~70 F4) subset under a fresh
   pre-registration — or demote to null and execute the analysis-paper pivot.
3. **Solidify measurement and the second benchmark (major).** Rerun stage tests
   E0-excluded / on the 48 human-gated rows, add a human audit of stage labels,
   scale full-haystack LongMemEval to n=50–100, and move off the `hash:384`
   embedding fallback (bge-m3 is available locally).

## Immediate cheapest decisive check

The `hash:384` fallback is named by the adjudicator as an independent confound
for the verbatim retrieval bottleneck. bge-m3 is already available locally
(no API). Recomputing retrieval ranking/recall with bge-m3 on the n=100
questions is free and decides whether the retrieval-stage fingerprint is a real
property or an embedding artifact. Do this before spending on a black-box
system.
