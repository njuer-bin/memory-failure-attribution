# Status — where to resume

Last updated: 2026-10-21 (P2 LoCoMo n=200 complete; ablation plan written by an
independent reviewer; Phase-0 audit done; next gate is the A1 placebo run).

This is the single resume point. History and reasoning live in
`docs/RESEARCH_LOG.md`; definitions live in `docs/PROTOCOL.md`.

## Repo state

- Branch: `fix/formation-diagnostics-evidence-based`
- The 2026-10-18 audit repairs, the 2026-10-19 ordering-refutation layer, the
  2026-10-20 P2 intervention layer, and the 2026-10-21 same-sample analysis
  script are on this branch. All of it is uncommitted; run artifacts live under
  gitignored `results/`.
- `python -m pytest tests/` → 142 passed (verified 2026-10-21).

## Result artifacts

| path | valid? |
|---|---|
| `results/oracle_experiments_n50_final/` | **yes — canonical n=50 run** (`resumed_records: 0`, `errors: 0`) |
| `.../judge_reliability_self.json` | yes — same-judge self-consistency (kappa 1.0, 0 flips) |
| `.../judge_reliability_gemma3.json` | yes — cross-model estimate (raw_judge agreement 0.71, kappa ≈ 0.03) |
| `results/oracle_experiments_locomo_n50_v3/` | **yes — LoCoMo n=50**, qwen→deepseek-v4.1-flash via gateway; `resumed_records: 33` (interrupted by host memory, resumed under the same protocol), `errors: 0`, semantic errors 4/147 judge calls |
| `results/oracle_experiments_locomo_n200/` | **yes — canonical LoCoMo n=200**, deepseek-v4.1-flash, `errors: 0`, `resumed_records: 178`; embedding `hash:384` |
| `results/interventions_longmemeval_n200/` | **yes — P2 three-arm intervention, LongMemEval n=200**, `errors: 0`, one resume from 69/200 |
| `results/interventions_locomo_n200/` | **yes — P2 three-arm intervention, LoCoMo n=200**, 200×3 rows, `errors: 0`, `status: completed` (resumed 168→200 on 2026-10-21) |
| `results/analysis_interventions_locomo_n200.json` | same-sample analysis of the LoCoMo intervention (`experiments/analyze_interventions.py`) |
| `results/analysis_interventions_longmemeval_n200.json` | same-sample analysis of the LongMemEval intervention; reproduces every number quoted below |
| `results/analysis_locomo_n200.txt` | analysis output for the LoCoMo n=200 run |
| `results/oracle_experiments_locomo_n5_v2/` | smoke test, 0 semantic errors after the retry fix |
| `results/oracle_experiments_locomo_n50/` | **no — negative**: max_tokens truncation, 58 empty judge responses |
| `results/oracle_experiments_locomo_n50_v2/` | **no — interrupted run** (memory), superseded by v3 |
| `results/oracle_experiments_n50_orderrefuted/` | instrument-refinement rescore (stored verdicts + `--apply-ordering-refutation`; NOT a fresh run) |
| `results/analysis_n50_final.txt` | analysis output for the canonical run |
| `results/oracle_experiments_n50_repaired/` | **no — negative result.** `resumed_records: 38`; 38/50 rows inherited by `--resume` from pre-fix output |
| `results/oracle_experiments_n50_rescored/` | **no — instrument comparison only** |
| `results/archive/n50_lexical_2026-10-18/` | negative result, withdrawn numbers |
| `results/oracle_experiments/` | abandoned partial run (killed by host memory pressure) |

## Canonical n=50 numbers (LongMemEval oracle, `5a6a52e1a98f85eb`)

Lifecycle recall — Real Memory formation 0.503, storage 1.00, retrieval 1.00,
rerank 0.993, context 0.880; Oracle Memory retrieval 1.00, rerank 1.00, context 0.982;
Oracle Context context 1.00. First-loss (Real): formation 36, context 1, none 13.

Answer failure attribution (canonical run + ordering refutation applied):

