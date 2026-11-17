# V3 Replication Freeze Record (2026-11-17)

**Decision:** freeze the second-model replication before generation.

## Frozen artifacts (SHA-256)

| SHA-256 | File |
|---|---|
| `4f45d84ae88e88f3243a8cf56470a0b2d84e7d28c54e1127d3a238bcdeae7c7c` | `docs/research/V3_REPLICATION_PROTOCOL.md` |
| `e5a9a4559d341d8b107fbe3e600e199ada6dc8002c45dc2729377fedcd854144` | `experiments/v3_replication_writer.py` |
| `36ec772b6608d4a27c84334f71b39d7ae8af4e287d00652244debe2dda94fda2` | `experiments/v3_p4_behavioral.py` (agent phase) |
| `8c18049942bdfb143171c7d52c8fa9c1993ebb5dc257dbae277ae51e710b2a24` | `docs/research/V3_ANNOTATION_GUIDELINES.md` (v3.2.4) |
| `f23615ea0cce5700d21cc3da2a942c6941a70b4a62d038ed1755426496e7037b` | `docs/research/V3_FORMAL_DEFINITIONS.md` (v3.2.4) |

Base commit: `1632ae73c291ead86334b1e2f69bdbc16c1ae038`.

## Design

- Writer `gemma3:12b`: 12 P2 trajectories × 7 conditions = 84 final memories;
  deterministic diagnostics plus blind human labels under v3.2.4.
- Agent `gemma3:12b`: 30 P2 trajectories × 4 variants = 120 decisions;
  automatic outcomes.
- Replication cohort is separate from the qwen confirmatory runs.

## Smoke

Writer: 1 trajectory, 7/7 conditions complete. Agent: 1 trajectory, 4/4
variants complete, all parsed. `gemma3:12b` latency ~1.5 s (writer) and ~2.6 s
(agent) per call in the smoke.

## Freeze rule

Any change to a frozen artifact invalidates this record.
