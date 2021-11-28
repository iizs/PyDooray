import requests


class MessengerHook:
    """
    Dooray! messenger incoming hook
    """

    def __init__(
        self,
        hook_url,
        hook_name="My Bot",
        hook_icon="https://static.dooray.com/static_images/dooray-bot.png",
        user_agent="PyDooray/Python",
    ):
        """
        :param hook_url: string
        :param hook_name: string
        :param hook_icon: string
        :param user_agent: string
        """
        assert hook_url is not None and isinstance(hook_url, str), hook_url
        assert hook_name is not None and isinstance(hook_name, str), hook_name
        assert hook_icon is not None and isinstance(hook_icon, str), hook_icon
        assert user_agent is None or isinstance(user_agent, str), user_agent

        self._hook_url = hook_url
        self._hook_name = hook_name
        self._hook_icon = hook_icon
        self._request_header = {
            'User-Agent': user_agent
        }

    def send(self, text, attachments=None):
        """
        Send message
        :param text: string
        :param attachments: list of dict
        :return:
        """
        assert text is not None and isinstance(text, str), text
        assert attachments is None or isinstance(attachments, list), attachments

        payload = {
            'botName': self._hook_name,
            'botIconImage': self._hook_icon,
            'text': text,
        }
        if attachments is not None:
            payload['attachments'] = attachments
        resp = requests.post(self._hook_url, json=payload, headers=self._request_header)
        if resp.status_code != 200:
            pass


class MessengerHookAttachments:
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
        return MessengerHookAttachments()

    def add_attachment(
        self,
        title=None,
        title_link=None,
        text=None,
        color=None
    ):
        e = MessengerHookAttachments._create_attachment(title, title_link, text, color)
        if e is not None:
            self._attachments.append(e)
        return self

    def create(self):
        return self._attachments