| mode | none | F1 | F5 | F6 | E0 | RC | EVAL |
|---|---|---|---|---|---|---|---|
| real_memory | 28 | 14 | 1 | 5 | 2 | — | 0 |
| oracle_memory | 30 | 0 | 1 | 16 | 2 | — | 1 |
| oracle_context | 31 | 0 | 1 | 0 | 2 | 16 | 1 |

Five stored judge false positives were refuted (`gpt4_2487a7cb` ×3, `gpt4_1a1dc16d`
×2). Semantic accuracy RM 19/41, OM 23/42, OC 25/43. Paired McNemar non-significant
across all three conditions (p = 0.7266, 0.4531, 1.0000); bootstrap CIs straddle 0.

## Judge reliability (2026-10-19)

- **Self-consistency** (qwen2.5:7b re-judged by qwen2.5:7b, temperature 0):
  123 answer verdicts + 50 gate re-checks, **zero flips, kappa 1.0** — the judge
  is deterministic under the protocol, so re-running it adds no information.
- **Cross-model** (gemma3:12b): `correct_verdict` agreement 0.927, kappa 0.849
  with 9 flips (all gemma3-side loosening: stored False → rerun True);
  `raw_judge` agreement 0.710, kappa ≈ 0.03 — the two models' raw verdicts are
  statistically near-independent. **Conclusion: an LLM judge alone cannot
  support a paper-grade F6 number.**
- Both models reproduce the `gpt4_2487a7cb` false positive; cross-model
  adjudication does not fix ordering false positives.

## Instrument fix: deterministic ordering refutation

Root cause of the F6 undercount: the pre-2026-10-19 evaluator had only
false-negative repair paths (temporal, lexical, numeric) and no path that could
overturn a judge false positive. 30 of 45 stored `semantic_correct=True` rows
whose answer differs lexically from the gold were two-option ordering
questions ("Which ... first, A or B?") where the candidate names the *wrong*
option — provably wrong because the evidence dates resolve the order.

The fix (`evaluation/answer_semantic_eval.py::_ordering_refutes_judge`,
applied inside `evaluate_answer` and offline via
`experiments/rescore_answers.py --apply-ordering-refutation`) flips a verdict
only when ALL of: (1) ordering question with exactly a two-option tail;
(2) the candidate names exactly one option; (3) each option's supporting
sentence carries a resolvable explicit or relative date, and the picked
option's date is strictly later than the other's. Everything ambiguous stays
with the judge. Known limitation: rows whose option binding crosses sentence
boundaries (e.g. "necklace for my sister" with "for my sister" in another
sentence) remain judge-decided.

## LongMemEval n=200 (DeepSeek-v4.1-flash, `results/oracle_experiments_longmemeval_n200/`)

200 records, errors 0, resumed 0. Gate sufficient 153 / insufficient 41 / error 6.
Semantic accuracy RM 0.521, OM 0.691, OC 0.821. **All pairwise contrasts
significant** (McNemar p = 0.0041 / <0.0001 / 0.0414; bootstrap CIs exclude 0).

| mode | none | F1 | F4 | F5 | F6 | E0 | RC | EVAL |
|---|---|---|---|---|---|---|---|---|
| real_memory | 116 | 61 | 1 | 1 | 3 | 10 | — | 8 |
| oracle_memory | 151 | 0 | 0 | 20 | 10 | 11 | — | 8 |
| oracle_context | 174 | 0 | 0 | 0 | 0 | 13 | 10 | 3 |

First-loss: RM formation 155, context 4, rerank 2, none 39; OM context 29, none 171.

## LoCoMo n=50 (DeepSeek-v4.1-flash via opencode gateway, `results/oracle_experiments_locomo_n50_v3/`)

Gate: sufficient 32 / insufficient 17 / error 1. Semantic accuracy RM 28/49 (0.571),
OM 37/49 (0.755), OC 37/47 (0.787).

