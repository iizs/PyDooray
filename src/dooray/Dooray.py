import requests
import datetime
import dooray.DoorayObjects
import dooray.Member
import dooray.IncomingHook
import dooray.Project
import dooray.Messenger
from .DoorayExceptions import BadHttpResponseStatusCode, ServerGeneralError

DEFAULT_ENDPOINT = "https://api.dooray.com"


class DoorayBase:
    """
        This is the base class to access Dooray! API
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

        resp = requests.request(method, f'{self._endpoint}{url}', **kwargs)

        if resp.status_code != 200:
            raise BadHttpResponseStatusCode(resp)
        if resp.text == 'SERVER_GENERAL_ERROR':
            raise ServerGeneralError(resp)

        return resp


class Dooray(DoorayBase):
    """
    This is the main class you instantiate to access the Dooray! API
    """
    def __init__(
        self,
        token=None,
        endpoint=DEFAULT_ENDPOINT,
        user_agent="PyDooray/Python",
    ):
        super().__init__(token, endpoint, user_agent)
        self.messenger = DoorayMessenger(token, endpoint, user_agent)
        self.project = DoorayProject(token, endpoint, user_agent)

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
        """

        :param name:
        :param user_code:
        :param user_code_exact:
        :param id_provider_user_id:
        :param external_emails:
        :param page:
        :param size:
        :return:
        """
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

        resp = self._request('GET', f'/common/v1/members', params=params)

        return dooray.DoorayObjects.DoorayListResponse(resp.json(), dooray.Member.Member, page=page, size=size)

    def get_incoming_hook(self, incoming_hook_id):
        """
        https://hook.dooray.com/services/<?>/<incoming_hook_id>/<?>
        :param incoming_hook_id:
        :return:
        """
        resp = self._request('GET', f'/common/v1/incoming-hooks/{incoming_hook_id}')

        return dooray.DoorayObjects.DoorayResponse(resp.json(), dooray.IncomingHook.IncomingHook)


class DoorayMessenger(DoorayBase):
    """
        This is the class to access the Dooray! Messenger API
        """

    def __init__(
            self,
            token=None,
            endpoint=DEFAULT_ENDPOINT,
            user_agent="PyDooray/Python",
    ):
        super().__init__(token, endpoint, user_agent)

    @staticmethod
    def _get_member_id_list(member_ids):
        member_id_list = []
        if isinstance(member_ids, str):
            member_id_list.append(member_ids)
        elif isinstance(member_ids, list):
            member_id_list.extend(member_ids)
        else:
            assert False, member_ids
        return member_id_list

    def get_channels(self):
        """

        :return:
        """

        resp = self._request('GET', f'/messenger/v1/channels')

        return dooray.DoorayObjects.DoorayListResponse(resp.json(), dooray.Messenger.Channel, size=None)

    def send_direct_message(self, member_id, text):
        """

        :param member_id:
        :param text:
        :return:
        """
        data = {
            'text': text,
            'organizationMemberId': member_id,
        }

        resp = self._request('POST', f'/messenger/v1/channels/direct-send', json=data)

        return dooray.DoorayObjects.DoorayResponse(resp.json())

    def send_channel_message(self, channel_id, text):
        """

        :param channel_id:
        :param text:
        :return:
        """
        data = {
            'text': text,
        }

        resp = self._request('POST', f'/messenger/v1/channels/{channel_id}/logs', json=data)

        return dooray.DoorayObjects.DoorayResponse(resp.json())

    def send_channel_log(self, channel_id, text):
        """
        Alias for send_channel_message()
        """
        return self.send_channel_message(channel_id, text)

    def join_channel(self, channel_id, member_ids):
        """

        :param channel_id:
        :param member_ids:
        :return:
        """
        data = {
            'memberIds': DoorayMessenger._get_member_id_list(member_ids),
        }

        resp = self._request('POST', f'/messenger/v1/channels/{channel_id}/members/join', json=data)

        return dooray.DoorayObjects.DoorayResponse(resp.json())

    def leave_channel(self, channel_id, member_ids):
        """

        :param channel_id:
        :param member_ids:
        :return:
        """
        data = {
            'memberIds': DoorayMessenger._get_member_id_list(member_ids),
        }

        resp = self._request('POST', f'/messenger/v1/channels/{channel_id}/members/leave', json=data)

        return dooray.DoorayObjects.DoorayResponse(resp.json())

    def create_channel(self, title, member_ids, id_type='memberId', channel_type='private', capacity=100):
        """

        :param title:
        :param channel_type:
        :param member_ids:
        :param id_type:
        :param capacity:
        :return:
        """
        # TODO Creating 'private' channel with the same name and the same member do not return CHANNEL_ALREADY_EXISTS_ERROR(-300101)
        # TODO Creating 'direct' channel returns HTTP status code 500
        data = {
            'memberIds': DoorayMessenger._get_member_id_list(member_ids),
            'capacity': capacity,
            'type': channel_type,
            'title':title,
        }
        params = {
            'idType': id_type,
        }
        resp = self._request('POST', f'/messenger/v1/channels', params=params, json=data)

        return dooray.DoorayObjects.DoorayResponse(resp.json(), dooray.DoorayObjects.Relation)


class DoorayProject(DoorayBase):
    """
        This is the class to access the Dooray! Project API
        """

    def __init__(
            self,
            token=None,
            endpoint=DEFAULT_ENDPOINT,
            user_agent="PyDooray/Python",
    ):
        super().__init__(token, endpoint, user_agent)

    def is_creatable(self, code):
        """
        """
        data = {
            'code': code,
        }

        try:
            self._request('POST', f'/project/v1/projects/is-creatable', json=data)
        except BadHttpResponseStatusCode as e:
            return False

        return True

    def create(self, code, description, scope='private'):
        """
        """
        data = {
            'code': code,
            'description': description,
            'scope': scope,
        }

        resp = self._request('POST', f'/project/v1/projects', json=data)

        return dooray.DoorayObjects.DoorayResponse(resp.json(), dooray.DoorayObjects.Relation)

    def get(self, project_id):
        """

        :param project_id:
        :return:
        """
        resp = self._request('GET', f'/project/v1/projects/{project_id}')

        return dooray.DoorayObjects.DoorayResponse(resp.json(), dooray.Project.Project)

    def get_workflows(self, project_id):
        """

        :param project_id:
        :return:
        """
        resp = self._request('GET', f'/project/v1/projects/{project_id}/workflows')

        return dooray.DoorayObjects.DoorayListResponse(resp.json(), dooray.Project.Workflow)

    def create_email_address(self, project_id, email_address, name):
        """
        """
        data = {
            'emailAddress': email_address,
            'name': name,
        }

        resp = self._request('POST', f'/project/v1/projects/{project_id}/email-addresses', json=data)

        return dooray.DoorayObjects.DoorayResponse(resp.json(), dooray.DoorayObjects.Relation)

    def get_email_address(self, project_id, email_address_id):
        """

        :param project_id:
        :param email_address_id:
        :return:
        """

        resp = self._request('GET', f'/project/v1/projects/{project_id}/email-addresses/{email_address_id}')

        return dooray.DoorayObjects.DoorayResponse(resp.json(), dooray.Project.EmailAddress)

    def create_tag(self, project_id, name=None, color=None):
        """

        :param project_id:
        :param name:
        :param color:
        :return:
        """
        assert name is not None and isinstance(name, str), name
        assert color is not None and isinstance(color, str), color

        data = {
            'name': name,
            'color': color,
        }
        # TODO color parameter only accepts string in 'xxxxxx' format

        resp = self._request('POST', f'/project/v1/projects/{project_id}/tags', json=data)

        return dooray.DoorayObjects.DoorayResponse(resp.json(), dooray.DoorayObjects.Relation)

    def get_tag(self, project_id, tag_id):
        """

        :param project_id:
        :param tag_id:
        :return:
        """

        resp = self._request('GET', f'/project/v1/projects/{project_id}/tags/{tag_id}')

        return dooray.DoorayObjects.DoorayResponse(resp.json(), dooray.Project.Tag)

    def create_milestone(self, project_id, name, start_at, end_at):
        """

        :param project_id:
        :param name:
        :param start_at:
        :param end_at:
        :return:
        """
        assert name is not None and isinstance(name, str), name
        assert start_at is not None and (isinstance(start_at, str) or isinstance(start_at, datetime)), start_at
        assert end_at is not None and (isinstance(end_at, str) or isinstance(end_at, datetime)), end_at

        data = {
            'name': name,
            'startedAt': start_at,
            'endedAt': end_at,
        }
        # TODO if startedAt parameter is given as '2021-12-01+09:00', UI shows it as '2021-11-30'
        # TODO even if startedAt, endedAt parameters are given in other than KST format string, it is converted to KST
        # TODO how to create a milestone without period?

        resp = self._request('POST', f'/project/v1/projects/{project_id}/milestones', json=data)

        return dooray.DoorayObjects.DoorayResponse(resp.json(), dooray.DoorayObjects.Relation)

    def get_milestones(self, project_id, page=0, size=20, status=None):
        """

        :param project_id:
        :param page:
        :param size:
        :param status:
        :return:
        """
        params = {}
        if page is not None:
            params['page'] = page
        if size is not None:
            params['size'] = size
        if status is not None:
            params['status'] = status

        resp = self._request('GET', f'/project/v1/projects/{project_id}/milestones', params=params)

        return dooray.DoorayObjects.DoorayListResponse(resp.json(), dooray.Project.Milestone, page=page, size=size)

    def get_milestone(self, project_id, milestone_id):
        """

        :param project_id:
        :param milestone_id:
        :return:
        """

        resp = self._request('GET', f'/project/v1/projects/{project_id}/milestones/{milestone_id}')
        # TODO in case of milestone_id is wrong, returns 200 OK with 'SERVER_GENERAL_ERROR', not a json object

        return dooray.DoorayObjects.DoorayResponse(resp.json(), dooray.Project.Milestone)

    def update_milestone(self, project_id, milestone_id, name, status, start_at, end_at):
        """

        :param project_id:
        :param milestone_id:
        :param name:
        :param status:
        :param start_at:
        :param end_at:
        :return:
        """
        assert name is not None and isinstance(name, str), name
        assert status is not None and isinstance(status, str), status

        data = {
            'name': name,
            'status': status,
            'startedAt': start_at,
            'endedAt': end_at,
        }
        # TODO closedAt not updated if status set as 'closed' with this API

        resp = self._request('PUT', f'/project/v1/projects/{project_id}/milestones/{milestone_id}', json=data)

        return dooray.DoorayObjects.DoorayResponse(resp.json())

    def delete_milestone(self, project_id, milestone_id):
        """

        :param project_id:
        :param milestone_id:
        :return:
        """

        resp = self._request('DELETE', f'/project/v1/projects/{project_id}/milestones/{milestone_id}')

        return dooray.DoorayObjects.DoorayResponse(resp.json())

    def create_hook(self, project_id, url, send_events):
        """

        :param project_id:
        :param url:
        :param send_events:
        :return:
        """
        assert url is not None and isinstance(url, str), url
        assert send_events is not None and isinstance(send_events, list), send_events
        # TODO send_events must contains subset of [ "postCreated", "postCommentCreated", "postTagChanged", "postDueDateChanged", "postWorkflowChanged" ]

        data = {
            'url': url,
            'sendEvents': send_events,
        }

        resp = self._request('POST', f'/project/v1/projects/{project_id}/hooks', json=data)

        return dooray.DoorayObjects.DoorayResponse(resp.json(), dooray.DoorayObjects.Relation)

    def add_member(self, project_id, member_id, role='member'):
        """

        :param project_id:
        :param member_id:
        :param role:
        :return:
        """
        assert member_id is not None and isinstance(member_id, str), member_id
        assert role is not None and isinstance(role, str), role

        data = {
            'organizationMemberId': member_id,
            'role': role,
        }

        resp = self._request('POST', f'/project/v1/projects/{project_id}/members', json=data)
        # TODO result object is different from the API document
        # TODO if already exist member, do nothing. but the response is the same as payload

        return dooray.DoorayObjects.DoorayResponse(resp.json(), dooray.Project.ProjectMember)

    def get_member(self, project_id, member_id):
        """

        :param project_id:
        :param member_id:
        :return:
        """
        resp = self._request('GET', f'/project/v1/projects/{project_id}/members/{member_id}')

        return dooray.DoorayObjects.DoorayResponse(resp.json(), dooray.Project.ProjectMember)

    def get_member_groups(self, project_id, page=0, size=20):
        """

        :param project_id:
        :param page:
        :param size:
        :return:
        """
        params = {}
        # TODO does not works correctly due to API error

        if page is not None:
            params['page'] = page
        if size is not None:
            params['size'] = size

        resp = self._request('GET', f'/project/v1/projects/{project_id}/member-groups', params=params)
        # TODO result returns list of lists. looks like an error

        return dooray.DoorayObjects.DoorayListResponse(resp.json(), dooray.Project.MemberGroup, page=page, size=size)

    def get_member_group(self, project_id, member_group_id):
        """

        :param project_id:
        :param member_group_id:
        :return:
        """

        resp = self._request('GET', f'/project/v1/projects/{project_id}/member-groups/{member_group_id}')

        return dooray.DoorayObjects.DoorayResponse(resp.json(), dooray.Project.MemberGroup)

    # TODO Project > Template
    # TODO Project > Posts
    # TODO Projects > Posts > Logs
