from experiments.sample_human_annotation import (
    TARGET_COUNTS,
    _select_stratified,
    build_rows,
)


def _row(question_id: str, failure: str) -> dict:
    return {
        "question_id": question_id,
        "question": f"Question {question_id}",
        "gold_answer": "answer",
        "gold_evidence": [{"source_turn_id": "D1:turn_1", "text": "evidence"}],
        "modes": {
            "real_memory": {
                "answer_failure_type": None if failure == "NONE" else failure,
                "answer": {"correct": False},
            }
        },
    }


def _synthetic_rows() -> list[dict]:
    rows = []
    for failure, count in {
        **TARGET_COUNTS,
        "NONE": 10,
    }.items():
        rows.extend(_row(f"{failure}-{i}", failure) for i in range(count))
    return rows


def test_stratified_sample_contains_required_counts():
    selected = _select_stratified(_synthetic_rows(), total=25, seed=20261012)
    built = build_rows(selected)
    counts = {}
    for row in built:
        counts[row["auto_failure"]] = counts.get(row["auto_failure"], 0) + 1

    for label, expected in TARGET_COUNTS.items():
        assert counts[label] == expected
    assert counts["NONE"] == 6
    assert len(built) == 25


def test_stratified_sample_is_reproducible():
    rows = _synthetic_rows()
    a = _select_stratified(rows, total=25, seed=20261012)
    b = _select_stratified(rows, total=25, seed=20261012)
    assert [r["question_id"] for r in a] == [r["question_id"] for r in b]
