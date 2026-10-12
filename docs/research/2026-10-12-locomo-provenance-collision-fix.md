# LoCoMo Provenance Collision Fix — 2026-10-12

## Trigger

The single-record provenance validation for `conv-26#q0000` exposed a lifecycle provenance mismatch:

```text
expected: D1:turn_2
actual:   D10:turn_2
```

The mismatch occurred for Formation and Evolution. This is a dataset/provenance alignment problem, not an F1-F6 memory failure.

## Root cause

The LoCoMo public conversation can contain a container-level session identifier that conflicts with the benchmark `dia_id` carried by its messages. The previous adapter preferred the container identifier. That allowed a message whose benchmark provenance was `D1:3` to be represented under a container such as `D10`.

For benchmark-grounded provenance, the message-level `dia_id` is authoritative. The adapter must preserve the benchmark session prefix and only fall back to the container id when no usable benchmark id exists.

## Fix

`datasets/adapters.py` now:

1. extracts the session prefix from message `dia_id` values;
2. prefers a unique non-empty benchmark session id over a conflicting container `session_id`;
3. derives each message's `source_id` from its own benchmark turn id when available;
4. keeps the existing non-empty-message turn counter semantics (`D1:turn_0`, `D1:turn_1`, ...);
5. records normalization as `locomo_refined_v4_provenance_safe_sessions`.

A regression test now explicitly constructs the failure mode:

```text
container session_id = D10
message dia_id        = D1:1, D1:2, D1:3
```

and requires all canonical provenance ids to remain under `D1`.

## New validation gate

`experiments/provenance_e2e_gate.py` was added as a fail-closed single-record gate. It builds a real MemoryEngine from one normalized LoCoMo record, inspects stored lifecycle artifacts, and verifies that Gold Evidence provenance survives Formation, Storage, and Evolution.

A provenance mismatch is reported as `PROVENANCE_ALIGNMENT` behavior and is deliberately not converted into F1-F6 attribution.

## Experimental policy

Until the single-record gate passes and a small multi-record provenance sample is clean, previous LoCoMo n=50 failure distributions remain validation-only and must not be presented as final scientific results.

Required sequence:

```text
adapter fix
  -> q0000 provenance gate
  -> small provenance sample
  -> rerun LoCoMo n=50
  -> analyze changes
  -> only then n>=100
```
