# Phase 0 Audit Record: LoCoMo Data and Five-Question Pilot

> **Status:** Data audit complete for schema/count/license; five-question annotation dry run prepared, not yet human-annotated.
> **Date:** 2026-11-08

## 1. Official source inspected

- Repository: https://github.com/snap-research/locomo
- Data: data/locomo10.json
- README: https://github.com/snap-research/locomo/blob/main/README.MD
- License: https://github.com/snap-research/locomo/blob/main/LICENSE.txt
- Evaluation implementation: https://github.com/snap-research/locomo/blob/main/task_eval/evaluation.py

The public data file was parsed directly from the official repository. No raw dataset file was copied into this repository.

## 2. Verified dataset facts

- 10 public conversations.
- 1,986 QA records total.
- Each conversation has session arrays; each turn has a dia_id, speaker, and text.
- QA evidence is a list of turn IDs such as D3:13.
- The official README describes evidence IDs as the dialogue turns containing the answer, when available.
- The data file contains category IDs 1–5.
- The official evaluation code treats category 1 as multi-hop and computes partial/sub-answer F1 for it. Categories 2, 3, and 4 are evaluated without multi-hop sub-answer splitting; category 5 is adversarial.

### Category counts parsed from the official JSON

| JSON category | Interpretation | Count |
|---:|---|---:|
| 1 | Multi-hop | 282 |
| 2 | Temporal | 321 |
| 3 | Open-domain | 96 |
| 4 | Single-hop | 841 |
| 5 | Adversarial | 446 |
| **Total** | | **1,986** |

**Critical warning:** Do not assume category 3 means multi-hop. In the JSON, category 1 is multi-hop. This was cross-checked against the official task_eval/evaluation.py branch that uses multi-hop sub-answer scoring for category 1.

## 3. License and data-handling decision

The official repository's LICENSE.txt is Creative Commons Attribution-NonCommercial 4.0 International (CC BY-NC 4.0).

Operational rules:
- Do not commit the raw locomo10.json file.
- Do not bulk-copy conversation text into this repository.
- Keep question IDs, source turn IDs, and derived annotations only after checking whether the proposed redistribution is permitted.
- Cite Maharana et al. and the official dataset repository in any paper or release.
- Re-check license conditions before releasing transformed annotations or derived data.

## 4. Five-question dry-run sample

Selection criteria:
- JSON category 1 (multi-hop);
- at least two evidence turn IDs;
- five different conversations to avoid a single-conversation-only pilot;
- examples chosen to expose different evidence patterns and possible annotation failures.

The qa_index is zero-based within the corresponding conversation's qa array.

| Conversation | QA index | Question (short identifier) | Reference answer | Evidence turn IDs | Audit note |
|---|---:|---|---|---|---|
| conv-26 | 11 | Where did Caroline move from 4 years ago? | Sweden | D3:13, D4:3 | Candidate relation/identity bridge: one turn says she moved from her home country; another identifies that country. |
| conv-41 | 3 | What type of volunteering have John and Maria both done? | Volunteering at a homeless shelter | D3:5, D2:1 | Two speakers' evidence must be combined to establish the shared activity. |
| conv-42 | 11 | What is Joanna allergic to? | Most reptiles, animals with fur, cockroaches, dairy | D4:4, D5:11, D2:23 | Potential gold-evidence mismatch: the cited dairy turn says she cannot have dairy, which may not establish an allergy. Must not assume intolerance and allergy are equivalent. |
| conv-43 | 1 | What are John's goals for his career that are not related to his basketball skills? | Get endorsements, build his brand, do charity work | D6:15, D11:17 | Multiple answer slots across turns; check whether all slots are directly supported and whether one item is redundant. |
| conv-44 | 12 | What outdoor activities has Andrew done other than hiking in nature? | Rock climbing, fishing, camping | D8:1, D17:1, D14:1 | Three distinct activity facts; likely a multi-item aggregation rather than a single bridge chain. |

This sample is a **dry run**, not a final gold annotation set. The table intentionally includes a likely evidence-sufficiency problem so the annotation protocol is tested against benchmark imperfections.

## 5. Why this sample is useful—and what it cannot show

The five examples cover:
- entity/temporal relation resolution;
- cross-speaker evidence integration;
- answer-slot aggregation;
- possible evidence/reference mismatch;
- direct evidence from several sessions.

The set may contain few or no clean Bridge items. If that happens, do not treat it as evidence that Bridge does not exist in LoCoMo. Expand the candidate pool using a predeclared selection procedure, then annotate the next batch. Do not cherry-pick only examples that support the hypothesis.

Five examples are insufficient for:
- estimating prevalence of role types;
- statistical hypothesis testing;
- stable inter-annotator reliability;
- estimating the role-by-necessity interaction;
- making a paper-level claim.

## 6. Immediate next step

Use docs/ANNOTATION_GUIDELINES.md to independently annotate these five records. Compare role and necessity labels separately, inspect the evidence-sufficiency flag, and revise the codebook before selecting the 30–50-question pilot.


## 7. Local annotation packet generation

A helper script is available at experiments/prepare_locomo_annotation_packet.py.

Example (run from repository root):

~~~bash
python experiments/prepare_locomo_annotation_packet.py ^
  --dataset path/to/locomo10.json
~~~

On PowerShell, the command may be written on one line:

~~~powershell
python experiments/prepare_locomo_annotation_packet.py --dataset .\data\locomo10.json
~~~

The default output is written to the current user's home directory as locomo_pilot_annotation_packet.jsonl, not into the repository. The packet contains the selected raw dialogue excerpts, so it is subject to LoCoMo's CC BY-NC 4.0 terms. Keep the generated packet local and do not commit it.

The script checks:
- conversation ID and zero-based QA index;
- category ID equals 1 (multi-hop);
- question and reference answer match the pinned manifest;
- evidence turn IDs match the official QA record;
- every evidence turn ID resolves to a dialogue turn.

If any check fails, the script stops rather than silently constructing a mismatched annotation packet.
