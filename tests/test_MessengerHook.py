import unittest
import time
import dooray

MESSENGER_HOOK_URL = '<Your hook url>'
MESSENGER_HOOK_ICON_URL = "<Your hook icon url>"


class TestMessengerHook(unittest.TestCase):
    def setUp(self):
        self._hook = dooray.MessengerHook(MESSENGER_HOOK_URL)

    def tearDown(self):
        time.sleep(1)

    def testSendText(self):
        self._hook.send('Send text: Ok')

    def test_SendTextWithAttachment(self):
        attachments = [{
            "title": "title",
        }]
        self._hook.send('Send Text with attachment: Ok', attachments=attachments)

    def testSendTextWithComplexAttachment(self):
        attachments = [{
            "title": "title",
            "titleLink": "http://dooray.com/",
            "text": "message",
            "color": "red"
        }]
        self._hook.send('Send Text with complex attachment: Ok', attachments=attachments)

    def testSendTextWithMultipleAttachments(self):
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
        self._hook.send('Send Text with multiple attachments: Ok', attachments=attachments)

    def test_SendTextWithAttachmentBuilder(self):
        attachments = dooray.MessengerHookAttachments.builder()\
            .add_attachment(title='title by builder', text='text by builder', color='yellow')\
            .add_attachment(text='awesome text', color='purple')\
            .create()
        self._hook.send('Send Text with attachments builder: Ok', attachments=attachments)


class TestCustomizedMessengerHook(TestMessengerHook):
    def setUp(self):
        self._hook = dooray.MessengerHook(MESSENGER_HOOK_URL, hook_name="My Name", hook_icon=MESSENGER_HOOK_ICON_URL)
