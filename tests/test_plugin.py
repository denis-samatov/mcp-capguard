from __future__ import annotations

import pytest

pytest_plugins = ["pytester"]


def test_plugin_generates_one_passing_test_per_profile(pytester: pytest.Pytester) -> None:
    pytester.makepyfile(
        capguard_profiles_module="""
        from mcp_capguard import CapabilityProfile

        class _Server:
            def list_tools(self):
                return ["search"]

        def load():
            return [
                CapabilityProfile(
                    name="readonly",
                    factory=lambda _settings: _Server(),
                    settings=None,
                    must_expose=frozenset({"search"}),
                    must_not_expose=frozenset({"delete"}),
                ),
            ]
        """
    )
    pytester.makepyfile(
        test_capabilities="""
        def test_capability_boundary(capguard_profile):
            capguard_profile.check_sync()
        """
    )
    pytester.makeini(
        """
        [pytest]
        capguard_profiles = capguard_profiles_module:load
        """
    )
    result = pytester.runpytest("-v")
    result.assert_outcomes(passed=1)
    result.stdout.fnmatch_lines(["*test_capability_boundary*readonly*PASSED*"])


def test_plugin_fails_the_specific_profile_on_boundary_violation(
    pytester: pytest.Pytester,
) -> None:
    pytester.makepyfile(
        capguard_profiles_module="""
        from mcp_capguard import CapabilityProfile

        class _Server:
            def list_tools(self):
                return ["search", "delete"]

        def load():
            return [
                CapabilityProfile(
                    name="readonly",
                    factory=lambda _settings: _Server(),
                    settings=None,
                    must_not_expose=frozenset({"delete"}),
                ),
                CapabilityProfile(
                    name="admin",
                    factory=lambda _settings: _Server(),
                    settings=None,
                ),
            ]
        """
    )
    pytester.makepyfile(
        test_capabilities="""
        def test_capability_boundary(capguard_profile):
            capguard_profile.check_sync()
        """
    )
    pytester.makeini(
        """
        [pytest]
        capguard_profiles = capguard_profiles_module:load
        """
    )
    result = pytester.runpytest("-v")
    result.assert_outcomes(passed=1, failed=1)
    result.stdout.fnmatch_lines(["*test_capability_boundary*readonly*FAILED*"])


def test_no_profiles_configured_skips_instead_of_erroring(pytester: pytest.Pytester) -> None:
    # An empty pytest.mark.parametrize list is standard pytest behavior for
    # "skip, there's nothing to run" rather than an error — capguard doesn't
    # override that, so misconfiguration (or a genuinely empty profile list)
    # shows up as a skip, not a silent pass or a crash.
    pytester.makepyfile(
        test_capabilities="""
        def test_capability_boundary(capguard_profile):
            capguard_profile.check_sync()
        """
    )
    result = pytester.runpytest()
    result.assert_outcomes(skipped=1)
