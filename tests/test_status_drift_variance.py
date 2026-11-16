from experiments.status_drift_variance import memory_identity


def test_memory_identity_counts_identical_cells():
    a = {"s1": {"direct_memories": {"1": "x", "2": "y"},
                "recursive_memories": {"1": "r"}}}
    b = {"s1": {"direct_memories": {"1": "x", "2": "z"},
                "recursive_memories": {"1": "r"}}}
    identity = memory_identity(a, b)
    assert identity["direct_d1"]["rate"] == 1.0
    assert identity["direct_d2"]["rate"] == 0.0
    assert identity["recursive_d1"]["rate"] == 1.0


def test_memory_identity_ignores_missing_cells():
    a = {"s1": {"direct_memories": {"1": "x"}}}
    b = {"s1": {"direct_memories": {}}}
    assert memory_identity(a, b) == {}