| mode | none | F1 | F4 | F5 | F6 | E0 | RC | EVAL |
|---|---|---|---|---|---|---|---|---|
| real_memory | 28 | 5 | 3 | 1 | 2 | 10 | — | 1 |
| oracle_memory | 37 | 0 | 1 | 0 | 5 | 6 | — | 1 |
| oracle_context | 38 | 0 | 0 | 0 | 0 | 6 | 4 | 2 |

Retrieval recall differs sharply from LongMemEval: RM retrieval 0.560, rerank 0.515,
context 0.360; OM retrieval/rerank/context 0.810/0.810/0.805. The LoCoMo failure
profile is retrieval-heavy (F4 = 4 rows across modes; gate insufficient = 17), unlike
LongMemEval's formation-heavy profile. This is the cross-benchmark contrast the
roadmap's P0 gate asked for; n=50 only, no significance claim yet.

## LoCoMo n=200 (DeepSeek-v4.1-flash, `results/oracle_experiments_locomo_n200/`)

200 records, `errors: 0`, `resumed_records: 178` (four host-memory interruptions).
Gate: sufficient 106 / insufficient 86 / error 8 — **43% E0**, much weaker
gold/question pairing than LongMemEval's 20.5%. Semantic accuracy RM 70/173
(0.405), OM 144/173 (0.832), OC 150/176 (0.852). Analysis:
`results/analysis_locomo_n200.txt`.

| mode | none | F1 | F4 | F5 | F6 | E0 | RC | EVAL |
|---|---|---|---|---|---|---|---|---|
| real_memory | 0* | 39 | 10 | 5 | 2 | 43 | — | 23 |
| oracle_memory | 0* | 0 | 6 | 1 | 7 | 15 | — | 6 |
| oracle_context | 0* | 0 | 0 | 0 | 0 | 14 | 11 | 3 |

\*the summary's failure dict omits `None`; semantic-correct counts are above.

| contrast | n01 | n10 | p | diff | 95% CI |
|---|---|---|---|---|---|
| RM vs OM | 73 | 6 | <0.0001 | −0.432 | [−0.523, −0.348] |
| RM vs OC | 78 | 7 | <0.0001 | −0.452 | [−0.541, −0.357] |
| OM vs OC | 14 | 10 | 0.5413 | −0.025 | [−0.081, 0.037], n.s. |

Lifecycle recall RM formation 0.335, storage 0.995, retrieval 0.669, rerank
0.543, context 0.322; OM retrieval/rerank/context 0.872/0.872/0.867. The
retrieval-heavy profile persists at n=200, and unlike LongMemEval the OM→OC
contrast is no longer significant: after gold evidence is written to memory,
LoCoMo's remaining loss is retrieval/context, not reasoning.

## P2 intervention — LongMemEval n=200 complete 2026-10-20

`results/interventions_longmemeval_n200/`: 200 questions × 3 arms, `errors: 0`,
`progress.json` `status: completed`, one resume from 69/200. `summary.json` has
the per-arm tables; the numbers below are from it plus an offline same-sample
recomputation over `interventions.jsonl` (not a new run).

Per-arm paired semantic accuracy on each arm's own scored subset:

| arm | paired n | baseline correct | repaired correct | gain | McNemar p |
|---|---|---|---|---|---|
| first_loss | 51 | 1 | 13 | +23.5 pts | 0.0005 |
| path | 47 | 2 | 11 | +19.1 pts | 0.0039 |
| agnostic | 41 | 2 | 23 | +51.2 pts | 9.5e-07 |

The paired subsets differ by arm, so the fair comparison is the 34 questions
scored in all three arms:

| arm | baseline → repaired | gain | McNemar p | bootstrap CI (baseline − repaired) |
|---|---|---|---|---|
| first_loss | 1 → 8 /34 | +20.6 pts | 0.0156 | [−0.353, −0.088] |
| path | 1 → 9 /34 | +23.5 pts | 0.0078 | [−0.382, −0.088] |
| agnostic | 1 → 18 /34 | +50.0 pts | 1.5e-05 | [−0.676, −0.324] |

