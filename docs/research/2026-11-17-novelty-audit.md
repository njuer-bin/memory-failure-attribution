# V3 Novelty Audit — Full-Text Version (2026-11-17)

**Scope:** full-text audit of 14 papers downloaded to `literature/pdfs/` and
extracted to `literature/pdfs_txt/`. This supersedes the earlier
abstract-only audit. The audit is about whether the V3 claim is novel, not
whether the papers are good.

**The claim under audit.** V3 measures **status-specific loss under recursive
memory rewriting**: even when the target proposition survives, its epistemic /
intentional / conditional status may be omitted or distorted, and the two
outcomes have different downstream consequences.

## 1. Full-text comparison

| Paper | Core measurement | Transformation history controlled? | Proposition vs status separated? | Status modality measured? | Status-only downstream? | Human labels? | Overlap verdict |
|---|---|---|---|---|---|---|---|
| **StateMem / StateMemBench** (2608.19652) | State tracking vs recall; current vs superseded state; 234 multi-session scenarios; five failure modes (Status, Salience, Sequence, Compound, Anti-trap). | No: final QA over full/retrieved context, not rewriting histories. | No: state is the answer target, not a status tuple attached to a proposition. | No. | No: QA answers, not a present/omitted/distorted intervention. | Yes: judge labels + two human annotators. | **Closest on the phenomenon** (state drift independent of recall). Not the V3 mechanism or status ontology. |
| **ProgMem** (AACL 2026 Findings) | Structured memory programs over stable/dynamic/plan subspaces; temporal updates, plan changes, counterfactuals, evidence checks. | No: structured writes, not chained summary rewriting. | No: state is represented, not measured against gold per proposition. | Partially (temporal/plan/uncertainty), not epistemic/intentional/conditional fidelity. | No. | No. | Overlap on structured state representation; not on transformation history or status fidelity. |
| **BELIEFMEM** (EMNLP 2026 Findings) | AGM belief revision (EXP/REV/DUP/CON), history-preserving belief base, lineage pointers. | No: belief-revision write semantics. | No. | No status-fidelity measurement. | No. | No. | Overlap on belief revision/uncertainty; not on chained rewriting. |
| **STALE** (2605.06527) | Implicit conflict; State Resolution, Premise Resistance, Implicit Policy Adaptation; 400 scenarios, 1,200 queries. | No. | No: latent user state, not proposition-status tuples. | No. | **Yes:** downstream policy adaptation is one probe. | Yes: expert-validated; judge protocol. | **Closest on downstream behavior.** V3 cannot claim first stale-state → behavior. |
| **StateAuditor** (2608.01619) | Repairs the STALE IPA gap via state-to-draft transition verification. | No. | No. | No. | Yes: response repair. | No. | Overlap on downstream state-to-behavior repair. |
| **MemDerive** (2610.25373) | Derived-state benchmark; Datalog gold DAG; failures where the intermediate state exists but is not retrieved/propagated. | No. | No: derived state, not status. | No. | No. | Gold DAG, no human status labels. | Overlap on state derivation/tracking; not status. |
| **ABBEL** (2512.20111) | Recursive summarization into explicit natural-language belief states; diagnoses omission and incorrect updates; RL fine-tuning. | **Yes: recursive summaries.** | No: belief-state content vs task performance; no proposition-level status coding. | No. | Task performance, not status-only intervention. | No. | **Closest on recursive summarization + omission.** V3 cannot claim first recursive-summary omission. |
| **Supersede** (2606.27472) | Bounded notes memory rewritten after each session; raw history never re-fed; supersession accuracy; failure grows with conversation length, not compression ratio. | **Yes: chained rewriting of bounded memory.** | No: fact currency / current value, not status modality. | No. | Final answer correctness; stale-value penalty. | No. | **Closest on chaining mechanism.** V3 cannot claim first "chaining hurts"; must claim status-specificity. |
| **LiveCtx** (Discover Computing 2026) | Preserves original sessions; query-time selection; compresses the selected set once; compares with rolling/summary compression. | No: source-preserving alternative. | No. | No. | QA accuracy. | No. | **Source access is already a studied idea.** P5 cannot claim it as novel. |
| **ReSum** (2509.13313) | Periodic summary tool; recursive context compression for search agents. | Yes: recursive summaries. | No. | No. | Task success. | No. | Recursive summarization is prior work. |
| **LightMem** (2510.18866) | Three-stage memory: compression, topic-aware short-term, sleep-time consolidation. | Compression/consolidation, not paired histories. | No. | No. | QA accuracy. | No. | Compression lifecycle is prior work. |
| **MemTX** (2607.23929) | Transactional belief commit; action-safety gating; cascade repair. | No. | No: belief commit vs action, not status fidelity. | No. | Yes: action gating / downstream harm. | No. | Memory state → action is prior work. |
| **EAL-Bench** (2609.01836) | Writer → memory → executor; false authority formation and propagation; one-shot vs incremental typed updates; 45.4% formation, 99% propagation. | Partially: incremental writes; not paired compression histories. | No: authorization state, not status modality. | No. | **Yes:** unauthorized actions. | No. | **Closest on memory-state → action.** V3 cannot claim first downstream harm. |
| **TWIST** (2609.28575) | Intervention quality at belief change points; contradiction detection, draft vetting, supersession, safe recall; human-validated κ 0.85. | No. | No: intervention behavior, not proposition-status fidelity. | No. | Intervention decisions. | Yes: benchmark validation. | Belief-change intervention is prior work. |

