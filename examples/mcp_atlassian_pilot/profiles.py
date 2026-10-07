"""Check client-visible tools, including MCP Atlassian's request-time filters."""

import os
from dataclasses import dataclass, replace
from unittest.mock import patch

from mcp_capguard import CapabilityProfile

READ_TOOLS = frozenset(
    {"jira_search", "jira_get_issue", "confluence_search", "confluence_get_page"}
)
WRITE_TOOLS = frozenset(
    {"jira_create_issue", "jira_delete_issue", "confluence_create_page", "confluence_delete_page"}
)


@dataclass(frozen=True)
class Settings:
    read_only: bool = True
    enabled_tools: tuple[str, ...] = ()


class ClientVisibleTools:
    def __init__(self, settings: Settings) -> None:
        self.settings = settings

    async def list_tools(self) -> list[str]:
        # Isolate the global, environment-configured upstream server. Run serially:
        # this context intentionally changes process-wide environment variables.
        environment = {
            "JIRA_URL": "https://capguard-pilot.atlassian.net",
            "JIRA_USERNAME": "pilot@example.invalid",
            "JIRA_API_TOKEN": "offline-pilot-not-a-token",
            "CONFLUENCE_URL": "https://capguard-pilot.atlassian.net/wiki",
            "CONFLUENCE_USERNAME": "pilot@example.invalid",
            "CONFLUENCE_API_TOKEN": "offline-pilot-not-a-token",
            "READ_ONLY_MODE": str(self.settings.read_only).lower(),
            "TOOLSETS": "all",
            "ENABLED_TOOLS": ",".join(self.settings.enabled_tools),
            "MCP_ATLASSIAN_USE_SYSTEM_TRUSTSTORE": "false",
            "FASTMCP_CHECK_FOR_UPDATES": "off",
            "DO_NOT_TRACK": "1",
        }
        with patch.dict(os.environ, environment, clear=True):
            # Import only inside the isolated environment: module import builds main_mcp.
            from fastmcp import Client
            from mcp_atlassian.servers.main import main_mcp

            async with Client(main_mcp) as client:
                tools = await client.list_tools()
            return [tool.name for tool in tools]


def capguard_profiles() -> list[CapabilityProfile]:
    allowed = ("jira_get_issue", "confluence_get_page")
    return [
        CapabilityProfile(
            name="readonly",
            factory=ClientVisibleTools,
            settings=Settings(),
            must_expose=READ_TOOLS,
            must_not_expose=WRITE_TOOLS,
        ),
        CapabilityProfile(
            name="readwrite",
            factory=ClientVisibleTools,
            settings=Settings(read_only=False),
            must_expose=READ_TOOLS | WRITE_TOOLS,
        ),
        CapabilityProfile(
            name="two-tool-allowlist",
            factory=ClientVisibleTools,
            settings=Settings(read_only=False, enabled_tools=allowed),
            must_expose=frozenset(allowed),
            must_not_expose=(READ_TOOLS - set(allowed)) | WRITE_TOOLS,
        ),
    ]


def leaking_profiles() -> list[CapabilityProfile]:
    """Turn off the real readonly filter while keeping the readonly policy."""
    return [replace(capguard_profiles()[0], settings=Settings(read_only=False))]