**Path vs first_loss (registered question): no separation.** Directly paired on
the same 34 rows: 0.265 vs 0.235, n01=4 / n10=3, exact p = 1.0000, bootstrap
diff [−0.176, 0.118]. The hypothesis that path routing beats first-loss routing
is not supported at this sample size. The only arm that separates from the
other two is `agnostic` (0.529 vs 0.235/0.265; p = 0.0020 / 0.0117), and it
bundles formation write-through, wide retrieval and self-check — it is not a
targeted-stage effect, and the self-check second attempt is a confound.

**Power note on this run.** On the 34-row common subset the observed net flips
are 7 (first_loss), 8 (path) and 17 (agnostic), all with zero losses, so each
clears the pre-registered 6-flip threshold; the subset is still small and the
target composition differs (first_loss 31/34 formation; path 16 reasoning /
14 context / 4 retrieval). Do not quote these as paper-grade until
`aris-ablation-planner` + `aris-experiment-audit` have run.

The offline reanalysis below still stands: first-loss formation labels
over-attribute failures, and routing the same rows through a path check does
not recover more answers.

Code: `experiments/interventions.py` (routing + repairs) and
`experiments/run_interventions.py` (three arms: `first_loss`, `path`,
`agnostic`; paired McNemar + bootstrap). Definitions in `docs/PROTOCOL.md`;
tests in `tests/test_interventions.py`.

## Offline reanalysis of LongMemEval n=200 failures

Offline reanalysis of the n=200 real-memory failures changes the repair target:

- 61 rows are labelled `F1_FORMATION`, but in 35 of them every later stage —
  including the final context — already contains all gold evidence. Only 21 are
  context-limited and 5 rerank-limited.
- Path routing over all 66 attributable failures: reasoning 38, context 22,
  retrieval 6. Formation repair therefore cannot move the majority of answers
  that the first-loss protocol attributes to formation.

**Power caveat (pre-registered):** exact McNemar needs 6 net flips for p<0.05
with zero losses — 15.8 points on the 38-row reasoning subset, 9.1 on the
66-row attributable set, 3.0 on all 200. Do not claim a 5-point targeted effect
as significant on the subset; the full-set gate wording is in the roadmap.

## P2 intervention — LoCoMo n=200 complete 2026-10-21

`results/interventions_locomo_n200/`: 200 questions × 3 arms, `errors: 0`,
`progress.json` `status: completed` (resumed from 168/200 on 2026-10-21; the
last 32 questions took 942 s). Analysis by
`python -m experiments.analyze_interventions --interventions
results/interventions_locomo_n200/interventions.jsonl` → 
`results/analysis_interventions_locomo_n200.json`.

Per-arm paired semantic accuracy on each arm's own targeted subset:

| arm | paired n | baseline correct | repaired correct | gain | McNemar p |
|---|---|---|---|---|---|
| first_loss | 49 | 9 | 13 | +8.2 pts | 0.3877 |
| path | 49 | 9 | 12 | +6.1 pts | 0.5488 |
| agnostic | 46 | 7 | 21 | +30.4 pts | 0.0026 |

Common subset — 44 questions scored in all three arms:

| arm | baseline → repaired | gain | McNemar p | bootstrap CI (baseline − repaired) |
|---|---|---|---|---|
| first_loss | 7 → 12 /44 | +11.4 pts | 0.2266 | [−0.250, 0.023] |
| path | 7 → 11 /44 | +9.1 pts | 0.3438 | [−0.227, 0.045] |
| agnostic | 7 → 20 /44 | +29.5 pts | 0.0044 | [−0.477, −0.136] |

Pairwise on the 44-row common subset (repaired verdicts): first_loss 0.273 vs
path 0.250, n01=2 / n10=3, p=1.0000, CI [−0.068, 0.114]; first_loss vs agnostic
0.273 vs 0.455, p=0.0574; path vs agnostic 0.250 vs 0.455, p=0.0225.

