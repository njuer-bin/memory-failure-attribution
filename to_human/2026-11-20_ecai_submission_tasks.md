# Outstanding human-only tasks — ECAI 2027 (2026-11-20)

The ECAI 7+1-page port is built (`paper/submission_ecai/`), and the figures and
supplementary archive are resynced to include the glm-5.3-flash v3.1 matrix.
Everything below needs a person. Items 1–3 and 5 were completed on 2026-11-20;
item 4 remains before submission (~April 2027).

## 1. Validate the 16 new authorized controls — DONE (2026-11-20)

WMY (A) and YTB (B) completed `validation_A_16.csv` / `validation_B_16.csv`
independently. Pooled over 16: realism 4.97, status clarity 5.00, rule clarity
4.97, distortion plausibility 4.31, stake severity 2.88;
`only_status_differs` yes-both 0.9375 (kappa 1.000); `HEA-11` excluded, 15
survivors. Acceptance (realism ≥ 3.5, yes-both ≥ 0.90) passes.
`request_check.csv` is 54/54 `manipulation_ok=yes` with notes. Provenance is in
`validation_16_provenance_A.json` / `_B.json`.

## 2. Independent second rater for the reason coding — DONE (2026-11-20)

Sheet: `results/status_drift_v3_p4_2_v3_v31/analysis/reason_sheet_blind.csv`
(39 rows) is complete (D1 34, O2 5). Agreement with `analyst_code` is raw 1.000,
kappa 1.000; `unauthorized_reason_codes.csv` now carries `rater_b_code` /
`rater_b_note`. Record the rater's identity and independence in
`unauthorized_reason_codes_summary.json` before citing this as human.

## 3. Annotate the remaining 18 writer-replication trajectories — DONE (2026-11-20)

Directory: `results/status_drift_v3_replication_writer/annotation_v325_remaining/`
(126 items, ids `REPR-0085`–`REPR-0210`). `annotator_A.csv` and
`annotator_B.csv` are complete (126/126, schema-clean). The 50 A/B
disagreements were adjudicated by
`claude-sonnet-4.6 (model third-reviewer simulation; NOT human)`; all 50
resolved to A. Report n = 12 (pre-registered) and n = 30 (post-hoc
sensitivity, model-adjudicated) separately.

## 4. Swap in the official ECAI 2027 class when released

`paper/submission_ecai/ecai.cls` is a local stand-in reproducing the ECAI
geometry. When the official kit appears: replace `ecai.cls`/`.bst`, recompile
`main.tex` and `appendix.tex`, and re-check the page count (the official class
may use 10 pt and grow the body) and the PDF metadata. Only the front matter
(`\title`, `\author`, abstract) should need touching.

## 5. Final read-through against the frozen state — DONE (2026-11-20)

`paper/V3_NUMBERS.md` now carries §12b for the n = 30 cohort, and the ECAI
main text, ECAI appendix (`tab:repl30`), ACL source, and `V3_PAPER_DRAFT.md`
report it as a post-hoc, model-adjudicated sensitivity analysis alongside the
pre-registered n = 12 cohort. The reason-rater provenance is recorded in
`unauthorized_reason_codes_summary.json` as unrecorded / not an independent
human rating. PDFs were rebuilt: ECAI `main.pdf` 6 pages and `appendix.pdf`
4 pages (0 overfull, 0 unresolved); ACL `main.pdf` 12 pages with the body ending
on page 8. `paper/supplementary.zip` was rebuilt (53 files).

Only item 4 (swap in the official ECAI class when released) remains.

## 6. Optional: a real human third rater for the 50 n=30 disagreements

The 50 A/B disagreements in the n=30 cohort were resolved by a model
third-reviewer, not a human. If a qualified third annotator is available
before submission:

- Freeze and hash the items, annotation guide, A/B sheets, and the existing
  model adjudication output.
- Give the adjudicator the item and the guide only, with A/B labels, the model
  decision, condition summaries, and the expected direction hidden.
- Collect the independent third label before any discussion, then document a
  resolution step for whatever still disagrees.
- Keep A/B, third-rater, model-adjudicated, and final labels in separate
  fields; do not overwrite the current adjudication file.

If this is not done, the paper keeps the current wording: model-assisted
adjudication, n = 30 post-hoc sensitivity, not independent human confirmation.
The 210-item reconciliation (`analysis_v325_full/reconciliation.json`) shows
every condition has 30 items and the five categories partition each condition;
the rewrite-matched row sums to 30 only when its two ambiguous items are kept,
so that column must stay in the table.

## Status after v2.1 (2026-11-20)

Done locally: three-layer control audit, stratified n=30 reliability, canonical
results layer with consistency checks, novelty-audit extension, GLM Study 2b
sync into the ACL manuscript, fig5 legend repair, both PDF rebuilds, supplement
rebuild, and anonymity scans. Remaining human inputs are unchanged: an optional
independent third annotator for the n=30 disputes, and the official ECAI 2027
class/kit when it is released. No thresholds, labels, or denominators were
changed.

## n=30 全量重批（已冻结，等待人工）

目录：`results/status_drift_v3_replication_writer/reannotation_2026-11-20/`

- 两名独立批注者分别使用 `annotator_RA.csv`、`annotator_RB.csv`（行序不同，均无 condition/gold/旧标签）。`key.csv` 只给协调者，已加入 gitignore。
- 两人独立完成、交回前不讨论；第三人用 `adjudication_sheet.csv` 只裁决分歧字段，并填写 `adjudicator` 与 `rule`。
- 流程：`python -m experiments.reannotation_round check --a ... --b ...` → 人工填写 → `merge --sheet ...` → `summarize`。
- 旧标签保留；在 merge 完成前，论文继续使用现行 n=30 弱支持表述，不提前替换数字。

## n=30 人工重裁决（当前待办）

第一轮 125 条分歧由 `ADJ-AI` 填写并合并，已归档到
`results/status_drift_v3_replication_writer/reannotation_2026-11-20/_ADJ-AI/`，
不得作为人类裁决使用。当前 `adjudication_sheet.csv` 已重置为空白，等待人工裁决。

重点：先定主维度；EPISTEMIC 下“考虑/打算”不是 POSSIBLE 的线索。需重点核对的
18 条边界项和 30 条主判断分歧项列在 `ADJUDICATION_GUIDE.md`。分工须保持两名原批注者
互不看表，裁决人不参考旧标签或 `_ADJ-AI/`。
