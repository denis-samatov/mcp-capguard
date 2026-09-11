from __future__ import annotations

import pytest

from mcp_capguard import CapabilityViolation, assert_capability_boundary, get_exposed_tool_names
from tests.fake_server import AsyncToolObjectServer, FakeTool, SyncStringServer, WrappedServer


class TestAssertCapabilityBoundary:
    def test_passes_when_boundary_satisfied(self) -> None:
        assert_capability_boundary(
            {"search", "read"},
            must_expose={"search"},
            must_not_expose={"delete"},
        )

    def test_raises_on_missing_required_tool(self) -> None:
        with pytest.raises(CapabilityViolation) as exc_info:
            assert_capability_boundary({"read"}, must_expose={"search"})
        assert exc_info.value.missing == {"search"}
        assert exc_info.value.forbidden == set()

    def test_raises_on_forbidden_tool_present(self) -> None:
        with pytest.raises(CapabilityViolation) as exc_info:
            assert_capability_boundary({"search", "delete"}, must_not_expose={"delete"})
        assert exc_info.value.forbidden == {"delete"}
        assert exc_info.value.missing == set()

    def test_profile_name_is_carried_on_the_exception(self) -> None:
        with pytest.raises(CapabilityViolation) as exc_info:
            assert_capability_boundary(
                {"delete"}, must_not_expose={"delete"}, profile_name="readonly"
            )
        assert exc_info.value.profile_name == "readonly"

    def test_accepts_tool_objects_with_name_attribute(self) -> None:
        assert_capability_boundary([FakeTool(name="search")], must_expose={"search"})

    def test_message_lists_both_missing_and_forbidden(self) -> None:
        with pytest.raises(CapabilityViolation) as exc_info:
            assert_capability_boundary(
                {"delete"},
                must_expose={"search"},
                must_not_expose={"delete"},
                profile_name="readonly",
            )
        message = str(exc_info.value)
        assert "readonly" in message
        assert "search expected but not exposed" in message
        assert "delete unexpectedly exposed" in message


class TestGetExposedToolNames:
    async def test_sync_list_tools_returning_strings(self) -> None:
        server = SyncStringServer(["search", "read"])
        names = await get_exposed_tool_names(lambda _settings: server, settings=None)
        assert names == {"search", "read"}

    async def test_async_list_tools_returning_tool_objects(self) -> None:
        server = AsyncToolObjectServer(["search", "delete"])
        names = await get_exposed_tool_names(lambda _settings: server, settings=None)
        assert names == {"search", "delete"}

    async def test_accessor_unwraps_a_wrapper_object(self) -> None:
        wrapper = WrappedServer(["search"])
        names = await get_exposed_tool_names(
            lambda _settings: wrapper,
            settings=None,
            accessor=lambda app: app.mcp_server,
        )
        assert names == {"search"}

    async def test_missing_list_tools_raises_type_error(self) -> None:
        with pytest.raises(TypeError, match="list_tools"):
            await get_exposed_tool_names(lambda _settings: object(), settings=None)

    async def test_settings_is_passed_through_to_factory(self) -> None:
        captured = []

        def factory(settings: object) -> SyncStringServer:
            captured.append(settings)
            return SyncStringServer(["search"])

        sentinel = object()
        await get_exposed_tool_names(factory, settings=sentinel)
        assert captured == [sentinel]
