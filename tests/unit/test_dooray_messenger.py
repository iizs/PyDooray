import unittest
from unittest.mock import patch, MagicMock
import dooray
from tests.fixtures.responses import (
    RESPONSE_HEADER_SUCCESS,
    RELATION_RESPONSE,
    CHANNEL_LIST_RESPONSE,
)


class TestDoorayMessenger(unittest.TestCase):
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
    def test_get_channels(self, mock_request):
        """Verify endpoint and unpaginated response (size=None)."""
        mock_request.return_value = self._make_mock_resp(CHANNEL_LIST_RESPONSE)

        result = self._dooray.messenger.get_channels()

        call_args = mock_request.call_args
        self.assertEqual(call_args[0][0], "GET")
        self.assertIn("/messenger/v1/channels", call_args[0][1])
        self.assertEqual(len(result.result), 1)
        self.assertEqual(result.result[0].id, "ch-1")
        self.assertEqual(result.result[0].title, "Test Channel")

    @patch("requests.request")
    def test_send_direct_message(self, mock_request):
        """Verify correct body payload for direct message."""
        mock_request.return_value = self._make_mock_resp(RESPONSE_HEADER_SUCCESS)

        self._dooray.messenger.send_direct_message("member-1", "Hello")

        call_kwargs = mock_request.call_args
        body = call_kwargs.kwargs["json"]
        self.assertEqual(body["text"], "Hello")
        self.assertEqual(body["organizationMemberId"], "member-1")

    @patch("requests.request")
    def test_send_channel_message(self, mock_request):
        """Verify correct endpoint with channel_id."""
        mock_request.return_value = self._make_mock_resp(RESPONSE_HEADER_SUCCESS)

        self._dooray.messenger.send_channel_message("ch-1", "Hello channel")

        call_args = mock_request.call_args
        self.assertEqual(call_args[0][0], "POST")
        self.assertIn("/messenger/v1/channels/ch-1/logs", call_args[0][1])
        body = call_args.kwargs["json"]
        self.assertEqual(body["text"], "Hello channel")

    @patch("requests.request")
    def test_send_channel_log_alias(self, mock_request):
        """send_channel_log delegates to send_channel_message."""
        mock_request.return_value = self._make_mock_resp(RESPONSE_HEADER_SUCCESS)

        self._dooray.messenger.send_channel_log("ch-1", "Log message")

        call_args = mock_request.call_args
        self.assertIn("/messenger/v1/channels/ch-1/logs", call_args[0][1])
        body = call_args.kwargs["json"]
        self.assertEqual(body["text"], "Log message")

    @patch("requests.request")
    def test_join_channel_single_member(self, mock_request):
        """str member_id is normalized to list."""
        mock_request.return_value = self._make_mock_resp(RESPONSE_HEADER_SUCCESS)

        self._dooray.messenger.join_channel("ch-1", "member-1")

        call_kwargs = mock_request.call_args
        body = call_kwargs.kwargs["json"]
        self.assertEqual(body["memberIds"], ["member-1"])

    @patch("requests.request")
    def test_join_channel_multiple_members(self, mock_request):
        """list member_ids is passed directly."""
        mock_request.return_value = self._make_mock_resp(RESPONSE_HEADER_SUCCESS)

        self._dooray.messenger.join_channel("ch-1", ["member-1", "member-2"])

        call_kwargs = mock_request.call_args
        body = call_kwargs.kwargs["json"]
        self.assertEqual(body["memberIds"], ["member-1", "member-2"])

    @patch("requests.request")
    def test_leave_channel(self, mock_request):
        """Verify correct endpoint and payload for leave_channel."""
        mock_request.return_value = self._make_mock_resp(RESPONSE_HEADER_SUCCESS)

        self._dooray.messenger.leave_channel("ch-1", ["member-1"])

        call_args = mock_request.call_args
        self.assertIn("/messenger/v1/channels/ch-1/members/leave", call_args[0][1])
        body = call_args.kwargs["json"]
        self.assertEqual(body["memberIds"], ["member-1"])

    @patch("requests.request")
    def test_create_channel(self, mock_request):
        """Verify all params: title, member_ids, id_type, channel_type, capacity."""
        mock_request.return_value = self._make_mock_resp(RELATION_RESPONSE)

        self._dooray.messenger.create_channel(
            title="New Channel",
            member_ids=["member-1", "member-2"],
            id_type="email",
            channel_type="public",
            capacity=50
        )

        call_args = mock_request.call_args
        self.assertEqual(call_args[0][0], "POST")
        self.assertIn("/messenger/v1/channels", call_args[0][1])
        params = call_args.kwargs["params"]
        self.assertEqual(params["idType"], "email")
        body = call_args.kwargs["json"]
        self.assertEqual(body["title"], "New Channel")
        self.assertEqual(body["memberIds"], ["member-1", "member-2"])
        self.assertEqual(body["type"], "public")
        self.assertEqual(body["capacity"], 50)
