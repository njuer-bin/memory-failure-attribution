# Literature Survey — Status Drift in Long-Term Conversational Memory

**Last updated:** 2026-11-16
**Status:** metadata verified via arXiv search; full texts not yet read.
Do not cite a paper's method or claim until the full text and appendix are read.

## Plan-named works

| Plan name | Resolved paper | Status |
|---|---|---|
| BELIEFMEM | *Belief Memory: Agent Memory Under Partial Observability* (arXiv 2605.05583, Liao et al., 2026-05) | Resolved; closest adjacent work on storing beliefs rather than deterministic conclusions. Must read. |
| Answer Bubbles | *Answer Bubbles: Information Exposure in AI-Mediated Search* (arXiv 2603.16138, Huang et al., 2026-03) | Title resolved, but the abstract is about generative search summaries, not memory status. Confirm whether the plan meant this paper. If not, unresolved. |
| ProgMem | No exact arXiv match on 2026-11-16. Nearby hits: ProgRouter (2608.25992), MemCoRe (2602.07885). | Unresolved. |
| HELM | Ambiguous; no exact match found for a memory-status paper. | Unresolved. |

## Relevant arXiv hits (metadata as returned by the search API)

| ID | Title | Why it matters |
|---|---|---|
| 2605.05583 | Belief Memory: Agent Memory Under Partial Observability | Stores evolving beliefs/uncertainty instead of single deterministic conclusions. Closest to the epistemic-status claim. |
| 2602.07885 | MemCoRe: Recovering Evidence from Progressively Compressed Factual Knowledge for Agent Memory | Progressively compressed factual knowledge; directly adjacent to the recursion claim. |
| 2512.20111 | ABBEL: Learning Natural-Language Belief States for Memory-Efficient Interaction | Recursively updated natural-language belief states. |
| 2609.28575 | TWIST: A Proposed Benchmark for Intervention Quality in Conversational Memory | Evolving user beliefs and memory state; possible benchmark overlap. |
| 2609.12354 | CueMem: Cue-Guided Context Reconstruction for Long-Term Conversational Memory | Compressed memory may lose fine-grained evidence. |
| 2509.21212 | SGMem: Sentence Graph Memory for Long-Term Conversational Agents | Compression/summarization trade-offs. |
| 2402.11975 | Compress to Impress: Compressive Memory in Real-World Long-Term Conversations | Compressive-memory baseline. |
| 2608.30508 | UTILMEM: Benchmarking Evidence Utilization in Long-Term Conversational Memory | Evidence-utilization measurement. |
| 2602.06052 | A Survey of Agent Memory in the Second Half | Survey framing of memory lifecycle. |
| 2610.07309 | The Right Memory in the Wrong Context: Verifying Retrieval Admissibility | Lifecycle/state admissibility in memory. |
| 2410.21195 | Belief in the Machine: Epistemological Blind Spots of Language Models | Fact vs belief vs knowledge distinctions. |

## Additional 2026 belief-memory work (metadata only)

| ID | Title | Why it matters |
|---|---|---|
| 2610.01415 | Beyond Memory: Harnessing Long-Horizon Agents with Explicit Belief States | Explicit belief-state framework; may cover status tracking. |
| 2607.23929 | MemTX: Transactional Belief Commit for Stateful Agent Memory | Belief commit/state transitions in agent memory. |
| 2610.25119 | Memory as Belief: Bayesian Evolution of Memory for Self-Evolving LLM Agents | Treats memory as evolving belief; adjacent to status evolution. |
| 2605.11436 | Agent-BRACE: Decoupling Beliefs from Actions in Long-Horizon Tasks via Verbalized State Uncertainty | Directly relevant to the status-vs-action distinction. |
| 2609.21997 | Bayesian Belief Layer for Controllable Opinion Dynamics in LLM Agents | Belief-state dynamics. |
| 2104.08401 | Enriching a Model's Notion of Belief using a Persistent Memory | Older belief-memory baseline. |

This is a crowded space. The defensible gap is **controlled measurement of
status-cue loss under repeated/chained compression**, with the
direct-vs-rewrite-matched contrast and deterministic cue metrics. Do not claim
a new memory architecture or the first belief-state memory.

## Verified summaries (AlphaXiv, 2026-11-16)

### BELIEFMEM — Belief Memory: Agent Memory Under Partial Observability (2605.05583)

- Stores attribute-level probabilistic beliefs: candidate hypotheses plus
  evidence-based probabilities, updated with a noisy-OR merge and archived
  prior probabilities. Belief-aware retrieval returns candidates with
  probabilities.
- Evaluated on LoCoMo (F1/BLEU) and ALFWorld (success rate); ablations show
  probabilistic memory beats deterministic memory.
- **Not** a measurement of status preservation under recursive/repeated
  compression; no direct-vs-chained control, no status-cue metric.

### MemCoRe — Recovering Evidence from Progressively Compressed Factual Knowledge (2602.07885)

- Compression hierarchy: detailed records → keywords → topic groups; retrieval
  searches across levels. Framed as an information-bottleneck trade-off.
- Measures evidence recall/retrieval under compression, **not** epistemic,
  intentional, or conditional status preservation.
- Adjacent on progressive compression, but a different target.

## Novelty position

The defensible contribution is a **controlled diagnostic**:

1. status-cue loss measured separately from proposition retention;
2. direct vs chained vs rewrite-matched controls, isolating chained rewriting
   from intermediate budget shrinkage;
3. a deterministic cue metric plus three-judge validation;
4. a status-aware writer prompt as a mitigation baseline.

BELIEFMEM already covers probabilistic belief memory; MemCoRe covers
compression-hierarchy retrieval. Neither appears to measure status drift under
chained rewriting. Still unread in full: PoS (2610.01415), MemTX (2607.23929),
Memory as Belief (2610.25119), Agent-BRACE (2605.11436).

## Immediate literature tasks

1. Read BELIEFMEM (2605.05583) fully. If it already measures status change under
   recursive memory updates, narrow the novelty claim to controlled
   status-only corruption and downstream behavior.
2. Read MemCoRe (2602.07885). If it measures status preservation under
   progressive compression, the recursion claim must be repositioned.
3. Read ABBEL (2512.20111) and TWIST (2609.28575) for metric overlap.
4. Resolve ProgMem and HELM; if they cannot be located, remove them from the
   plan rather than citing unverifiable names.
5. Check whether any paper separates proposition retention from status change
   with an explicit CPSD-like metric.
