# LoCoMo Evidence Resolution Diagnosis — 2026-10-09

## Trigger

The first LoCoMo single-record trace used:

- Question: `When did Caroline go to the LGBTQ support group?`
- Benchmark answer: `7 May 2023`
- Gold evidence reference: `D1:3`

The normalized record incorrectly represented the evidence as:

```text
text = "D1:3"
granularity = unresolved
```

This caused the lifecycle tracer to report the required evidence as missing from Formation onward. Oracle Memory and Oracle Context also injected the literal string `D1:3`, producing the invalid answer `D1:3`.

## Root cause

Inspection of the public LoCoMo conversation showed that the conversation is stored as a dictionary with a `sessions` list. The first session contains messages whose benchmark IDs are explicit:

```text
D1:1
D1:2
D1:3  -> I went to a LGBTQ support group yesterday and it was so powerful.
```

Therefore `D1:3` is a **benchmark turn reference**, not evidence text.

There was also a second adapter mismatch: the normalized record exposed the raw conversation dictionary, while the experiment runner expects a list of canonical sessions with `session_id` and `messages`.

## Fix

`datasets/adapters.py` now:

1. Normalizes the public LoCoMo `sessions` structure into the runner schema.
2. Derives the internal session ID (`D1`) from the benchmark `dia_id` when no explicit `session_id` exists.
3. Preserves benchmark turn IDs such as `D1:3` separately from canonical MemoryEngine provenance IDs.
4. Resolves scalar evidence references such as `D1:3` through `benchmark_turn_id`.
5. Preserves the benchmark session date/time as evidence timestamp metadata.
6. Keeps MemoryEngine turn indexing aligned with non-empty ingested messages.

For this example, the normalized evidence becomes conceptually:

```text
source_id = D1
turn_id = D1:turn_2
text = I went to a LGBTQ support group yesterday and it was so powerful.
granularity = turn
```

The benchmark answer remains `7 May 2023`; evidence resolution and answer extraction are now treated as separate concerns.

## Regression coverage

`tests/test_locomo_turn_provenance.py` now covers:

- non-empty-message turn indexing;
- per-session turn counter reset;
- public LoCoMo `D1:3` evidence-reference resolution;
- normalization of the public conversation dictionary into the experiment runner schema;
- preservation of the benchmark answer.

## Scientific interpretation

The earlier LoCoMo `n=50` result showing near-total Formation loss was **not a valid scientific finding**. The benchmark adapter had not resolved Gold Evidence references correctly and had exposed the conversation in a shape incompatible with the experiment runner.

Likewise, the earlier low Oracle Context answer accuracy cannot be interpreted as evidence of F6 reasoning failure for these records, because Oracle Context was receiving the literal evidence reference rather than the referenced evidence text.

The correct protocol is now:

```text
raw LoCoMo evidence reference
        ↓
benchmark turn resolution
        ↓
canonical provenance
        ↓
MemoryEngine ingestion
        ↓
Formation → Storage → Evolution → Retrieval → Rerank → Context
        ↓
answer evaluation
```

## Validation gate

The next required step is a **single-record end-to-end LoCoMo run** after this adapter fix. It must verify:

1. `D1:3` resolves to the expected message text;
2. normalized conversation contains the expected sessions;
3. real-memory ingestion uses matching session/turn provenance;
4. Gold Evidence is no longer reported as unresolved;
5. Oracle Context receives the actual evidence text;
6. answer scoring can compare the generated answer against `7 May 2023`.

Only after this gate passes should the larger LoCoMo experiment be rerun.
