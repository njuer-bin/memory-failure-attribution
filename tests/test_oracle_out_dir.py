import json

from experiments import run_oracle_experiments as runner


def _row(question_id: str) -> dict:
    return {"question_id": question_id, "modes": {"real_memory": {}}}


def _patch_pipeline(monkeypatch, records, calls):
    monkeypatch.setattr(
        runner, "iter_normalized", lambda dataset, limit: list(records),
    )

    def fake_run_record(record, idx):
        calls.append(record["question_id"])
        return _row(record["question_id"])

    monkeypatch.setattr(runner, "run_record", fake_run_record)
    monkeypatch.setattr(
        runner, "_build_summary",
        lambda dataset, limit, rows, errors: {"records": len(rows), "errors": errors},
    )


def test_run_writes_to_explicit_out_dir(monkeypatch, tmp_path):
    """Cross-benchmark runs must not truncate an existing run's comparison.jsonl."""
    calls: list[str] = []
    _patch_pipeline(monkeypatch, [{"question_id": "q1"}], calls)

    summary = runner.run("locomo_refined_public", 1, tmp_path)

    assert summary["records"] == 1
    assert (tmp_path / "summary.json").exists()
    assert (tmp_path / "progress.json").exists()
    rows = (tmp_path / "comparison.jsonl").read_text(encoding="utf-8").splitlines()
    assert [json.loads(row)["question_id"] for row in rows if row] == ["q1"]


def test_resume_skips_completed_questions_and_appends(monkeypatch, tmp_path):
    """An interrupted run must be completable without redoing finished questions."""
    (tmp_path / "comparison.jsonl").write_text(
        json.dumps(_row("q1")) + "\n", encoding="utf-8",
    )
    calls: list[str] = []
    _patch_pipeline(monkeypatch, [{"question_id": "q1"}, {"question_id": "q2"}], calls)

    summary = runner.run("longmemeval_oracle", 2, tmp_path, resume=True)

    assert calls == ["q2"]
    assert summary["resumed_records"] == 1
    rows = (tmp_path / "comparison.jsonl").read_text(encoding="utf-8").splitlines()
    assert [json.loads(row)["question_id"] for row in rows if row] == ["q1", "q2"]


def test_resume_ignores_a_truncated_final_line(monkeypatch, tmp_path):
    """A process killed mid-write leaves a partial line; it must not break resume."""
    (tmp_path / "comparison.jsonl").write_text(
        json.dumps(_row("q1")) + "\n" + '{"question_id": "q2", "mod',
        encoding="utf-8",
    )
    calls: list[str] = []
    _patch_pipeline(monkeypatch, [{"question_id": "q1"}, {"question_id": "q2"}], calls)

    summary = runner.run("longmemeval_oracle", 2, tmp_path, resume=True)

    assert calls == ["q2"]
    assert summary["resumed_records"] == 1
    rows = (tmp_path / "comparison.jsonl").read_text(encoding="utf-8").splitlines()
    assert [json.loads(row)["question_id"] for row in rows if row] == ["q1", "q2"]


def test_without_resume_the_output_is_truncated(monkeypatch, tmp_path):
    (tmp_path / "comparison.jsonl").write_text(
        json.dumps(_row("q1")) + "\n", encoding="utf-8",
    )
    calls: list[str] = []
    _patch_pipeline(monkeypatch, [{"question_id": "q1"}], calls)

    summary = runner.run("longmemeval_oracle", 1, tmp_path)

    assert calls == ["q1"]
    assert summary["resumed_records"] == 0
    rows = (tmp_path / "comparison.jsonl").read_text(encoding="utf-8").splitlines()
    assert [json.loads(row)["question_id"] for row in rows if row] == ["q1"]
