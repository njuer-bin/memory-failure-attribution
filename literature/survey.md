# Literature Survey — Status Drift in Long-Term Conversational Memory

**Last updated:** 2026-11-16
**Status:** search-result index, not a verified bibliography. Titles, authors, and
venues must be checked against the actual papers before citation.

## Named by the research plan (unverified)

`docs/STATUS_DRIFT_RESEARCH_PLAN_V2.md` lists HELM, ProgMem, BELIEFMEM, and
Answer Bubbles as closely related. On 2026-11-16 the local searxng backend
returned zero results for these names, and arXiv keyword search did not return
exact-title matches. Their full texts and appendices remain **unverified**.
Do not make a novelty claim until they are located and read.

## Relevant arXiv hits (metadata as returned by the search API)

| ID | Title | Why it matters |
|---|---|---|
| 2512.20111 | ABBEL: Learning Natural-Language Belief States for Memory-Efficient Interaction | Recursively updated natural-language belief states; closest to the recursion claim. |
| 2609.28575 | TWIST: A Proposed Benchmark for Intervention Quality in Conversational Memory | Studies evolving user beliefs and memory state; possible benchmark overlap. |
| 2609.12354 | CueMem: Cue-Guided Context Reconstruction for Long-Term Conversational Memory | Compressed memory units may lose fine-grained evidence. |
| 2509.21212 | SGMem: Sentence Graph Memory for Long-Term Conversational Agents | Compression/summarization trade-offs in long-term memory. |
| 2402.11975 | Compress to Impress: Compressive Memory in Real-World Long-Term Conversations | Compressive memory baseline. |
| 2608.30508 | UTILMEM: Benchmarking Evidence Utilization in Long-Term Conversational Memory | Evidence-utilization measurement, adjacent to omission vs distortion. |
| 2606.24775 | Are We Ready For An Agent-Native Memory System? | Survey framing of memory lifecycle and governance. |
| 2410.21195 | Belief in the Machine: Epistemological Blind Spots of Language Models | Fact vs belief vs knowledge distinctions relevant to epistemic labels. |

## Immediate literature tasks

1. Verify whether ABBEL and TWIST already measure status change under recursive
   compression. If so, narrow the novelty claim to controlled status-only
   corruption and downstream behavior.
2. Locate the four plan-named works; record venue, year, and exact contribution.
3. Check whether any paper separates proposition retention from status change
   with an explicit CPSD-like metric.
