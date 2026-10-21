# CCF-B validation plan (frozen 2026-10-21)

This supersedes the open-ended roadmap. The direction stops being "build a
memory debugging tool" and becomes a falsifiable study:

> Where do long-term memory agents actually fail? Do different memory systems
> have stable, different failure fingerprints? Can oracle intervention separate
> memory-induced loss, evidence insufficiency, evaluation error and reasoning
> failure?

The study is time-boxed by the kill line at the end of this document.

> **Model policy.** All answer, judge, reviewer and re-judge calls must use
> `DeepSeek-v4.1-flash`. Switching to any other model requires explicit user
> approval first. The earlier external review and re-judge artifacts were
> produced with `kimi-k3` without approval and are quarantined as exploratory.

## Terminology freeze

- `first-loss` may only be written as **first observable evidence-loss
  boundary**, never as the causal root cause. It is an attribution of where the
  required evidence first stops being observable, not a counterfactual claim.
- `F6` remains a *candidate* label; it is never manufactured. A near-zero F6
  after strict suffiency + semantic evaluation is itself a finding.
- Gold evidence is not ground truth for evidence sufficiency; the LLM judge is
  not an oracle. Both are instruments whose precision/recall must be measured
  against human labels.

## The validation chain

| # | Item | Current status (2026-10-21) |
|---|---|---|
| 1 | Freeze protocol and terminology | **do now** — PROTOCOL/STATUS wording; code labels unchanged |
| 2 | F3 Evolution probe: 30–50 update/conflict/stale scenarios | **done (n=40)** — evolution measured; F3-by-active-facts = 0; failures are stale-value leakage via profiles; history gate is an evaluator confound |
| 3 | Rerun LongMemEval and LoCoMo (50 → 100–200) after freeze, with bootstrap CIs | n=200 runs exist; rerun a 50-question consistency pass after the freeze |
| 4 | ≥3 memory systems / baselines, per-system Failure Fingerprint | **headline result** — LoCoMo n=43, same batch/judge/gate/budget: accuracy 0.488 / 0.465 / 0.465 (all pairwise p=1.0) but failures split F1+retrieval (semantic), F5 context (summary), F4 retrieval (verbatim) |
| 5 | Oracle ladder as the core analysis | done at n=50/200; must be reframed as the main result |
| 6 | Human labels for 100–200 samples (evidence sufficiency + answer correctness), evaluator P/R/F1; fix LoCoMo `yesterday/last Saturday/last week` semantics | **gap** — protocol + annotation package to build; needs annotators |
| 7 | F6 honesty | already the case (very few F6; 5 stored FPs refuted) |
| 8 | LoCoMo provenance/adapter | maintenance only from now on |

## F3 Evolution design

Scenarios are synthetic but controlled, so the ground-truth evidence path is
known exactly. Four families:

- **update** — S1 states V1, S2 states V2; the question asks for the current
  value. Gold = the S2 turn. Evolution succeeds iff V2 is active and V1 is
  superseded.
- **conflict** — a lower-authority source contradicts a user fact; the correct
  answer is the user fact. Success = user fact stays active, the contradiction
  is preserved as auditable conflict, not silently overwritten.
- **stale** — a state change that is not a noun substitution ("two dogs" →
  "one passed away"). Tests the boundary between extraction (F1) and
  evolution (F3).
- **history** — the question asks for the earlier value. Success = the
  superseded fact is still retrievable from history; failure = history lost.

Measurement (`tracing/engine_trace.py`, `run_oracle_experiments.py`): the
evolution stage observes only **active** semantic artifacts, and additionally
records whether gold exists in history. `F3` fires when formation and storage
found the gold turn but the active set lost it (superseded/conflicted away).
A `measured: true` flag is written per trace; existing runs stay unmeasured and
`F3` never fires for them.

Early mechanism finding (5-scenario smoke): the atomic fact set evolves
correctly (old superseded, new active, `evolution` recall 1.0), but the
parallel `profile` artifacts retain both values. The answer context therefore
contains a contradiction and the model hedges ("Lyon or Paris"), which the
frozen first-loss protocol labels F6 even though the causal story is stale-value
leakage through a second artifact channel. `trace.context.details.
stale_old_value_items` now measures the leak. This is a candidate headline:
reasoning-looking failures can be evolution failures that survive in a
different storage channel.

## Multi-system fingerprint

Each system is run through the same questions, judge, gate and lifecycle
tracer; the only change is the memory backend. Minimal viable set:

1. current engine (semantic facts + provenance + governance),
2. verbatim-window RAG (no extraction; raw turns only),
3. summary memory (LLM-compressed sessions; no provenance),
4. (if installable) a third-party OSS memory system (Mem0/A-MEM class).

Deliverable: a per-system `[F1,F2,F3,F4,F5,F6,E0]` fingerprint with bootstrap
CIs, and the pre-registered test that fingerprints differ across systems even
when final QA accuracy is within CI.

## Human evaluation

Build an annotation package: 100–200 stratified samples (correct/incorrect ×
gate sufficient/insufficient × benchmark), two annotators, blinded to system
and arm. Report evaluator precision/recall/F1 and agreement; re-run attribution
on adjudicated labels. This is the measurement fix the external reviewer called
non-negotiable; no ablation substitutes for it.

## Kill line

After the chain completes, stop and pivot if **any** of:

- multi-system failure fingerprints are not stably different (CIs overlap
  across systems in every contrast);
- F3 cannot be measured reliably on the controlled probe (human-checked
  scenarios disagree with the tracer);
- human adjudication shows attribution is unreliable or evaluator P/R is too
  low to support the claims;
- the only defensible conclusion is "we can classify errors into categories".

Pivot if none of the above blocks but effects are too small for a stable
cross-benchmark phenomenon.

Otherwise, package the paper: cross-benchmark × multi-system × large n ×
statistical significance.

## Immediate next steps

1. Freeze wording in `docs/PROTOCOL.md` (no code renames).
2. Build the evolution probe (scenarios + adapter + measured F3) and smoke it.
3. Then add the two non-LLM baselines, then the human-annotation package.
