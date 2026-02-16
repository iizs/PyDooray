import unittest
from unittest.mock import patch, MagicMock
import dooray


class TestMessengerHook(unittest.TestCase):
    def setUp(self):
        self._hook = dooray.MessengerHook(hook_url="https://hook.example.com/test")

    @patch("requests.post")
    def test_send_returns_true_on_success(self, mock_post):
        """P0: send() must return True when status_code == 200."""
        mock_resp = MagicMock()
        mock_resp.status_code = 200
        mock_post.return_value = mock_resp

        result = self._hook.send("Hello")

        self.assertTrue(result)

    @patch("requests.post")
    def test_send_returns_false_on_failure(self, mock_post):
        """P0: send() must return False when status_code != 200."""
        mock_resp = MagicMock()
        mock_resp.status_code = 500
        mock_post.return_value = mock_resp

        result = self._hook.send("Hello")

        self.assertFalse(result)

    @patch("requests.post")
    def test_send_payload_structure(self, mock_post):
        """Verify the JSON body contains botName, botIconImage, and text."""
        mock_resp = MagicMock()
        mock_resp.status_code = 200
        mock_post.return_value = mock_resp

        self._hook.send("Test message")

        call_kwargs = mock_post.call_args
        payload = call_kwargs.kwargs["json"]
        self.assertEqual(payload["botName"], "My Bot")
        self.assertEqual(payload["text"], "Test message")
        self.assertIn("botIconImage", payload)

    @patch("requests.post")
    def test_send_with_attachments(self, mock_post):
        """Verify attachments key is included when provided."""
        mock_resp = MagicMock()
        mock_resp.status_code = 200
        mock_post.return_value = mock_resp

        attachments = [{"title": "test"}]
        self._hook.send("Hello", attachments=attachments)

        call_kwargs = mock_post.call_args
        payload = call_kwargs.kwargs["json"]
        self.assertIn("attachments", payload)
        self.assertEqual(payload["attachments"], [{"title": "test"}])

    @patch("requests.post")
    def test_send_without_attachments(self, mock_post):
        """Verify attachments key is absent when None."""
        mock_resp = MagicMock()
        mock_resp.status_code = 200
        mock_post.return_value = mock_resp

        self._hook.send("Hello")

        call_kwargs = mock_post.call_args
        payload = call_kwargs.kwargs["json"]
        self.assertNotIn("attachments", payload)

    def test_constructor_assertions(self):
        """Verify assertion errors on invalid constructor params."""
        with self.assertRaises(AssertionError):
            dooray.MessengerHook(hook_url=None)
        with self.assertRaises(AssertionError):
            dooray.MessengerHook(hook_url=123)
        with self.assertRaises(AssertionError):
            dooray.MessengerHook(hook_url="http://ok", hook_name=None)
        with self.assertRaises(AssertionError):
            dooray.MessengerHook(hook_url="http://ok", hook_icon=None)