**Reading.** Unlike LongMemEval, neither stage-targeted arm separates from the
fresh baseline on LoCoMo; only the composite `agnostic` arm does, and
path-vs-first_loss again shows nothing. Target composition explains part of
this: first_loss routes 39/56 to formation, while path routes 30/56 to
retrieval and 21/56 to context (LongMemEval path was mostly reasoning). On the
retrieval-heavy LoCoMo profile, widening retrieval alone recovers little.

**Instrument caveat (new 2026-10-21, audit item).** The intervention regenerates
the baseline answer instead of reusing the stored one. Among non-skipped
questions the fresh baseline flips stored-wrong→fresh-correct for 9 of 50
LoCoMo questions (agreement 0.821, exact McNemar p=0.0039) and 2 of 60
LongMemEval questions (agreement 0.967, p=0.5). Stored verdicts are all False
in this subset by construction, so kappa is degenerate and must not be quoted.
So ~18% of LoCoMo's attributable-failure set is not reproducible even with
temperature 0 — provider-side sampling or judge nondeterminism. All paired
numbers above use the fresh baseline, so they are internally fair, but the
failure-label base rate carries this measurement error and must be reported
with any intervention number.

**Power note.** On the 44-row common subset the net flips are +5 (first_loss),
+4 (path), +13 (agnostic); with 3–4 losses the exact test is far from the
zero-loss 6-flip threshold. Do not quote these as paper-grade until
`aris-ablation-planner` + `aris-experiment-audit` have run.

## P2 Phase-0 audit (2026-10-21, no new API calls)

`experiments/audit_interventions.py` → `results/audit_interventions_*_n200.json`.
It answers the reviewer's cheap questions before any new arm:

| readout | LongMemEval | LoCoMo |
|---|---|---|
| ITT gain first_loss / path / agnostic (pts of 200) | +6.0 / +4.5 / +10.5 | +2.0 / +1.5 / +7.0 |
| losses that land on stale labels | 0 / 0 / 0 (no losses) | 4/4, 4/4, 3/3 |
| deterministic-floor share of discordants | 5/12, 3/9, 11/21 | 3/13, 2/11, 6/20 |
| Holm-adjusted primary-family p | 0.0156 / 0.0156 / 4.6e-05 | 0.453 / 0.453 / 0.0133 |
| mean length delta, gained minus lost answers (chars) | −0.5 / −3.7 / −2.1 (no losses) | −0.5 vs +2.3 / +12.7 vs +2.3 / +14.9 vs +4.7 |

- **Every LoCoMo arm loss sits on a stale-label question** — the fresh baseline
  already answered it correctly. Repair harm on LoCoMo is measurement
  staleness, not a harmful repair.
- LongMemEval's three primary tests survive Holm. LoCoMo only `agnostic`
  survives; the targeted arms remain non-significant.
- Roughly 30–50% of flips are decided by deterministic floors, not the judge —
  a flip-provenance readout must accompany any F6 discussion.
- LoCoMo `agnostic`/`path` gains are longer answers than their losses
  (+12.7 / +14.9 chars): a judge length-bias confound to test with a sham arm.
- EVAL rows are never routed (`first_loss_target` returns None), so they are
  an unexposed group, not a usable negative control.
- ITT is much smaller than the subset headline: +10.5 pts on LongMemEval and
  +7.0 on LoCoMo for `agnostic`, from +50 / +29.5 on the common subsets.

## Ablation plan (2026-10-21)

Independent review (`kimi-k3`; the skill's Codex backend is unavailable on this
host) is saved in `docs/research/2026-10-21-ablation-review-kimi-k3.md`, with a
normalised, feasibility-checked plan in
`docs/research/2026-10-21-ablation-plan.md`.

Reviewer's verdict: C2 (path beats first_loss) is dead — `path_target` reads
gold and still ties. The two questions that decide the paper are (a) whether
`agnostic` is just self-check (A3), and (b) whether targeted repair beats
arbitrary repair (A5/A6). Measurement (judge validity, multiplicity, stale
labels) binds before any new arm.

