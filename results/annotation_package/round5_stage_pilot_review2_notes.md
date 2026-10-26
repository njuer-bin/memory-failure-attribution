# Round 5 pilot — 审阅轮 2（review2）记录

产出：`round5_stage_pilot_review2.csv`（40 行，仅填写 `annotated_first_loss_stage` / `confidence` / `notes`）。
`round5_stage_pilot.csv` 与 `round5_stage_pilot_key.csv` 均未改动（未打开 key）。

> 命名说明：本轮最初写入的是 `round5_stage_pilot_review1.csv`，但该文件随后被另一份标注覆盖（197545 B，含 13 个 `evolution` 标签，与本表内容不同）。为避免继续互相覆盖，本表改用 `review2`；`review1` 保持原样未动。

## 判定规则（实际执行）

1. 先判 **E0**：gold evidence 的文本（加上它所在会话的日期锚点）能否推出 reference answer；不能则 `E0`。
2. 再按生命周期顺序扫描 `formation → storage → evolution → retrieval → rerank → context`，取**第一个**不再含有“回答所需证据”的阶段。判“含有”允许改写/换词；答案是多选一（A 或 B）时，命中一支即算含。
3. **`evolution` 不作为失证阶段**：B 系统该阶段构造上为空（`VerbatimSystem.stages()` 返回 `evolution: []`，`stage_dict` 里 `measured=False`），A 系统该列是**常量**（20 行全是 `[1] I use for self-expression and peace`，39 字符）。按 `evaluation/attribution.py` 的 `_stage_measured`，该阶段本就不参与归因，故不判 `evolution`，也不据它判 `uncertain`。
4. 同一行里“后面阶段又出现”不改变标签（README 要求的是**第一个**缺失阶段，与 `first_missing_stage` 语义一致）；这类行在 `notes` 里写明“后来在 context/第 N 项又出现”。
5. `none` 表示六个阶段（不含未测量的 evolution）都仍含所需证据。

## 输入数据的两处结构性问题（建议在正式 100 题前修掉）

- `evolution_preview` 无信息量：A 侧 20/20 相同常量片段，B 侧 20/20 为空。该列无法支持任何逐行判断 → 本表一律不判 `evolution`。
- `retrieval / rerank / context` 只给前 5 条；B 系统（`VerbatimSystem`）的 retrieval=top20、rerank=context=top10，所以三列预览在 B 上完全逐字相同（`retrieval==rerank==context`）。因此 B 组不可能产生 `rerank`/`context` 标签，且“证据不在前 5”不等于“不在 top10/20”（已在 `confidence` 与 `notes` 里标注）。

## E0 的两行（同一问题，A/B 都判 E0）

- `q002`（Melanie 何时画日出，答 2022）：gold 是 “take a look at this”，配图 caption 为 “a painting of a sunset over a lake”，没有年份；2022 只来自下一句 D1:14 “I painted that lake sunrise last year”。所列证据推不出答案。
- `q005`（Caroline 的身份，答 Transgender woman）：gold “The transgender stories were so inspiring!” 配图是狗/墙面涂鸦，证据只说明她被跨性别故事打动，没有陈述她的身份；身份要靠 D3:1 等后续轮次。

## 关于“when”类问题的日期（未据此判 E0）

本批 20 题里 9 题是 `when`，答案需要会话日期 + 相对时间（“yesterday / last week / next month / this month”）。CSV 的 `gold_evidence` 只有文本、没有 session 日期，但记忆项本身带时间戳（`session_date_time`，如 D1 = 8 May 2023 → 7 May 2023）。因此按“证据项自带时间戳”处理，不判 E0；否则 9 行会因导出缺列而集体变 E0，pilot 失去意义。若要排除歧义，建议在 CSV 里补 `gold_evidence_dates` 列。

## 分布（review1）

| 标签 | A | B | 合计 |
|---|---|---|---|
| none | 4 | 4 | 8 |
| formation | 6 | 0 | 6 |
| retrieval | 8 | 14 | 22 |
| E0 | 2 | 2 | 4 |

只用到了 4 个类别（`storage` / `rerank` / `context` / `uncertain` 均为 0）。A 组的 `formation` 集中在“gold 在被抽取成 fact 时丢了、但原文仍在 storage/context”的情形；B 组的 `retrieval` 集中在“原始轮次仍在库里，但向量检索前 5 全是寒暄/泛化追问”。

## 对 pilot 可达性的提醒

- 若第二标注者同样按“第一个缺失阶段”判，A 组的分歧热点预计在 `formation` vs `retrieval`（取决于是否认为 `formation` 预览（按 gold 词面重叠取 top5）足以代表该阶段）。这是任务形状问题，不是标注者问题：建议正式轮把 `formation` 的取法从“gold 词面 top5”改成“按会话顺序全量/固定配额”，或明确写“预览缺失即视为该阶段缺失”。
- `evolution` 列必须在正式轮修好或从 9 分类里去掉，否则该类恒为 0。
- 现在只有 4 个非空类，k=9 的 kappa 会被大量空类稀释；建议报告时同时给出仅在前述 4 类上的 kappa。
