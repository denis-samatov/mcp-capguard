"""pytest plugin: reads a ``module:function`` import path from ini/CLI
config, calls it to get a list of ``CapabilityProfile``, and parametrizes
any test that requests the ``capguard_profile`` fixture — one test run per
profile, each failure naming its specific profile.
"""

from __future__ import annotations

import importlib

import pytest

from mcp_capguard.profiles import CapabilityProfile


def pytest_addoption(parser: pytest.Parser) -> None:
    group = parser.getgroup("capguard")
    group.addoption(
        "--capguard-profiles",
        action="store",
        default=None,
        help=(
            "Import path (module:function) to a zero-arg callable "
            "returning a list[CapabilityProfile]."
        ),
    )
    parser.addini(
        "capguard_profiles",
        help="Same as --capguard-profiles, settable in pytest.ini/pyproject.toml.",
        default=None,
    )


def _resolve_profiles(config: pytest.Config) -> list[CapabilityProfile]:
    target = config.getoption("capguard_profiles") or config.getini("capguard_profiles")
    if not target:
        return []

    module_path, _, attr = target.partition(":")
    if not attr:
        raise pytest.UsageError(f"--capguard-profiles must be 'module:function', got {target!r}")

    module = importlib.import_module(module_path)
    loader = getattr(module, attr)
    profiles = list(loader())
    if not all(isinstance(profile, CapabilityProfile) for profile in profiles):
        raise TypeError(f"{target} must return a list[CapabilityProfile], got {profiles!r}")
    return profiles


def pytest_generate_tests(metafunc: pytest.Metafunc) -> None:
    if "capguard_profile" not in metafunc.fixturenames:
        return
    profiles = _resolve_profiles(metafunc.config)
    metafunc.parametrize(
        "capguard_profile",
        profiles,
        ids=[profile.name for profile in profiles],
    )


@pytest.fixture
def capguard_profile(request: pytest.FixtureRequest) -> CapabilityProfile:
    return request.param