## Next action — placebo gate (A1), then decomposition

1. Free Phase-0 analyses: **done** (above).
2. A1 placebo: a second identical fresh baseline on LoCoMo (and LongMemEval if
   budget allows). It bounds the nondeterminism/regression-to-the-mean floor.
   **Gate:** if placebo discordants are the same order as the arm effects,
   stop and fix measurement before A2–A6.
3. Then A2/A3/A4 (decompose `agnostic`), then A5/A6 (targeting thesis).
4. Human/frontier re-judge of all discordant pairs in the primary contrasts
   remains non-negotiable before any paper number.

## Open todos (in order)

1. Run the A1 placebo gate, then A2–A6 (see Next action). The ablation plan is
   frozen in `docs/research/2026-10-21-ablation-plan.md`; do not add arms
   after seeing results without recording the change as exploratory.
2. Judge-validity reporting for the n=200 runs: rerun
   `experiments/judge_reliability.py` on `longmemeval_n200` and
   `locomo_n200` with a second model. **Unblocked 2026-10-21:** the gateway's
   alternative models speak OpenAI-compatible only, and `evaluation/llm_api.py`
   now sends the required session header and user agent; pass
   `SEMANTIC_JUDGE_API_STYLE=openai` and a `/v1`-suffixed base URL. Prefer
   `kimi-k3` or `qwen3.8-max` over `deepseek-v4-pro` (same family as the
   answerer).
3. Confirm CIKM / COLING / ECIR / NLPCC deadlines. **Blocked 2026-10-20:** all
   web tools (WebSearch, WebFetch, MCP research) failed from this host; retry
   when network access exists.
4. Optional: remote embedding support. Note the audit: all current runs use the
   deterministic `hash:384` fallback, so a remote embedder would change the
   backend and require re-running every condition.

## Environment notes

- Answer/judge via `evaluation/llm_api.py`: `ANSWER_API_STYLE=anthropic`,
  opencode zen gateway, model `deepseek-v4.1-flash`. `x-opencode-session` header
  required; `Authorization: Bearer` causes HTTP 403. Thinking-only responses are
  retried (`LLM_API_RETRIES`, default 3); `max_tokens` must stay ≥4096 for
  reasoning models.
- `results/` is gitignored; each run's `run_metadata` records commit, dataset
  sha256, model and dirty flag, so runs are reconstructable.

Default is local Ollama. To run against a remote gateway instead (answer and/or
judge), use the switchable backend in `evaluation/llm_api.py`:

```bash
# any Anthropic-Messages-compatible gateway (e.g. opencode zen)
ANSWER_API_STYLE=anthropic ANSWER_BASE_URL=https://... ANSWER_API_KEY=...
# or any OpenAI-compatible provider
ANSWER_API_STYLE=openai   ANSWER_BASE_URL=https://... ANSWER_API_KEY=...
# judge can be routed separately:
SEMANTIC_JUDGE_API_STYLE / SEMANTIC_JUDGE_BASE_URL / SEMANTIC_JUDGE_MODEL / SEMANTIC_JUDGE_API_KEY
```

Never commit the key; keep it in `.env.local` (gitignored). **Embedding backend
(2026-10-20 correction):** the code default is `qwen3-embedding:4b`, which is not
installed; every run since 2026-10-10 therefore used the deterministic 384-dim
hash fallback, including the canonical n=50 and n=200 runs. Ollama is not
contacted at all during those runs, so the runner needs ~100 MB, not an
embedding model. `run_metadata.embedding` now records the probed backend and the
run log warns on fallback. Do not switch backends mid-study: comparisons are
only valid within one backend.

```bash
G:/aconda/python.exe -m experiments.run_oracle_experiments \
  --dataset locomo_refined_public --limit 50 \
  --out-dir results/oracle_experiments_locomo
```

After that: freeze the protocol, update `docs/PROTOCOL.md` with the refutation
layer, and only then consider any F6 number paper-usable.
