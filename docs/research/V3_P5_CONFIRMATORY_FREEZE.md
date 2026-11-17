# V3 P5 Confirmatory Freeze Record (2026-11-17)

**Decision:** freeze the 2×2 confirmatory mitigation study before generation.

## Frozen artifacts (SHA-256)

| SHA-256 | File |
|---|---|
| `fc572426d857eb2eb03392d3a7a2c2cad7db7611795aa06094bdeaa0ef8f528f` | `docs/research/V3_P5_CONFIRMATORY_PROTOCOL.md` |
| `ace0bac58b66be6f8c00be92d1e5fa2f776b2125ea3963260e01a53aa774f7c2` | `experiments/v3_p5_confirmatory.py` |
| `6e7fe4307dd27cc07ce205c263ab9534805cf9c51784f256c4e93532793f219b` | `docs/research/V3_ANNOTATION_GUIDELINES.md` (v3.2.3) |
| `ff26e30ee4441c0f40a51e9cf04834d055c2d76c20c50534d458d65b6449abcb` | `docs/research/V3_FORMAL_DEFINITIONS.md` (v3.2.3) |

Base commit: `f2ceb1362c703a0ffa8c6d8bee3d1cee14a6a9fb`.

## Design

- 30 P2 trajectories × 4 conditions: `neutral`, `status_aware`,
  `neutral_source`, `status_aware_source`.
- 5-stage chain 220 → 180 → 140 → 120 → 100; writer `qwen2.5:7b`,
  temperature 0, seed 42.
- Primary: human faithful status rate (`NO_DISTORTION` + `LEGITIMATE_UPDATE`)
  among proposition-preserved items, `status_aware` vs `neutral`.
- Secondary: source-access main effect, interaction, best-vs-baseline.
- Budget gate: report inflation; flag any condition above 1.5× neutral.
- 120 blind items; two annotators under v3.2.3; adjudication; κ per field.

## Smoke check

2 trajectories × 4 conditions completed. `status_aware` 1.22× neutral,
`neutral_source` 1.41×, `status_aware_source` 1.70× in the smoke; the full
30-trajectory inflation will be reported against the 1.5× flag.

## Freeze rule

Any change to a frozen artifact invalidates this record. Create a new version
and a separate cohort.