## 2. What is clearly not novel

- **State tracking as a problem distinct from recall:** StateMem.
- **Structured belief/state representation:** ProgMem, BELIEFMEM, PoS.
- **Uncertainty-preserving or belief-revising memory:** BeliefMem, BELIEFMEM,
  Agent-BRACE.
- **Recursive summarization and omission/update errors under it:** ABBEL,
  ReSum, Supersede.
- **Chained rewriting harming information:** Supersede (length, not compression
  ratio), LiveCtx's critique of rolling summaries.
- **Memory state → downstream behavior/unauthorized action:** STALE,
  StateAuditor, MemTX, EAL-Bench.
- **Source access / preserving raw history:** LiveCtx.
- **Intervention-quality evaluation at belief change points:** TWIST.

## 3. The defensible gap

No audited paper combines:

1. **A target proposition with an explicit status tuple** (epistemic,
   intentional, conditional, action) measured against gold;
2. **Paired transformation histories** on the same dialogue: direct, recursive,
   rewrite-matched, repeated-direct, and source-access;
3. **Proposition identity held fixed**, so status loss is separated from
   proposition loss;
4. **Status omission vs unsupported distortion as distinct outcomes**;
5. **Blind human labels** under a calibrated ontology;
6. **A status-only downstream intervention** (present / omitted / distorted)
   with proposition content held constant;
7. **A second-model replication** of the behavioral asymmetry.

The closest papers cover one or two ingredients:

- StateMem/STALE/MemDerive: state tracking and derived state, but not
  rewriting histories or status tuples.
- ABBEL/Supersede/ReSum/LiveCtx: recursive rewriting or source access, but not
  status fidelity or proposition-controlled measurement.
- EAL-Bench/MemTX/STALE: memory state → action, but authorization/stale state,
  not epistemic/intentional/conditional status.
- ProgMem/BELIEFMEM: state representation/update, but no paired
  transformation-history experiment.

**Claim:** a **status-specific, proposition-controlled transformation-history
diagnostic**. The novelty is the combination and the measurement target, not the
existence of state tracking, recursive summarization, or memory→action effects.

## 4. Claim guardrails

**Say:**

- "status-specific loss under chained rewriting";
- "proposition identity held fixed";
- "paired transformation histories, separating chaining from budget and call
  count";
- "omission vs unsupported distortion";
- "status-only downstream intervention";
- "source access removes the loss in qwen; the mitigation ranking is
  model-dependent";
- "second-model replication of the behavioral asymmetry".

**Do not say:**

- first to study state tracking / status in agent memory (StateMem);
- first structured belief-state memory (ProgMem, BELIEFMEM);
- first uncertainty-preserving memory (BeliefMem, Agent-BRACE);
- first recursive summarization or first evidence that chaining loses
  information (ABBEL, Supersede, ReSum);
