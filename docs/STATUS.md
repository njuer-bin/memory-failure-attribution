# Status — where to resume

Last updated: 2026-10-19 (end of the judge-reliability and ordering-refutation session).

This is the single resume point. History and reasoning live in
`docs/RESEARCH_LOG.md`; definitions live in `docs/PROTOCOL.md`.

## Repo state

- Branch: `fix/formation-diagnostics-evidence-based`
- The 2026-10-18 audit repairs and the 2026-10-19 ordering-refutation layer are
  committed on this branch; nothing left uncommitted (verify with `git status`).
- `python -m pytest tests/` → 123 passed (verified 2026-10-19).

## Result artifacts

| path | valid? |
|---|---|
| `results/oracle_experiments_n50_final/` | **yes — canonical n=50 run** (`resumed_records: 0`, `errors: 0`) |
| `.../judge_reliability_self.json` | yes — same-judge self-consistency (kappa 1.0, 0 flips) |
| `.../judge_reliability_gemma3.json` | yes — cross-model estimate (raw_judge agreement 0.71, kappa ≈ 0.03) |
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

## Next action — LoCoMo cross-benchmark run

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

Never commit the key; export it in the shell. With a remote backend the host
keeps only the embedding model (bge-m3, ~0.7 GB) resident.

```bash
G:/aconda/python.exe -m experiments.run_oracle_experiments \
  --dataset locomo_refined_public --limit 50 \
  --out-dir results/oracle_experiments_locomo
```

After that: freeze the protocol, update `docs/PROTOCOL.md` with the refutation
layer, and only then consider any F6 number paper-usable.
