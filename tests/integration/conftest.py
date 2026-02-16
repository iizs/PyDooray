"""Integration test configuration. Requires valid API token."""
import pytest
import dooray
from tests.tokens import API_TOKEN


@pytest.fixture
def dooray_client():
    return dooray.Dooray(API_TOKEN)


@pytest.fixture
def project_id():
    return "3172006893461634976"