- first memory state → action or unauthorized action (STALE, MemTX, EAL-Bench);
- source access is novel (LiveCtx);
- unsupported distortion is common (0.9% here);
- the v2 intentional-specific claim is confirmed.

## 5. Reviewer questions to prepare for

1. **"How is this different from StateMem/STALE?"** StateMem/STALE measure final
   state tracking/behavior; V3 measures whether the *writer's transformation
   history* changes the status representation while the proposition survives.
2. **"How is this different from ABBEL/Supersede?"** ABBEL/Supersede study
   recursive summarization and fact currency; V3 adds a status tuple,
   proposition-controlled human labels, and the omission/distortion split.
3. **"How is this different from EAL-Bench?"** EAL-Bench measures authorization
   state → action; V3 measures epistemic/intentional/conditional status →
   action, with present/omitted/distorted manipulation.
4. **"Isn't source access just LiveCtx?"** LiveCtx preserves raw history;
   V3's contribution is showing source access removes *status* omission in
   chained rewriting, and that the mitigation ranking is model-dependent.
5. **"Why should we care about 0.9% unsupported distortion?"** Because it is
   behaviorally dangerous (66.7% unauthorized in P4), while the dominant
   omission failure is conservative. The two outcomes must be reported
   separately.

## 6. Remaining risks

- The synthetic template family may make the status manipulation cleaner than
  real dialogue; natural-dialogue replication is still missing.
- The writer-side replication is model-dependent and uses 12 trajectories.
- Human annotation is model-assisted at adjudication; provenance is
  unrecorded.
- Supersede/ABBEL appendix check completed 2026-11-19 (§8): neither contains a
  proposition-controlled status split.
- The "status-only downstream" design is novel in this combination, but the
  general memory→action finding is not.

## 7. Sources (full text in `literature/pdfs/`)

- StateMem: `2608.19652_statemen.pdf`
- ProgMem: `2026.findings-aacl.120_progmem.pdf`
- BELIEFMEM: `2026.findings-emnlp.576_beliefmem.pdf`
- STALE: `2605.06527_stale.pdf`
- StateAuditor: `2608.01619_stateauditor.pdf`
- MemDerive: `2610.25373_memderive.pdf`
- ABBEL: `2512.20111_abbel.pdf`
- Supersede: `2606.27472_supersede.pdf`
- LiveCtx: `s10791-026-10807-5_livectx.pdf`
- ReSum: `2509.13313_resum.pdf`
- LightMem: `2510.18866_lightmem.pdf`
- MemTX: `2607.23929_memtx.pdf`
- EAL-Bench: `2609.01836_ealbench.pdf`
- TWIST: `2609.28575_twist.pdf`

## 8. Appendix check — ABBEL and Supersede (2026-11-19)

The remaining open risk was that ABBEL or Supersede already contains a
proposition-controlled status split in its appendices. Both PDFs were
re-extracted with `pdftotext -layout` and read to the end.

**ABBEL (2512.20111).** Appendices: A prompts and environment details, B belief
state examples, C.1 reasoning lengths, C.2 unnecessary belief-state
reconstruction, C.3 hallucinating past observations during belief update. The
paper's error analysis separates *omitting information* from *incorrectly
updating information*, and C.3 documents hallucinated observations. Evaluation
is task success, not status fidelity; there is no proposition-identity control,
no typed status, and no human status annotation. Overlap: omission and
hallucinated update under recursive summarization. Non-overlap: the status
tuple, proposition-controlled pairing, and the omission/distortion split
measured on proposition-preserved items.

**Supersede (2606.27472).** Appendices: A reward/matcher details, B additional
results, C two procedurally generated training episodes. The whole design is a
bounded-notes memory rewritten per session, evaluated by whether the final
answer conveys the current value rather than a superseded one. The related-work
section notes that multi-session dialogue work "does not annotate a dedicated
update category", which is also true of Supersede itself. No status dimension,
no uncertainty/authorization state, no human annotation. Overlap:
chained-rewriting harm. Non-overlap: what is lost (status vs value) and the
downstream status-only intervention.

Verdict: the defensible-claim wording in `research-state.yaml` stands. Remove
the "check before submission" risk item; both checks are now done.
