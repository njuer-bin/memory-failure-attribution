# 裁决表填写说明（2026-11-20）

文件：`adjudication_sheet.csv`

两名批注者的表格都已交回，`check` 已生成此表。当前只有 **125 个存在实质分歧的条目**，没有分歧的条目不在这里。

## 只填这些列

1. 看 `disputed_fields`，它列出本条需要裁决的字段，例如
   `primary_judgment;evidence_support`。
2. 只填对应的 `adj_<field>`，例如 `adj_primary_judgment`、
   `adj_evidence_support`。
3. `A_*` 和 `B_*` 是原始记录，**不要修改**；`item_id` 和文本列也不要改。
4. 每条填 `adjudicator`（裁决人标识）和 `rule`（一句依据，如“T3 明确确认，采 A”）。
5. 不在 `disputed_fields` 里的字段不用填；填了也会被忽略。

## 不参与裁决的列

- `rationale`、`turn_references` 是自由文本，不作为分歧裁决；合并时保留 RA 的
  rationale，RB 的原文仍在 `B_rationale` 中。
- `confidence` 不要求裁决；合并时取两人中较低的一档（LOW < MEDIUM < HIGH）。

## 必须先修的一个值

`REPR-0206` 的 RA 行：`action_status = NOT_PURSUING`，但
`primary_dimension = ACTION`。校验器不允许 ACTION 维度使用该值。请二选一：

- 若主维度应为 `ACTION`，把 `action_status` 改为 `NOT_APPLICABLE`；
- 若应表达“未继续”的意图，把 `primary_dimension` 改为 `INTENTIONAL`。

修改后会改变该条的分歧情况，请重新运行 check 生成新表后再裁决。

## 生成/合并命令

```bash
python -m experiments.reannotation_round check \
  --a results/status_drift_v3_replication_writer/reannotation_2026-11-20/annotator_RA.csv \
  --b results/status_drift_v3_replication_writer/reannotation_2026-11-20/annotator_RB.csv

# 人工填完 adjudication_sheet.csv 后
python -m experiments.reannotation_round merge \
  --sheet results/status_drift_v3_replication_writer/reannotation_2026-11-20/adjudication_sheet.csv

python -m experiments.reannotation_round summarize
```

`merge` 会拒绝任何仍未填 `adj_*` 或缺少 `adjudicator` 的分歧项，不会自动替裁决人选择。
