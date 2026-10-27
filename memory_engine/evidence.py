from __future__ import annotations

from collections import OrderedDict


class EvidenceBuilder:
    def build(self, candidates, top_k, type_cap=3):
        """
        Evidence completeness：
        同一事实的 raw + structured evidence 不重复刷屏；
        优先保留不同 memory_type 的互补证据。

        ``type_cap`` is the intervention control: the baseline context keeps at
        most 3 items of one memory type, while a context repair raises it.
        """
        selected = []
        seen_content = set()
        type_count = {}

        # 第一轮：保证证据类型多样性
        for item in candidates:
            content = item["content"].strip()
            if not content or content in seen_content:
                continue
            mt = item.get("memory_type","raw")
            if type_count.get(mt,0) >= type_cap:
                continue
            selected.append(item)
            seen_content.add(content)
            type_count[mt] = type_count.get(mt,0) + 1
            if len(selected) >= top_k:
                break

        return selected
