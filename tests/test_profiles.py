from __future__ import annotations

import pytest

from mcp_capguard import CapabilityProfile, CapabilityViolation
from tests.fake_server import SyncStringServer


class TestCapabilityProfileCheck:
    async def test_check_passes_silently_when_satisfied(self) -> None:
        profile = CapabilityProfile(
            name="readonly",
            factory=lambda _settings: SyncStringServer(["search"]),
            settings=None,
            must_expose=frozenset({"search"}),
        )
        await profile.check()

    async def test_check_raises_with_profile_name_on_violation(self) -> None:
        profile = CapabilityProfile(
            name="readonly",
            factory=lambda _settings: SyncStringServer(["search", "delete"]),
            settings=None,
            must_not_expose=frozenset({"delete"}),
        )
        with pytest.raises(CapabilityViolation) as exc_info:
            await profile.check()
        assert exc_info.value.profile_name == "readonly"
        assert exc_info.value.forbidden == {"delete"}

    def test_check_sync_wraps_the_coroutine(self) -> None:
        profile = CapabilityProfile(
            name="readonly",
            factory=lambda _settings: SyncStringServer(["search"]),
            settings=None,
            must_expose=frozenset({"search"}),
        )
        profile.check_sync()

    def test_check_sync_raises_on_violation(self) -> None:
        profile = CapabilityProfile(
            name="readonly",
            factory=lambda _settings: SyncStringServer(["delete"]),
            settings=None,
            must_not_expose=frozenset({"delete"}),
        )
        with pytest.raises(CapabilityViolation):
            profile.check_sync()

    def test_profile_is_frozen(self) -> None:
        profile = CapabilityProfile(
            name="readonly",
            factory=lambda _settings: SyncStringServer([]),
            settings=None,
        )
        with pytest.raises(AttributeError):
            profile.name = "other"  # type: ignore[misc]
