# V3 Novelty Audit (2026-11-17)

**Scope:** abstract- and metadata-level audit of the closest memory, belief,
compression, state-tracking, and agent-safety work. arXiv abs pages were blocked
by the local fetch policy; abstracts were verified through OpenAlex and the
existing AlphaXiv summaries. **Full texts and appendices are still required
before a submission novelty claim.**

## 1. The claim under audit

V3 measures **selective status loss under recursive memory rewriting**: even
when the target proposition survives, its epistemic / intentional / conditional
status may be omitted or distorted, and the two outcomes have different
downstream consequences.

## 2. The three closest papers

### StateMem / StateMemBench (2608.19652)

- Defines **state tracking** as distinct from recall: answers must reflect the
  current state, not a superseded one.
- StateMemBench: 234 multi-session scenarios, closed-pool grading into current
  state / superseded state / other failure.
- StateMem explicitly tracks supersession and relational dependencies; +32 to
  +67 points as a wrapper over six memory backends.
- Per the maintainer's audit, it also separates State, Salience, Sequence,
  Compound, and Anti-trap failure categories (full text pending).
- **Overlap:** state tracking is independent of fact retrieval; stale state can
  survive even when the fact is in context.
- **Difference:** StateMem studies whether an agent *tracks a changing world
  state*; V3 studies whether *repeatedly rewriting the memory itself* changes
  the status representation, holding the proposition and source fixed.

### ProgMem (Findings of AACL 2026)

- Compiles dialogue events into **structured memory programs**, with evidence
  checks, temporal updates, plan changes, counterfactual reasoning, and
  uncertainty when evidence is insufficient.
- Strong on temporal F1 and query-time state maintenance.
- **Overlap:** structured belief/state representation is already a published
  idea; proposing a tuple of epistemic/intentional/conditional/action state is
  not a novelty.
- **Difference:** ProgMem is a memory-maintenance architecture; it does not run
  the controlled transformation-history comparison (direct vs recursive vs
  rewrite-matched vs repeated-direct) with proposition identity held fixed.

### BELIEFMEM (Findings of EMNLP 2026)

- Applies AGM belief revision (EXP/REV/DUP/CON) to a history-preserving belief
  base; superseded beliefs retain predecessor pointers; query-time selection of
  head / chain / neither.
- **Overlap:** belief revision, uncertainty preservation, and avoiding
  contradictory coexisting beliefs are prior work.
- **Difference:** BELIEFMEM is a write-semantics architecture; it does not
  measure whether *chained rewriting of a summary* selectively erases status
  while the proposition survives.

## 3. Other close work

| Paper | What it covers | Impact on the claim |
|---|---|---|
| **STALE** (2605.06527) | Implicit conflict; State Resolution, Premise Resistance, Implicit Policy Adaptation; downstream behavior; best model 55.2%. | Cannot claim first evidence that stale state changes downstream behavior. |
| **StateAuditor** (2608.01619) | Repairs the STALE implicit-policy-adaptation gap with transition verification. | Downstream state→behavior repair is already studied. |
| **MemDerive** (2610.25373) | Derived-state benchmark; failures where the intermediate state exists but is not retrieved/propagated. | State tracking and derivation failures are already benchmarked. |
| **ABBEL** (2512.20111) | Recursive summarization into explicit natural-language belief states; notes omission/incorrect updates; RL fine-tuning. | Recursive summarization and belief-state omission are already studied; V3 must isolate the transformation-history mechanism. |
| **Agent-BRACE** (2605.11436) | Atomic belief claims + verbalized certainty; policy decoupled from belief; long-horizon embodied tasks. | Belief/action separation and certainty labels are prior work. |
| **BeliefMem** (2605.05583) | Probabilistic candidate beliefs with Noisy-OR updates; LoCoMo/ALFWorld. | Uncertainty-preserving memory is prior work. |
| **MemCoRe** (2602.07885) | Compression hierarchy and cross-level evidence retrieval. | Progressive compression/evidence retrieval is prior work. |
| **MemTX** (2607.23929) | Transactional belief commit; action-safety gating; stale writes can drive irreversible actions. | Memory state → action authorization is prior work. |
| **EAL-Bench** (2609.01836) | Memory misrepresents authorization state; 45.4% false authority, 99% executor action. | Memory errors → unauthorized action is prior work. |
| **Revoked but Still Authoritative** (2609.08258) | Revoked facts remain retrievable and drive unsafe actions. | Stale/revoked state → action is prior work. |
| **TWIST** (2609.28575) | Intervention-quality benchmark at belief change points; human-validated κ 0.85. | Intervention quality is prior work; V3 is not the first belief-change evaluation. |
| **PoS** (2610.01415) | Explicit belief states + consistency validation/recovery. | Explicit state maintenance is prior work. |
| **TOKI** (2606.06240) | Bitemporal contradiction resolution for persistent memory. | Write-time contradiction resolution is prior work. |
| **Supersede / LiveCtx / LightMem / ReSum** (maintainer audit) | Knowledge-update failures in real dialogue; source-preserving query-time selection; compression/integration lifecycle; recursive summarization. | Source access and recursive summarization are adjacent, not novel. Full texts pending. |

