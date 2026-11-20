# 人工裁决说明（n = 30 重批）

本轮是 **两名独立人工批注 + 第三人工裁决**。第一版裁决由 `ADJ-AI` 完成，已整体归档到
`_ADJ-AI/`，不作为人类裁决使用。现在需要人工重新填写 `adjudication_sheet.csv`。

## 只填分歧字段

- 表内是 125 个存在实质分歧的条目；`disputed_fields` 列出每条要裁决的字段。
- 只填对应的 `adj_<field>`，例如 `adj_primary_dimension`、`adj_primary_judgment`。
- `A_*`、`B_*`、`item_id`、文本列都不可修改。
- 每条填写 `adjudicator`（你的标识）和 `rule`（一句依据，注明轮次或原话）。
- `rationale`、`turn_references` 不裁决；`confidence` 取两人较低一档。

## 裁决顺序

1. **先定主维度**：看对话更新轮在谈什么（真假/确定、意图、条件、执行）。
2. **再定状态是否被表达**：只有明确状态词才算 YES。
3. **再定具体状态**：必须与主维度匹配。
4. **最后按指南 F 节顺序得主判断**：ambiguous → proposition loss → legitimate update →
   unsupported distortion → omission → no distortion。

## 本轮重点检查的两类边界

### 1. EPISTEMIC 维度下，“考虑/打算”不是 epistemic 状态词

指南把 `考虑` / `打算` 列为 INTENTIONAL 的 `CONSIDERING` 线索；EPISTEMIC 的
POSSIBLE 线索是 `可能` / `不能确定`。如果记忆只写“考虑开始健身”，而对话 T3 说
“仍然只是可能、尚未确认”，需要先判断主维度：

- 若主维度是 EPISTEMIC：记忆没有 epistemic 状态词，应考虑
  `status_expressed = NO`、`expressed_status = NOT_EXPRESSED`，主判断按 F 节处理；
  不能仅因“考虑”语气不确定就填 `POSSIBLE`。
- 若主维度是 INTENTIONAL：`CONSIDERING` 是合法状态，再判断它是否被对话支持。

以下 18 条属于该边界，请重点核对维度与状态，而不是直接沿用任一方：

```
REPR-0003 REPR-0011 REPR-0022 REPR-0029 REPR-0030 REPR-0038
REPR-0063 REPR-0066 REPR-0086 REPR-0087 REPR-0089 REPR-0090
REPR-0127 REPR-0128 REPR-0130 REPR-0169 REPR-0171 REPR-0172
```

### 2. 主判断分歧集中在这些条目

两人的 `primary_judgment` 在这 30 条不同，裁决时必须逐条读对话，不要按某一方整体处理：

```
REPR-0002 REPR-0004 REPR-0005 REPR-0009 REPR-0012 REPR-0031
REPR-0039 REPR-0040 REPR-0044 REPR-0052 REPR-0055 REPR-0057
REPR-0080 REPR-0084 REPR-0102 REPR-0107 REPR-0108 REPR-0113
REPR-0114 REPR-0116 REPR-0118 REPR-0150 REPR-0155 REPR-0156
REPR-0158 REPR-0191 REPR-0192 REPR-0197 REPR-0200 REPR-0202
```

## 完成后

```bash
python -m experiments.reannotation_round merge \
  --sheet results/status_drift_v3_replication_writer/reannotation_2026-11-20/adjudication_sheet.csv
python -m experiments.reannotation_round summarize
```

`merge` 会拒绝任何缺 `adj_*` 或 `adjudicator` 的分歧项，并把裁决人计数写入
`merge_report.json`；如果裁决人标识看起来是机器（含 AI/model 等），会打印警告。
