# V3 P4 Freeze Record (2026-11-17)

**Decision:** freeze the P4 downstream behavioral intervention before
confirmatory generation. All defaults approved by the maintainer.

## Frozen artifacts (SHA-256)

| SHA-256 | File |
|---|---|
| `a5271b0acb6e8c27dcd9eb74e345aaf38831fc14a66d54c31de4a218c2fbd534` | `docs/research/V3_P4_PROTOCOL.md` |
| `36ec772b6608d4a27c84334f71b39d7ae8af4e287d00652244debe2dda94fda2` | `experiments/v3_p4_behavioral.py` |
| `6e7fe4307dd27cc07ce205c263ab9534805cf9c51784f256c4e93532793f219b` | `docs/research/V3_ANNOTATION_GUIDELINES.md` (v3.2.3) |
| `ff26e30ee4441c0f40a51e9cf04834d055c2d76c20c50534d458d65b6449abcb` | `docs/research/V3_FORMAL_DEFINITIONS.md` (v3.2.3) |

Base commit: `6843a46fc40f1f69ca4a7b26f06415166ac49ca3`.

## Design

- 30 P2 trajectories; each under `present`, `omitted`, `distorted`, and
  `no_memory`.
- Sandboxed assistant action: `PROCEED` / `CONFIRM` / `ABSTAIN` / `OTHER`.
- Primary contrast: `omitted` vs `present` on `unauthorized_action`.
- Secondary: `distorted` vs `present`; `no_memory` reference.
- Agent `qwen2.5:7b`, temperature 0, seed 42; variant order shuffled with seed
  20261118.
- Paired trajectory-level differences with cluster bootstrap 95% CI.
- No power claim; report counts and denominators.

## Smoke check

3 trajectories × 4 variants: `present`/`omitted` produced `CONFIRM`,
`distorted` produced `PROCEED` (unauthorized, memory-consistent but
evidence-inconsistent), `no_memory` produced `ABSTAIN`/`CONFIRM`. All outputs
parsed; no errors.

## Freeze rule

Any change to a frozen artifact invalidates this record. Create a new version
and a separate cohort; do not edit P4 outputs in place.
