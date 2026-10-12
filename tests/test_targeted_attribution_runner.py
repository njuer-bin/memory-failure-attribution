from __future__ import annotations

import subprocess
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "experiments" / "run_targeted_attribution.py"


def test_targeted_runner_exposes_exact_question_id_option() -> None:
    result = subprocess.run(
        [sys.executable, str(SCRIPT), "--help"],
        cwd=ROOT,
        capture_output=True,
        text=True,
        check=True,
    )
    assert "--question-id" in result.stdout
    assert "Exact normalized question ID" in result.stdout
