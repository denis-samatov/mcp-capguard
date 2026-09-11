from __future__ import annotations

import sys

import pytest

from mcp_capguard.cli import main


@pytest.fixture(autouse=True)
def _run_from_fixtures_dir(monkeypatch: pytest.MonkeyPatch) -> None:
    # Exercise the real entry-point path: a user runs `capguard check` from
    # their project directory, not with the fixtures dir pre-added to
    # sys.path. This is what catches the "cwd isn't importable" class of bug.
    monkeypatch.chdir("tests/fixtures")
    for name in ("passing_profiles", "failing_profiles"):
        sys.modules.pop(name, None)


def test_check_exits_zero_when_all_profiles_pass(capsys: pytest.CaptureFixture[str]) -> None:
    exit_code = main(["check", "--profiles", "passing_profiles:load"])
    assert exit_code == 0
    out = capsys.readouterr().out
    assert "readonly" in out
    assert "SECURITY REGRESSION" not in out


def test_check_exits_one_when_a_profile_violates_boundary(
    capsys: pytest.CaptureFixture[str],
) -> None:
    exit_code = main(["check", "--profiles", "failing_profiles:load"])
    assert exit_code == 1
    out = capsys.readouterr().out
    assert "SECURITY REGRESSION" in out
    assert "readonly → delete" in out


def test_check_raises_a_clear_error_for_an_unimportable_module(
    capsys: pytest.CaptureFixture[str],
) -> None:
    with pytest.raises(ModuleNotFoundError):
        main(["check", "--profiles", "does_not_exist:load"])
