# Status Drift Pilot — Protocol v2.1 (Design Revision)

**Status:** pre-registered design revision; no v2.1 outputs exist yet.
**Branch:** `research/status-drift-v2-pilot`
**Supersedes for new runs:** the v1.0 smoke design, but not its recorded outputs.

## 1. Why revise

The v1.0 smoke test and the v1.1 judge calibration produced three conclusions:

1. The v1.0 judge was invalid (conditional inversion, broken retention field).
2. Even after v1.1, two independent judges agree on only 39/54 condition-items
   (0.722), and on only 8/18 conditional items (0.444). Single-judge labels
   cannot support a scientific claim.
3. The dataset has a design confound: odd topics are always the updated variant
   and even topics are always stable, so topic and update are perfectly
   confounded. The final turn also states the gold status almost verbatim, and
   the writer prompt explicitly instructs status preservation.

Scaling this design to 30 trajectories would multiply a confound and a judge
artifact, not add evidence. This protocol fixes the design and the measurement
before any larger run.

## 2. Design changes

### 2.1 Crossed topic × update

Each (dimension, topic) pair is rendered in **both** variants:

- `S` — status stable across the dialogue;
- `U` — status explicitly updated by later evidence.

Topic no longer predicts update. The smoke set is 3 dimensions × 2 topics ×
2 variants = 12 trajectories; the full set is 3 × 5 × 2 = 30.

### 2.2 Neutral writer control

Two writer prompts, otherwise identical:

- `status_aware` — the v1.0 prompt, which names proposition, certainty,
  intention strength, and condition satisfaction, and forbids status inflation.
- `neutral` — "compress into one concise memory, preserve important information",
  with no status instruction and no status vocabulary.

The primary comparison is `status_aware` vs `neutral`. A drift effect that only
appears under `neutral` is evidence about default compression, not about the
status-aware writer, and must be reported as such.

### 2.3 Deterministic proposition retention

A per-topic keyword set is defined in the runner. For each memory,
`proposition_match = any(keyword in memory)`. This is independent of any judge.

- Report both deterministic and judge-based retention.
- CPSD denominators use **deterministic** retention.
- Judge-based retention remains a secondary signal; disagreements are reported.

### 2.4 Two-step judge

The judge must first quote the **latest status-bearing span** in the text, then
assign a label that follows that span. It also reports `conflict_present` when
earlier and later spans disagree.

Required JSON fields:

    {"status": "...", "latest_evidence": "...", "conflict_present": true/false,
     "proposition_retained": true/false, "confidence": "high|medium|low"}

The judge prompt states that a later explicit confirmation overrides an earlier
uncertainty statement, and that "condition not satisfied" is not proposition
omission.

### 2.5 Multi-judge adjudication

Every condition-item is judged by `qwen2.5:7b` and `gemma3:12b`.

- Substantive claims use only items where both judges agree.
- Disagreements are manually (assistant) adjudicated and reported separately.
- Inter-judge agreement is a reported metric, not a footnote.

### 2.6 Determinism

Pass an explicit Ollama `seed`. On a stratified subset, re-judge the same text
twice and report label stability.

### 2.7 Regression tests

Before any run:

- crossed dataset balance (each dimension × topic appears as S and U);
- deterministic retention on known strings;
- memory lookup uses string depth keys and never judges empty text.

## 3. Metrics

- Raw / direct / recursive status accuracy, per dimension.
- Deterministic proposition retention and omission.
- CPSD with deterministic denominator.
- Legitimate-transition accuracy (updated subset).
- Recursive-minus-direct paired error delta.
- Inter-judge agreement, overall and per dimension.
- Self-consistency under repeated judging.
- `status_aware` vs `neutral` writer difference.

Always report raw counts and denominators. No significance tests on n=12/30.

## 4. Pre-registered directional predictions

- **P1:** the `neutral` writer preserves status less often than `status_aware`.
- **P2:** recursive depth increases stale-uncertainty phrasing relative to
  direct compression at the same target budget, if a recursion effect exists.
- **P3:** deterministic retention ≥ judge-based retention (judges false-negative
  on omission).
- **P4:** conditional items are the least reliable dimension across judges.

These are predictions, not findings. A null result is a valid outcome.

## 5. Decision gates for the v2.1 smoke (n=12)

Proceed to the 30-trajectory run only if:

- inter-judge agreement ≥ 0.85 overall and ≥ 0.80 per dimension;
- deterministic omission < 10%;
- all disagreements manually adjudicated;
- at least 3 items have deterministic retention true and **both judges agree**
  the status is wrong, or the recursion/direct contrast is null and clearly
  reported.

If any gate fails, revise the instrument or design again; do not scale.

## 6. Integrity

- v1.0 and v1.1 outputs remain on disk; nothing is overwritten.
- No prompt is tuned to produce a desired substantive result; only label
  semantics and retention measurement are clarified.
- Synthetic templates only; assistant adjudication is not human ground truth.
- No novelty claim before the four plan-named works are verified.
