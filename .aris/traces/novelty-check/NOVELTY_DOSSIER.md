# Novelty dossier

## Proposed work

A diagnostic protocol for LLM long-term-memory agents that attributes each failed QA
answer to the earliest lifecycle stage where required Gold Evidence disappears:
Formation → Storage → Evolution (unmeasured) → Retrieval → Rerank → Context → Reasoning.
Three nested conditions separate stages: Real Memory (full pipeline), Oracle Memory
(gold evidence written directly into the store, then real retrieval), Oracle Context
(gold evidence placed directly in the answer context). Per-question first-loss
attribution yields F1/F2/F4/F5/F6 plus E0 (benchmark evidence insufficient) and EVAL
(judge uncertain). Evidence matching is provenance-constrained. Answer verdicts combine
a semantics judge with deterministic floors (numeric ranges, temporal equivalence,
ordering refutation); judge reliability is measured (self-consistency kappa 1.0;
cross-model raw-judge kappa ≈ 0.03 between qwen2.5:7b and gemma3:12b).

Findings (n=50 each, preliminary):
- LongMemEval oracle: formation-dominated (recall 0.503), retrieval perfect; F6=16/50 OM
  after refutation.
- LoCoMo: retrieval-limited (RM recall 0.560, OM 0.810; context RM 0.360), 17/50
  insufficient-gate; F4 present, F6=5/50 OM.
- Therefore the first-loss stage is workload-conditional, not universal.
- LLM judges alone cannot sustain F6: deterministic floors required.

Target venue: CCF-B (CIKM / COLING / ECIR / NLPCC).

## Core claims

C1. A unified lifecycle-stage attribution protocol that assigns, per question, the
    earliest stage where gold evidence disappears, using nested oracle conditions to
    isolate stage contributions.
C2. The first-loss stage profile is a property of the (memory system × workload) pair:
    formation-dominated on LongMemEval, retrieval/context-limited on LoCoMo.
C3. Judge-based F6 is unreliable without deterministic floors; reliability is measured
    and reported (cross-model kappa ≈ 0.03).
C4. Evidence-sufficiency gating (E0) is necessary before stage attribution, judged
    non-circularly against the benchmark reference answer.

## Prior work found (arXiv, 2025-2026)

P1. A-TMA: Decoupling State-Aware Memory Failures in Long-Term Agent Memory
    (2607.01935, 2026-07). Ghost-memory state coordination; argues for decoupled
    evaluation of bank maintenance, retrieval, answer-time resolution; proposes an
    overlay, not observational attribution.
P2. Diagnosing Retrieval vs. Utilization Bottlenecks in LLM Agent Memory
    (2603.02473, 2026-03). 3×3 write-strategy × retrieval-method study on LoCoMo;
    diagnostic framework over three coarse factors, no per-question attribution, no
    lifecycle oracle ladder.
P3. Stale, Misattributed, or Late: Where Personal Memory Fails Before Generation
    (2610.10265, 2026-10). Measures pre-generation failures (obsolete value, wrong
    person, no fact by deadline) against a Personal Fact Memory reference layer.
P4. When Failures Propagate: Causal Failure Attribution in Agentic Retrieval-Augmented
    Generation (2608.20627, 2026-08). Interventional benchmark injecting faults at RAG
    hops; evaluates post-hoc diagnosers. Different setting (multi-hop RAG) and
    interventional method.
P5. Relevance Is Not Sufficiency: What Actually Closes the Evidence Gap in Long-Term
    Memory QA (2610.09348, 2026-10). Recasts retrieval as building a sufficient evidence
    set; blinded LLM judgment; Gold Hit / Turn Hit; proposes BFR retrieval.
P6. Fidelity Before Structure (2601.00821). Controlled storage-representation ablation;
    verbatim vs extracted artifacts on LoCoMo/LongMemEval.
P7. Many Steps into One (2610.17544). Reasoning contraction and stale-memory detection.

## Questions for the reviewer

1. Is the proposed work novel relative to P1–P5? Name the closest prior work.
2. What exactly is the delta, stated in one sentence a reviewer could verify?
3. Is claim C2 (workload-conditional first-loss) plausibly novel as a finding, even if
   the individual stages are known?
4. Would a CCF-B reviewer accept this as a paper, and which venue fits best?
5. What must be added (intervention? scale? novelty framing?) for acceptance?

=== NOVELTY VERDICT LIMITS (these bound how you judge, never how widely you search) ===
Search exhaustively; judge calibrated. Two failures waste months equally:
passing an idea a published paper already contains, and killing a viable idea
because the territory has neighbors.
1. Proximity is information, not a verdict. Someone working nearby goes in the
   report; it is not by itself a reason to reject.
2. ABANDON has exactly one qualification: a specific published paper already
   contains this result — name that paper. No named paper, no ABANDON.
3. Crowded-but-deltaed is PROCEED: state the delta in one sentence a reviewer
   could verify. Thin or contested delta is PROCEED WITH CAUTION — say what
   would make it carry, not why it should die. CAUTION is not a safe middle:
   if you cannot name the specific thing that makes the delta thin, the
   verdict is PROCEED.
4. Concurrent or competing work is not a veto. That is a race — report it and
   let the user decide whether to run it.
5. A direct attack on a central problem is legitimate novelty when nobody has
   executed it well. "This area is hot" does not mean "this area is taken."
6. This check is an early gate, never the last one — more triage, pilots, or
   external review still stand between any idea and a paper, whatever order
   this run uses. A wrongly passed idea dies cheaply at one of them; a wrongly
   killed idea is never seen again. When torn between two verdicts, choose the
   more permissive one.
Say plainly when an idea clears the check. Do not manufacture overlap.
