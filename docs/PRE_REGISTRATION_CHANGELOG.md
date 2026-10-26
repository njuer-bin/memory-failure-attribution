# Pre-registration changelog

Append-only. Any change to a frozen item in `docs/PROTOCOL_FREEZE.md`, any change
to an analysis plan after seeing its outcome, or any re-scoping of a claim must
be recorded here **before** the affected run or analysis. Each entry states what
changed, why, and which analyses it invalidates or re-labels.

## Template

```
## YYYY-MM-DD — <short title>
- Item: <frozen item or plan>
- Old: <what was pre-registered>
- New: <what it becomes>
- Reason: <why, stated before seeing the outcome where applicable>
- Affected analyses: <artifact paths, label versions>
- Decision impact: <none / re-label / invalidate / re-scope>
```

## Entries

## 2026-10-26 — Adopt the CCF-B decision plan and freeze the protocol
- Item: governing plan and frozen configuration.
- Old: phase plan in `docs/PUBLICATION_ROADMAP.md`; no formal freeze.
- New: `docs/CCF_B_DECISION_PLAN_2026-10-26.md` is the governing plan;
  `docs/PROTOCOL_FREEZE.md` freezes commit `b8b1f6e`, model config, datasets,
  evaluation and annotation protocols, and headline artifacts.
- Reason: adversarial review (`docs/reviews/2026-10-26-direction-kill-argument.md`)
  found the current framing not CCF-B viable as-is; the plan replaces
  paper-polishing with falsifiable decision gates.
- Affected analyses: all headline numbers must now state their label version
  (auto / abstention-corrected / human-gated); E0 levels are not quoted.
- Decision impact: none on stored results; re-scope of claims pending gates A–D.
