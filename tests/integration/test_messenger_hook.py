"""Integration tests for MessengerHook.

Requires a valid Messenger Hook URL.
Pure pytest functions with module-scoped fixtures.
"""
import time
import pytest
import dooray
from tests.tokens import MESSENGER_HOOK_URL

MESSENGER_HOOK_ICON_URL = "https://nhnent.dooray.com/messenger/v1/api/stickers/16/01_on_110px"

pytestmark = pytest.mark.integration


@pytest.fixture(scope="module")
def hook():
    return dooray.MessengerHook(MESSENGER_HOOK_URL)


@pytest.fixture(scope="module")
def custom_hook():
    return dooray.MessengerHook(
        MESSENGER_HOOK_URL,
        hook_name="Under Construction",
        hook_icon=MESSENGER_HOOK_ICON_URL
    )


@pytest.fixture(autouse=True)
def _api_cooldown():
    """Pause between tests to avoid Dooray API rate limiting."""
    yield
    time.sleep(1)


# --- Default hook tests ---

def test_send_text(hook):
    hook.send('Send text: Ok')


def test_send_text_with_attachment(hook):
    attachments = [{"title": "title"}]
    hook.send('Send Text with attachment: Ok', attachments=attachments)


def test_send_text_with_complex_attachment(hook):
    attachments = [{
        "title": "title",
        "titleLink": "http://dooray.com/",
        "text": "message",
        "color": "red"
    }]
    hook.send('Send Text with complex attachment: Ok', attachments=attachments)


def test_send_text_with_multiple_attachments(hook):
    attachments = [
        {
            "title": "title",
            "titleLink": "http://dooray.com/",
            "text": "message",
            "color": "red"
        },
        {
            "title": "title",
            "titleLink": "http://dooray.com/",
            "text": "message in green",
            "color": "green"
        },
        {
            "title": "title",
            "titleLink": "http://dooray.com/",
            "text": "message in #0000ff",
            "color": "#0000ff"
        },
    ]
    hook.send('Send Text with multiple attachments: Ok', attachments=attachments)


def test_send_text_with_attachment_builder(hook):
    attachments = dooray.MessengerHookAttachments.builder()\
        .add_attachment(title='title by builder', text='text by builder', color='yellow')\
        .add_attachment(text='awesome text', color='purple')\
        .create()
    hook.send('Send Text with attachments builder: Ok', attachments=attachments)


# --- Custom hook tests (same scenarios, different hook config) ---

def test_custom_send_text(custom_hook):
    custom_hook.send('Send text: Ok')


def test_custom_send_text_with_attachment(custom_hook):
    attachments = [{"title": "title"}]
    custom_hook.send('Send Text with attachment: Ok', attachments=attachments)


def test_custom_send_text_with_complex_attachment(custom_hook):
    attachments = [{
        "title": "title",
        "titleLink": "http://dooray.com/",
        "text": "message",
        "color": "red"
    }]
    custom_hook.send('Send Text with complex attachment: Ok', attachments=attachments)


def test_custom_send_text_with_multiple_attachments(custom_hook):
    attachments = [
        {
            "title": "title",
            "titleLink": "http://dooray.com/",
            "text": "message",
            "color": "red"
        },
        {
            "title": "title",
            "titleLink": "http://dooray.com/",
            "text": "message in green",
            "color": "green"
        },
        {
            "title": "title",
            "titleLink": "http://dooray.com/",
            "text": "message in #0000ff",
            "color": "#0000ff"
        },
    ]
    custom_hook.send('Send Text with multiple attachments: Ok', attachments=attachments)


def test_custom_send_text_with_attachment_builder(custom_hook):
    attachments = dooray.MessengerHookAttachments.builder()\
        .add_attachment(title='title by builder', text='text by builder', color='yellow')\
        .add_attachment(text='awesome text', color='purple')\
        .create()
    custom_hook.send('Send Text with attachments builder: Ok', attachments=attachments)
