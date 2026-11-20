from experiments.v3_p4_2_v3_runner import (
    CONTROL_HALF_FLOOR,
    control_half_floor_warning,
)


def test_half_floor_is_inclusive():
    assert control_half_floor_warning(0.50)
    assert control_half_floor_warning(0.0)
    assert not control_half_floor_warning(0.55)


def test_exact_boundary_from_counts_warns():
    # The qwen2.5:7b action control is exactly 10/20; it must be flagged.
    assert CONTROL_HALF_FLOOR == 0.5
    assert control_half_floor_warning(10 / 20)


def test_missing_rate_falls_back_to_warning():
    assert control_half_floor_warning(None)
