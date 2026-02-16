import unittest
import dooray


class TestMessengerHookAttachments(unittest.TestCase):
    def testCreateAttachment(self):
        self.assertEqual(dooray.MessengerHookAttachments._create_attachment(None, None, None, None), None)

        self.assertEqual(
            dooray.MessengerHookAttachments._create_attachment('My title', None, None, None),
            {'title': 'My title'}
        )
        self.assertEqual(
            dooray.MessengerHookAttachments._create_attachment('My title', 'http://a.com', None, None),
            {'title': 'My title', 'titleLink': 'http://a.com'}
        )
        self.assertEqual(
            dooray.MessengerHookAttachments._create_attachment('My title', 'http://a.com', 'My text', None),
            {'title': 'My title', 'titleLink': 'http://a.com', 'text': 'My text'}
        )
        self.assertEqual(
            dooray.MessengerHookAttachments._create_attachment('My title', 'http://a.com', 'My text', 'red'),
            {'title': 'My title', 'titleLink': 'http://a.com', 'text': 'My text', 'color': 'red'}
        )
        self.assertEqual(
            dooray.MessengerHookAttachments._create_attachment('My title', None, 'My text', 'red'),
            {'title': 'My title', 'text': 'My text', 'color': 'red'}
        )
        self.assertEqual(
            dooray.MessengerHookAttachments._create_attachment('My title', 'http://a.com', None, 'red'),
            {'title': 'My title', 'titleLink': 'http://a.com', 'color': 'red'}
        )
        self.assertEqual(
            dooray.MessengerHookAttachments._create_attachment(None, 'http://a.com', 'My text', 'red'),
            {'titleLink': 'http://a.com', 'text': 'My text', 'color': 'red'}
        )

    def testBuilder(self):
        self.assertEqual(
            dooray.MessengerHookAttachments.builder()
                .add_attachment(title='My title')
                .create(),
            [{'title': 'My title'}]
        )
        self.assertEqual(
            dooray.MessengerHookAttachments.builder()
            .add_attachment(title='My title')
            .add_attachment(title_link='http://b.com', text='My text')
            .create(),
            [{'title': 'My title'}, {'titleLink': 'http://b.com', 'text': 'My text'}]
        )
