# Round 5 pilot v2 — review2 记录

产出：`round5_stage_pilot_v2_review2.csv`（40 行，只填 `annotated_first_loss_stage` / `confidence` / `notes`）。
源文件 `round5_stage_pilot_v2.csv` 未改动：465989 B，md5 `eb5e6dc0…`，填入三列后其余内容逐字节一致；未打开 `round5_stage_pilot_v2_key.csv`。

## 本轮实际执行的规则（对应新版 README_round5.md）

1. **标签集**：`formation | storage | retrieval | rerank | context | none | E0 | uncertain`，`evolution` 已在 v2 中排除（B 为 `NOT MEASURED`，A 为常量片段），未产生该标签。
2. **formation / storage**：按 README 的 operational rule——只要 gold 句子在两视图（session 顺序前 10、gold 重叠前 10）中出现就判"在"。判据用最长公共子串 lcs：lcs ≥ 40 视为"该记忆项在"（预览按 205 字符截断，所以 lcs≈195 即整条 gold 被截断显示）。
3. **retrieval / rerank / context**：v2 给的是完整 top-20 / top-10 / top-N，因此"不在表里"即"该阶段没有"；判据是**参考答案能否从该阶段条目推出**（允许换词，但要求答案的区分性内容在，例如 q012 必须有 "Sweden" 而不只是 "home country"）。
4. 顺序取**第一个**缺失阶段（与 `first_missing_stage` 一致），后阶段重新出现不改标签，但写进 notes（q019-A）。
5. **E0** 用 `gold_evidence_dates` 解相对时间；本轮只有 q002、q005 判 E0。

## E0 两题

- `q002`（Melanie 何时画日出 → 2022）：gold 是 "take a look at this"（D1, 8 May 2023；配图 caption 为 "a painting of a sunset over a lake"），没有年份；2022 只能来自 D1:14 "I painted that lake sunrise last year"，不在 gold 里。
- `q005`（Caroline 身份 → Transgender woman）：gold 只说"跨性别故事很激励我"，配图是狗/墙面涂鸦，没有陈述其身份。

其余 9 个 `when` 题都靠 `gold_evidence_dates` 解出（D1=8 May、D2=25 May、D3=9 Jun、D5=3 Jul、D6=6 Jul），不再因缺日期判 E0。

## 一个需要你决策的判据冲突（影响 A 组 2 行）

`q003-A`、`q004-A`：gold 句子在两视图里都不出现，但视图里有**语义等价的改写**——

- q003-A 视图说 "I struggled with mental health … started looking into counselling and mental health career options"；
- q004-A 视图说 "I took the first step towards becoming a mom - I applied to adoption agencies!"。

按 README 写的 operational rule（gold 不出现即视为缺失）我判了 `formation`；若按"内容是否还在"判则应判 `retrieval`（q003-A 甚至可能是 `none`）。这两行是 v1→v2 我把标签从 `none`/`retrieval` 改成 `formation` 的唯一原因。**建议 README 明确一句：改写是否算"appear"。** 我在 notes 里都写明了，便于裁决。

## 分布（review2）

| 标签 | A | B | 合计 |
|---|---|---|---|
| none | 3 | 5 | 8 |
| formation | 8 | 0 | 8 |
| retrieval | 6 | 11 | 17 |
| rerank | 1 | 2 | 3 |
| E0 | 2 | 2 | 4 |

`storage` / `context` / `uncertain` 仍为 0（v2 的完整列表让"storage 才丢"与"context 才丢"基本不可能出现；`rerank` 现在可判了）。

## 与 v1 的对照（同一标注者，34/40 相同）

v2 的完整列表带来 6 处变化，全部可解释：

- `q006-B`、`q018-B`、`q019-A`：`retrieval` → `rerank`——gold 在 **top-20 的第 13/16/18 位**，v1 只给前 5 条所以看不到，v2 显示它进了候选池但被 top-10 重排切掉。
- `q003-B`：`retrieval` → `none`——top-20 里能看到 "…help others with their mental health" 与 "…pursue counseling"，答案两个分支都在。
- `q003-A`、`q004-A`：`none`/`retrieval` → `formation`——见上面的 operational rule。

A 组集中于 `formation`（8/20：抽取成 fact 时丢了，原文仍可从 storage 取回），B 组集中于 `retrieval`/`rerank`（11+2，候选池全是寒暄）。这正好是"同准确率、不同失效阶段"想测的信号，但只有 5 个非空类，报告 kappa 时建议同时给"实际使用类"的版本。

## 两标注者一致性（v2，与 `round5_stage_pilot_v2_review1.csv` 对照）

| 范围 | n | 一致率 | Cohen's κ |
|---|---|---|---|
| 全部 40 行，8 类 | 40 | 37/40 = 0.925 | **0.897**（过 0.70 门槛） |
| 去掉 4 个 E0 行 | 36 | 33/36 = 0.917 | 0.877 |

两边都只用到 5 类（E0 / formation / none / rerank / retrieval）。只有 3 处分歧：

- `q003-B`：review1 `retrieval` vs review2 `none`——top-20 里只剩 "…help others with their mental health" / "…pursue counseling" 这类**追问句**，算不算"证据在"是判据边界。
- `q008-A`：review1 `formation` vs review2 `retrieval`——formation 的 gold 视图里有 "tough breakup" 那一轮（lcs 200），我判"在"（它能推出 single），review1 认为不足以支撑 relationship status。
- `q014-A`：review1 `formation` vs review2 `retrieval`——formation 里有 "working with trans people …" 整轮（lcs 200），分歧在 storage 视图是否把第 2 条 gold 也算上。

三处都属于"部分支持算不算支持"的判据问题，建议在 README 里各加一句（①追问句里的预设算不算证据；②多单元 gold 是"全部单元"还是"能推出答案即可"）。