## 4. Novelty verdict

**No longer defensible as primary novelty:**

- discovering that memory has a state-tracking problem independent of recall
  (StateMem);
- proposing structured epistemic/intentional/conditional/action state
  (ProgMem, BELIEFMEM, PoS);
- preserving uncertainty or revising beliefs (BeliefMem, BELIEFMEM, Agent-BRACE);
- showing that stale memory changes downstream behavior (STALE, StateAuditor,
  MemTX, EAL-Bench);
- source access or recursive summarization as a method idea (LiveCtx, ReSum,
  ABBEL).

**Defensible core:** a **controlled transformation-history experiment** that
isolates a selective failure of recursive re-editing:

1. the same dialogue is transformed through direct, recursive, rewrite-matched,
   repeated-direct, and source-access histories;
2. **proposition identity is held fixed** while status fidelity is measured;
3. **status omission and unsupported distortion are separate outcomes**;
4. the design separates **chaining** from intermediate budget shrinkage and raw
   call count;
5. blind human labels under a calibrated ontology, plus a status-only downstream
   intervention (present / omitted / distorted) and a second-model replication.

StateMem, ProgMem, BELIEFMEM, STALE, and ABBEL each cover part of the
phenomenon. None audited here runs this specific paired transformation-history
experiment with proposition-controlled status outcomes.

## 5. Claim guardrails

**Say:**

- "controlled diagnostic of path-dependent status representation loss under
  chained rewriting";
- "status omission vs unsupported distortion, separated from proposition loss";
- "chained re-editing, not budget shrinkage or call count";
- "source access removes the loss in qwen; the mitigation ranking is
  model-dependent";
- "omission is behaviorally conservative; distortion is behaviorally dangerous";
- "second-model replication of the behavioral asymmetry".

**Do not say:**

- first to study state tracking or status in agent memory;
- first belief-state or uncertainty-preserving memory;
- first to show memory errors affect actions;
- a new memory architecture or a universal mitigation;
- source access is novel or universally sufficient;
- unsupported distortion is common (0.9% here);
- the v2 intentional-specific claim is confirmed.

## 6. Required full-text audit

1. StateMem (2608.19652) — closest; confirm the failure taxonomy and whether it
   separates proposition identity from status.
2. ProgMem (AACL 2026 Findings) — confirm no transformation-history control.
3. BELIEFMEM (EMNLP 2026 Findings) — confirm no chained-rewrite status measure.
4. STALE (2605.06527) and StateAuditor (2608.01619) — downstream behavior.
5. ABBEL (2512.20111) — recursive summarization and omission.
6. MemTX (2607.23929), EAL-Bench (2609.01836), Revoked (2609.08258) — memory
   state → action.
7. Supersede, LiveCtx, LightMem, ReSum — resolve full texts and exact claims.

## 7. Sources

- arXiv:2608.19652, arXiv:2605.05583, arXiv:2602.07885, arXiv:2605.11436,
  arXiv:2512.20111, arXiv:2607.23929, arXiv:2609.28575, arXiv:2610.01415,
  arXiv:2610.25119, arXiv:2609.01836, arXiv:2609.08258, arXiv:2609.12354,
  arXiv:2608.30508, arXiv:2610.07309, arXiv:2605.06527, arXiv:2608.01619,
  arXiv:2610.25373, arXiv:2606.06240.
- AACL 2026 Findings: ProgMem (`2026.findings-aacl.120`).
- EMNLP 2026 Findings: BELIEFMEM (`2026.findings-emnlp.576`).
