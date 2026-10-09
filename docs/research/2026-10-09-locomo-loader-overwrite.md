# LoCoMo loader overwrite diagnosis

## Validation result

The first single-record end-to-end LoCoMo run still reported `F1_FORMATION`, while Oracle Memory and Oracle Context both had the expected evidence text. The result was initially suspicious because the raw conversation contains 19 sessions but the experiment logged only 11 sessions.

Inspection of `datasets/loader.py` identified the exact cause.

`normalize_locomo_refined()` already converts the public LoCoMo conversation object into the canonical runner schema: a list of session records with `session_id` and `messages`. However, `iter_normalized()` then overwrites that normalized value with the raw public conversation object:

```python
record = normalize_locomo_refined(raw, index=idx, conversation=conversation)
cid = record.get("conversation_id")
if cid and cid in conversations:
    record["conversation"] = conversations[cid]
```

The raw public object is a dict containing metadata keys such as `sample_id`, `conversation_idx`, `speaker_a`, `speaker_b`, `session_count`, `message_count`, `sessions`, etc. The experiment runner `_sessions()` expects `record["conversation"]` to be a list. Iterating the raw dict therefore iterates its keys rather than its sessions. This explains the observed `11 sessions` log: the runner was counting the raw conversation dict's top-level keys as sessions.

## Consequence

The observed `F1_FORMATION` is not a scientific formation failure. It is an adapter/loader schema overwrite that prevents the experiment runner from ingesting the actual LoCoMo sessions.

The Gold Evidence itself is already correct:

- benchmark reference: `D1:3`
- canonical source: `D1`
- canonical turn: `D1:turn_2`
- evidence text: `I went to a LGBTQ support group yesterday and it was so powerful.`

Oracle Memory correctly receives this evidence, confirming that evidence normalization is working.

## Required fix

Remove the post-normalization overwrite from `iter_normalized()` and yield the canonical record returned by `normalize_locomo_refined()` unchanged:

```python
record = normalize_locomo_refined(raw, index=idx, conversation=conversation)
yield record
```

After this fix, the single-record run should report the actual session count (19 for `conv-26`) and should be rerun before any scientific interpretation or larger LoCoMo experiment.

## Separate scoring observation

The same single-record run also produced `Yesterday.` from Oracle Memory/Oracle Context while the benchmark reference answer is `7 May 2023`. Token-F1 therefore marked the answer incorrect. This is a separate answer-scoring calibration issue: the evidence plus the session date makes `yesterday` semantically resolve to `7 May 2023`. It should not be conflated with the loader/provenance bug or used as evidence of F6 until answer scoring is benchmark-aligned.

## Scientific status

The current single-record output is a debugging artifact, not a valid LoCoMo result. The previous n=50 LoCoMo results remain invalid for scientific claims until this loader issue and the answer-scoring calibration are resolved.
