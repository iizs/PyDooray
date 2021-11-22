import requests
import dooray.DoorayObjects
import dooray.Member
from .DoorayExceptions import BadHttpResponseStatusCode

DEFAULT_ENDPOINT = "https://api.dooray.com"


class Dooray:
    """
    This is the main class you instantiate to access the Dooray! API
    """
    def __init__(
        self,
        token=None,
        endpoint=DEFAULT_ENDPOINT,
        user_agent="PyDooray/Python",
    ):
        assert token is not None and isinstance(token, str), token
        assert endpoint is not None and isinstance(endpoint, str), endpoint
        assert user_agent is None or isinstance(user_agent, str), user_agent

        self._token = token
        self._endpoint = endpoint
        self._request_header = {
            'Authorization': f'dooray-api {self._token}',
            'User-Agent': user_agent,
        }

    def _request(self, method, url, **kwargs):
        if 'headers' in kwargs:
            kwargs['headers'].update(self._request_header)
        else:
            kwargs['headers'] = self._request_header

        resp = requests.request(method, url, **kwargs)

        if resp.status_code != 200:
            raise BadHttpResponseStatusCode(resp)

        return resp

    def get_members(
        self,
        name=None,
        user_code=None,
        user_code_exact=None,
        id_provider_user_id=None,
        external_emails=None,
        page=0,
        size=20
    ):
        params = {}
        if name is not None:
            params['name'] = name
        if user_code is not None:
            params['userCode'] = user_code
        if user_code_exact is not None:
            params['userCodeExact'] = user_code_exact
        if id_provider_user_id is not None:
            params['idProviderUserId'] = id_provider_user_id
        if external_emails is not None:
            if isinstance(external_emails, str):
                params['externalEmailAddresses'] = external_emails
            elif isinstance(external_emails, list):
                params['externalEmailAddresses'] = ','.join([str(e) for e in external_emails])
        if page is not None:
            params['page'] = page
        if size is not None:
            params['size'] = size

        resp = self._request('GET', f'{self._endpoint}/common/v1/members', params=params)

        return dooray.DoorayObjects.DoorayListResponse(resp.json(), dooray.Member.Member, page=page, size=size)

