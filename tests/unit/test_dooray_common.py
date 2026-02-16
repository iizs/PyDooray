import unittest
from unittest.mock import patch, MagicMock
import dooray
from tests.fixtures.responses import MEMBER_RESPONSE, INCOMING_HOOK_RESPONSE


class TestDoorayCommon(unittest.TestCase):
    def setUp(self):
        self._dooray = dooray.Dooray(token="test-token")

    def _make_mock_resp(self, json_data):
        """Helper to create a mock response with status 200."""
        mock_resp = MagicMock()
        mock_resp.status_code = 200
        mock_resp.text = ""
        mock_resp.json.return_value = json_data
        return mock_resp

    @patch("requests.request")
    def test_get_members_no_filter(self, mock_request):
        """P1: get_members() auto-injects name='' when no filters given."""
        mock_request.return_value = self._make_mock_resp(MEMBER_RESPONSE)

        result = self._dooray.get_members()

        call_kwargs = mock_request.call_args
        params = call_kwargs.kwargs["params"]
        self.assertIn("name", params)
        self.assertEqual(params["name"], "")
        self.assertEqual(len(result.result), 1)
        self.assertEqual(result.result[0].name, "Test User")

    @patch("requests.request")
    def test_get_members_with_name(self, mock_request):
        """Does NOT inject name='' when name is already provided."""
        mock_request.return_value = self._make_mock_resp(MEMBER_RESPONSE)

        self._dooray.get_members(name="John")

        call_kwargs = mock_request.call_args
        params = call_kwargs.kwargs["params"]
        self.assertEqual(params["name"], "John")

    @patch("requests.request")
    def test_get_members_with_user_code(self, mock_request):
        """Does NOT inject name='' when user_code is provided."""
        mock_request.return_value = self._make_mock_resp(MEMBER_RESPONSE)

        self._dooray.get_members(user_code="jdoe")

        call_kwargs = mock_request.call_args
        params = call_kwargs.kwargs["params"]
        self.assertIn("userCode", params)
        # name should not be injected since a filter param exists
        self.assertNotIn("name", params)

    @patch("requests.request")
    def test_get_members_with_external_emails_str(self, mock_request):
        """Passes string directly for external_emails."""
        mock_request.return_value = self._make_mock_resp(MEMBER_RESPONSE)

        self._dooray.get_members(external_emails="a@b.com")

        call_kwargs = mock_request.call_args
        params = call_kwargs.kwargs["params"]
        self.assertEqual(params["externalEmailAddresses"], "a@b.com")
        self.assertNotIn("name", params)

    @patch("requests.request")
    def test_get_members_with_external_emails_list(self, mock_request):
        """Joins list with commas for external_emails."""
        mock_request.return_value = self._make_mock_resp(MEMBER_RESPONSE)

        self._dooray.get_members(external_emails=["a@b.com", "c@d.com"])

        call_kwargs = mock_request.call_args
        params = call_kwargs.kwargs["params"]
        self.assertEqual(params["externalEmailAddresses"], "a@b.com,c@d.com")
        self.assertNotIn("name", params)

    @patch("requests.request")
    def test_get_members_pagination(self, mock_request):
        """Passes page and size params correctly."""
        mock_request.return_value = self._make_mock_resp(MEMBER_RESPONSE)

        result = self._dooray.get_members(name="test", page=2, size=50)

        call_kwargs = mock_request.call_args
        params = call_kwargs.kwargs["params"]
        self.assertEqual(params["page"], 2)
        self.assertEqual(params["size"], 50)
        self.assertEqual(result.page, 2)
        self.assertEqual(result.size, 50)

    @patch("requests.request")
    def test_get_incoming_hook(self, mock_request):
        """Correct endpoint and response parsing for get_incoming_hook."""
        mock_request.return_value = self._make_mock_resp(INCOMING_HOOK_RESPONSE)

        result = self._dooray.get_incoming_hook("hook-1")

        mock_request.assert_called_once()
        call_args = mock_request.call_args
        self.assertEqual(call_args[0][0], "GET")
        self.assertIn("/common/v1/incoming-hooks/hook-1", call_args[0][1])
        self.assertEqual(result.result.id, "hook-1")
        self.assertEqual(result.result.name, "Test Hook")
        self.assertEqual(result.result.url, "https://hook.dooray.com/test")
