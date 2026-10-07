import pytest
from profiles import leaking_profiles

from mcp_capguard import CapabilityProfile, CapabilityViolation


def test_capability_boundary(capguard_profile: CapabilityProfile) -> None:
    capguard_profile.check_sync()


def test_readonly_policy_rejects_real_send_and_create_tools() -> None:
    with pytest.raises(CapabilityViolation) as failure:
        leaking_profiles()[0].check_sync()
    assert {"send_gmail_message", "create_drive_file"} <= failure.value.forbidden
