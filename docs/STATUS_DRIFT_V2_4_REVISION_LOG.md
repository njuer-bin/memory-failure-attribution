# Status Drift v2.4 Revision Log

**Revision:** v2.4  
**Branch:** research/status-drift-v2.4-revision  
**Date:** 2026-11-16  
**Scope:** protocol, runner safeguards, metric semantics, annotation materials.

## Why this revision was made

The previous pilot conflated lexical topic mention with proposition retention, relied on an LLM judge's own proposition-retention decision for CPSD, did not fully protect resume operations against cross-design output reuse, and did not expose enough information about failed judge predictions or actual memory lengths.

## Changes made

1. **Resume integrity**
   - Added a canonical run-configuration fingerprint, including protocol version, design, models, seed, dimensions, limits, writer style, rewrite-matched setting, timeout, and retries.
   - Resume now refuses to continue when the existing run fingerprint differs or is absent.
   - Each record carries the fingerprint.

2. **Metric semantics**
   - Renamed the deterministic lexical check to topic mention; it is no longer presented as proposition retention.
   - Renamed lexical conditional-error diagnostics so they cannot be mistaken for semantic CPSD.
   - Renamed judge-derived CPSD to cpsd_judge_provisional and explicitly documents that it is not confirmatory.
   - Corrected the recursive-minus-direct conditional error delta to compute recursive error minus direct error.
   - Preserved PARSE_ERROR as a distinct status and report invalid/parse-error and missing-prediction counts.

3. **Measurement diagnostics**
   - Record Unicode character and UTF-8 byte lengths for direct, recursive, and rewrite-matched memories.
   - These lengths are not token counts and do not establish token-budget equivalence.

4. **Human annotation**
   - Added a guide and CSV template separating proposition identity, polarity, epistemic status, intention, action execution, condition status, dialogue evidence, and unsupported status change.
   - The primary Unsupported Status Drift Rate is defined from human-adjudicated proposition identity and status labels, not from the LLM judge.

5. **Documentation**
   - Updated the research plan to v2.1 and aligned its title with the epistemic, intentional, and conditional scope.
   - Replaced the obsolete v1.0 pilot protocol and updated run instructions.

## Validation status

- GitHub file-level checks confirmed the revised files and key code anchors are present.
- No local Python syntax/test suite was executed in this revision session.
- No local Ollama model run was executed.
- No v2.4 summary.json or records.jsonl is claimed to exist.
- The previous v1 six-trajectory smoke-test results remain the only verified model outputs until the user runs v2.4 locally.

## Remaining work before interpreting results

1. Run the v3 smoke test in a fresh v24_smoke output directory.
2. Inspect every raw memory and judge response.
3. Run the full 30-trajectory v3 pilot with rewrite-matched enabled only after smoke-test review.
4. Complete the two-annotator reliability set described in the protocol.
5. Add token-level usage logging and a genuinely matched final-budget experiment before making causal claims about recursive compression.
