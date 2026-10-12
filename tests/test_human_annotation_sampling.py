from experiments.sample_human_annotation import (
    TARGET_COUNTS,
    _gold_evidence_text,
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
    for failure, count in {**TARGET_COUNTS, "NONE": 10}.items():
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


def test_gold_evidence_text_prefers_persisted_timestamp():
    row = _row("time-case", "NONE")
    row["gold_evidence"][0]["timestamp"] = "8 May 2023"
    text, context = _gold_evidence_text(
        row,
        time_index={("other-question", "D1:turn_1"): {"timestamp": "2026-10-12"}},
    )
    assert "[D1:turn_1 | 8 May 2023] evidence" == text
    assert context == "D1:turn_1 = 8 May 2023"


def test_gold_evidence_time_index_is_scoped_by_question_id():
    row = _row("q0006", "NONE")
    text, context = _gold_evidence_text(
        row,
        time_index={
            ("q0006", "D1:turn_1"): {"timestamp": "27 January 2023"},
            ("q0020", "D1:turn_1"): {"timestamp": "12 July 2023"},
        },
    )
    assert "27 January 2023" in text
    assert "12 July 2023" not in text
    assert context == "D1:turn_1 = 27 January 2023"


def test_build_rows_exposes_time_context_column():
    row = _row("time-case", "NONE")
    built = build_rows(
        [row],
        time_index={("time-case", "D1:turn_1"): {"timestamp": "8 May 2023"}},
    )
    assert built[0]["gold_evidence_time_context"] == "D1:turn_1 = 8 May 2023"
    assert "8 May 2023" in built[0]["gold_evidence"]
