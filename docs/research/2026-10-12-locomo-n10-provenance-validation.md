# LoCoMo n=10 Turn-Level Provenance Validation

Date: 2026-10-12  
Dataset: `locomo_refined_public`  
Gate: `LOCOMO_SINGLE_SAMPLE_PROVENANCE_E2E`  
Branch: `fix/independent-evidence-gate`

## 1. Purpose

After discovering that the original provenance E2E gate could use semantic fallback in `stage_match()` and therefore report a false D1 → D10 provenance mismatch, the provenance gate was changed to strict turn-level matching.

The purpose of this validation is to check that Gold Evidence can be mapped to the correct benchmark turn and raw memory record across multiple LoCoMo samples before running larger attribution experiments.

## 2. Validation protocol

For each question, the gate checks:

1. Gold Evidence provenance (`source_id`, `turn_id`, `raw_id`)
2. Gold Evidence → raw ingested memory mapping
3. Lifecycle artifacts using exact `turn_id` provenance only
4. No semantic-similarity fallback for provenance matching

A lifecycle `missing` result is **not** treated as a provenance failure. It is a possible lifecycle loss that may later contribute to F1–F5 attribution.

The key distinction is:

- **Provenance PASS**: the benchmark evidence points to the correct source turn/raw record.
- **Lifecycle found/missing**: whether that evidence survives a particular memory lifecycle stage.

## 3. Results

All 10 samples passed the provenance gate:

| Question | Gold evidence | Provenance | Sessions covered |
|---|---:|---|---|
| `conv-26#q0000` | 1 | PASS | D1 |
| `conv-26#q0001` | 1 | PASS | D1 |
| `conv-26#q0002` | 2 | PASS | D1 |
| `conv-26#q0003` | 1 | PASS | D2 |
| `conv-26#q0004` | 1 | PASS | D1 |
| `conv-26#q0005` | 1 | PASS | D2 |
| `conv-26#q0006` | 1 | PASS | D2 |
| `conv-26#q0007` | 2 | PASS | D2 + D3 |
| `conv-26#q0008` | 1 | PASS | D3 |
| `conv-26#q0009` | 1 | PASS | D3 |

Summary:

- Provenance PASS: **10/10 (100%)**
- Provenance errors: **0**
- Sessions represented: **D1, D2, D3**
- Single-evidence questions: **8**
- Multi-evidence questions: **2** (`q0002`, `q0007`)
- Both user and assistant source turns are represented.
- Raw and derived/event lifecycle artifacts are represented.

## 4. Representative lifecycle observations

### q0005: complete retrieval path

The Gold Evidence for `D2:turn_0` was found in storage, retrieval, rerank, and context with exact provenance. This demonstrates a complete evidence path without cross-turn substitution.

### q0006: retrieval/rerank survive, context misses

The Gold Evidence for `D2:turn_6` was found in storage, retrieval, and rerank, but was missing from context. This is a useful example of a potential context-stage loss. It is **not** itself a final F5 attribution; the full attribution protocol must still be applied.

### q0007: multi-evidence lifecycle divergence

Two Gold Evidence items were mapped correctly:

- `D3:turn_12`
- `D2:turn_13`

Storage retained both, while formation/evolution retained only `D3:turn_12`, and retrieval/rerank/context retained neither. This demonstrates why evidence-level lifecycle tracking is necessary for multi-hop/multi-evidence questions.

### q0008: formation/evolution success but retrieval loss

The evidence at `D3:turn_0` was found as both a formation event and raw storage record, but was missing from retrieval/rerank/context. This provides a clean example of a downstream retrieval loss with correct provenance.

## 5. Interpretation

The n=10 validation provides initial evidence that the strict turn-level provenance design is working across multiple sessions and evidence configurations.

It does **not** establish that provenance is correct for the full LoCoMo benchmark. The validation is still a small sample and is concentrated in one conversation (`conv-26`). Therefore it should be described as a **single-conversation n=10 validation**, not a dataset-wide guarantee.

The result supports proceeding to a larger provenance validation before treating the LoCoMo attribution results as final.

## 6. Next steps

1. Fix the attribution audit logic so `F4_RETRIEVAL` correctly accepts either retrieval or rerank loss.
2. Run the related audit/tests.
3. Perform additional provenance validation across other conversations, not only `conv-26`.
4. Re-run the n=50 LoCoMo experiment after provenance/evaluator changes are frozen.
5. Only then scale to larger samples and report confidence intervals.

## 7. Research significance

This validation separates two previously conflated questions:

> **Did the benchmark evidence point to the correct memory item?**

from:

> **Did that memory item survive each lifecycle stage?**

Strict turn-level provenance is therefore treated as an experimental validity prerequisite, rather than as another memory failure category.