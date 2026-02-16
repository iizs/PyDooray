"""Integration test configuration. Requires valid API token."""
import random
import time
import pytest
import dooray
from tests.tokens import API_TOKEN

TEST_MEMBER_NAMES = ['mark', 'bess', 'rick', 'kirin']


@pytest.fixture(scope="module")
def dooray_client():
    """Dooray client shared across all tests in a module."""
    return dooray.Dooray(API_TOKEN)


@pytest.fixture(scope="module")
def project_id(dooray_client):
    """Create a test project once per module.

    Returns the project ID. The project persists after tests
    (Dooray API does not provide a project delete endpoint).
    """
    ts = int(time.time())
    project = dooray_client.project.create(
        f'PyDooray-{ts}',
        f'Integration test {ts}',
        'private'
    )
    return project.result.id


@pytest.fixture(scope="module")
def test_member(dooray_client):
    """Look up a random known test member once per module.

    Raises RuntimeError if the member is not found.
    """
    name = random.choice(TEST_MEMBER_NAMES)
    members = dooray_client.get_members(name=name)
    if members.total_count == 0:
        raise RuntimeError(
            f"No member found with name='{name}'. "
            "Verify test member accounts exist in the Dooray organization."
        )
    return members.result[0]


@pytest.fixture(autouse=True)
def _api_cooldown():
    """Pause between tests to avoid Dooray API rate limiting."""
    yield
    time.sleep(0.5)


def get_random_member(dooray_client):
    """Fetch a random test member from TEST_MEMBER_NAMES.

    Use when the test doesn't care which specific member is used
    (e.g., assigning a post recipient, adding a project member).
    Each call may return a different member.

    :param dooray_client: Dooray client instance
    :returns: Member object
    :raises RuntimeError: if no member found
    """
    name = random.choice(TEST_MEMBER_NAMES)
    members = dooray_client.get_members(name=name)
    if members.total_count == 0:
        raise RuntimeError(
            f"No member found with name='{name}'. "
            "Verify test member accounts exist in the Dooray organization."
        )
    return members.result[0]


def get_member_by_name(dooray_client, name):
    """Fetch a specific test member by name.

    Use when the test requires a deterministic, specific member
    (e.g., verifying filter results for a known user, testing with
    a particular member's permissions).

    :param dooray_client: Dooray client instance
    :param name: Member name to search for (must exist in Dooray organization)
    :returns: Member object
    :raises RuntimeError: if no member found with the given name
    """
    members = dooray_client.get_members(name=name)
    if members.total_count == 0:
        raise RuntimeError(
            f"No member found with name='{name}'. "
            "Verify the member account exists in the Dooray organization."
        )
    return members.result[0]
