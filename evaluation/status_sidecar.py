"""Parse structured status sidecars from compressed memories.

Sidecar format produced by the `sidecar` writer style:

    [状态: 确定性=已确认|可能|不适用；意图=已决定|考虑中|不适用；条件=已满足|未满足|不适用]
"""
from __future__ import annotations

import re

FIELD_BY_DIMENSION = {
    "epistemic": "确定性",
    "intentional": "意图",
    "conditional": "条件",
}

LABELS = {
    "epistemic": {"已确认": "CERTAIN", "可能": "POSSIBLE"},
    "intentional": {"已决定": "COMMITTED", "考虑中": "CONSIDERING"},
    "conditional": {"已满足": "CONDITION_SATISFIED", "未满足": "CONDITION_ACTIVE"},
}

_SIDECAR_RE = re.compile(r"\[\s*状态\s*[:：]\s*(.*?)\]", flags=re.S)
_PAIR_SPLIT_RE = re.compile(r"[；;]")
_KV_SPLIT_RE = re.compile(r"[=:：]")


def parse_sidecar(text: str) -> dict[str, str] | None:
    matches = _SIDECAR_RE.findall(text)
    if not matches:
        return None
    # Recursive memories may accumulate sidecars; the last one is the latest.
    payload = matches[-1]
    fields: dict[str, str] = {}
    for part in _PAIR_SPLIT_RE.split(payload):
        part = part.strip()
        if not part:
            continue
        kv = _KV_SPLIT_RE.split(part, maxsplit=1)
        if len(kv) != 2:
            continue
        key, value = kv[0].strip(), kv[1].strip()
        if key:
            fields[key] = value
    return fields


def sidecar_present(text: str) -> bool:
    return parse_sidecar(text) is not None


def sidecar_status(text: str, dimension: str) -> str | None:
    fields = parse_sidecar(text)
    if not fields:
        return None
    field = FIELD_BY_DIMENSION.get(dimension)
    if field is None:
        return None
    value = fields.get(field)
    if value is None:
        return None
    return LABELS[dimension].get(value)
