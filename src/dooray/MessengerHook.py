import copy

import requests


class MessengerHook:
    """
    Dooray! messenger incoming hook helper class.
    """

    def __init__(
        self,
        hook_url,
        hook_name="My Bot",
        hook_icon="https://static.dooray.com/static_images/dooray-bot.png",
        user_agent="PyDooray/Python",
    ):
        """
        :param hook_url: Hook URL
        :type hook_url: str
        :param hook_name: Name of the hook. Defaults to "My Bot"
        :type hook_name: str, optional
        :param hook_icon: Icon URL of the hook. Defaults to "https://static.dooray.com/static_images/dooray-bot.png"
        :type hook_icon: str, optional
        :param user_agent: User agent of the request. Defaults to "PyDooray/Python"
        :type user_agent: str, optional
        """
        if not isinstance(hook_url, str):
            raise TypeError(hook_url)
        if not isinstance(hook_name, str):
            raise TypeError(hook_name)
        if not isinstance(hook_icon, str):
            raise TypeError(hook_icon)
        if user_agent is not None and not isinstance(user_agent, str):
            raise TypeError(user_agent)

        self._hook_url = hook_url
        self._hook_name = hook_name
        self._hook_icon = hook_icon
        self._request_header = {
            'User-Agent': user_agent
        }

    def send(self, text, attachments=None):
        """
        Send a message to the hook.

        :param text: Message text
        :type text: str
        :param attachments: List of dictionaries of attachments.\
            Attachment specifications could be found from \
            `Dooray Messenger Incoming Hook Data Format \
            <https://helpdesk.dooray.com/share/pages/9wWo-xwiR66BO5LGshgVTg/2900079844453730084>`_. \
            You may also use :obj:`dooray.MessengerHookAttachments` to create an input for this parameter. \
            Defaults to None
        :type attachments: list, optional
        """
        if not isinstance(text, str):
            raise TypeError(text)
        if attachments is not None and not isinstance(attachments, list):
            raise TypeError(attachments)

        payload = {
            'botName': self._hook_name,
            'botIconImage': self._hook_icon,
            'text': text,
        }
        if attachments is not None:
            payload['attachments'] = attachments
        resp = requests.post(self._hook_url, json=payload, headers=self._request_header)
        return resp.status_code == 200


class MessengerHookAttachments:
    """
    Dooray! messenger incoming hook attachment helper class.

    Usage::

        import dooray

        attachments = dooray.MessengerHookAttachments.builder()\\
             .add_attachment(title='Nice title', title_link= 'http://dooray.com/', text='Simple text', color='red')\\
             .add_attachment(text='Awesome text in purple box', color='purple')\\
             .create()
    """
    def __init__(self):
        self._attachments = []

    @staticmethod
    def _create_attachment(title, title_link, text, color):
        e = {}
        if title is not None:
            e['title'] = title
        if title_link is not None:
            e['titleLink'] = title_link
        if text is not None:
            e['text'] = text
        if color is not None:
            e['color'] = color

        if len(e.keys()) == 0:
            e = None
        return e

    @staticmethod
    def builder():
        """
        Create a new builder.
        """
        return MessengerHookAttachments()

    def add_attachment(
        self,
        title=None,
        title_link=None,
        text=None,
        color=None
    ):
        """
        Add an attachment to the builder.

        :param title: Title of the attachment. Defaults to None
        :type title: str, optional
        :param title_link: Title link of the attachment. Defaults to None
        :type title_link: str, optional
        :param text: Text of the attachment. Defaults to None
        :type text: str, optional
        :param color: Color of the attachment. Defaults to None
        :type color: str, optional
        """
        e = MessengerHookAttachments._create_attachment(title, title_link, text, color)
        if e is not None:
            self._attachments.append(e)
        return self

    def create(self):
        """
        Create a list of attachments.

        Returns a deep copy of the internal state, allowing the builder
        to be reused as a template for creating multiple similar attachments.
        """
        return copy.deepcopy(self._attachments)
