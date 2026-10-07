"""Exercise the published demo commands against the actual MCP SDK."""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path


def test_demo_passes_then_rejects_the_injected_readonly_regression() -> None:
    demo = Path(__file__).resolve().parents[1] / "examples" / "fastmcp_example" / "demo.py"
    passing = subprocess.run(
        [sys.executable, str(demo)], capture_output=True, text=True, timeout=15, check=False
    )
    assert passing.returncode == 0, passing.stderr
    assert "PASS: readonly" in passing.stdout

    failing = subprocess.run(
        [sys.executable, str(demo), "--leak-delete"],
        capture_output=True,
        text=True,
        timeout=15,
        check=False,
    )
    assert failing.returncode == 1, failing.stderr
    assert "capability boundary violated (readonly)" in failing.stdout
    assert "delete_document unexpectedly exposed" in failing.stdout
