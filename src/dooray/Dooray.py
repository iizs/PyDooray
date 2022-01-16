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
        """
        :param token: Dooray! API token
        :type token: str
        :param endpoint: Dooray! API endpoint, defaults to "https://api.dooray.com"
        :type endpoint: str
        :param user_agent: User agent string, defaults to "PyDooray/Python"
        :type user_agent: str
        """
        super().__init__(token, endpoint, user_agent)

        self.messenger = DoorayMessenger(token, endpoint, user_agent)
        """
        Messenger object to access Dooray! Messenger API
        
        :type: :class:`dooray.DoorayMessenger`
        """

        self.project = DoorayProject(token, endpoint, user_agent)
        """
        Project object to access Dooray! Project API

        :type: :class:`dooray.DoorayProject`
        """

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
        Returns a list of members which match the given criteria.

        :calls: `GET /common/v1/members \
            <https://helpdesk.dooray.com/share/pages/9wWo-xwiR66BO5LGshgVTg/2939987647631384419>`_

        :param name: Name of the member
        :type name: str
        :param user_code: User ID of the member, partial match
        :type user_code: str
        :param user_code_exact: User ID of the member, exact match
        :type user_code_exact: str
        :param id_provider_user_id: User ID from SSO provider
        :type id_provider_user_id: str
        :param external_emails: List of external emails of the member, exact match, comma separated
        :type external_emails: str
        :param page: Page number, starts from 0, defaults to 0
        :type page: int
        :param size: Page size, defaults to 20, max is 100
        :type size: int
        :return: :class:`dooray.DoorayObjects.DoorayListResponse` of :class:`dooray.Member.Member`
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
        # TODO when no parameter given, it returns bad request.
        #  but with name='' or userCode='' parameter, it returns all members. is it intended?

        resp = self._request('GET', f'/common/v1/members', params=params)

        return dooray.DoorayObjects.DoorayListResponse(resp.json(), dooray.Member.Member, page=page, size=size)

    def get_incoming_hook(self, incoming_hook_id):
        """
        Get an incoming hook information

        :calls: `GET /common/v1/incomingHooks/{incoming-hook-id} \
            <https://helpdesk.dooray.com/share/pages/9wWo-xwiR66BO5LGshgVTg/2939987647631384419>`_
        :param incoming_hook_id: Incoming hook ID
        :type incoming_hook_id: str
        :return: :class:`dooray.DoorayObjects.DoorayResponse` of :class:`dooray.IncomingHook.IncomingHook`
        """
        resp = self._request('GET', f'/common/v1/incoming-hooks/{incoming_hook_id}')

        return dooray.DoorayObjects.DoorayResponse(resp.json(), dooray.IncomingHook.IncomingHook)


class DoorayMessenger(DoorayBase):
    """
    This is the class to access the Dooray! Messenger API.

    Instead of instantiating this class directly, use :class:`dooray.Dooray.messenger`
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
        Get a list of messenger channels available.

        :calls: `GET /messenger/v1/channels \
            <https://helpdesk.dooray.com/share/pages/9wWo-xwiR66BO5LGshgVTg/2939987647631384419>`_
        :return: :class:`dooray.DoorayObjects.DoorayListResponse` of :class:`dooray.Messenger.Channel`
        """

        resp = self._request('GET', f'/messenger/v1/channels')

        return dooray.DoorayObjects.DoorayListResponse(resp.json(), dooray.Messenger.Channel, size=None)

    def send_direct_message(self, member_id, text):
        """
        Send a direct message to a member.

        :param member_id: Member ID of the recipient
        :type member_id: str
        :param text: Message text
        :type text: str
        :return: :class:`dooray.DoorayObjects.DoorayResponse`
        """
        data = {
            'text': text,
            'organizationMemberId': member_id,
        }

        resp = self._request('POST', f'/messenger/v1/channels/direct-send', json=data)

        return dooray.DoorayObjects.DoorayResponse(resp.json())

    def send_channel_message(self, channel_id, text):
        """
        Send a message to a channel.

        :call: `POST /messenger/v1/channels/{channel-id}/send \
            <https://helpdesk.dooray.com/share/pages/9wWo-xwiR66BO5LGshgVTg/2939987647631384419>`_
        :param channel_id: Channel ID
        :type channel_id: str
        :param text: Message text
        :type text: str
        :return: :class:`dooray.DoorayObjects.DoorayResponse`
        """
        data = {
            'text': text,
        }

        resp = self._request('POST', f'/messenger/v1/channels/{channel_id}/logs', json=data)

        return dooray.DoorayObjects.DoorayResponse(resp.json())

    def send_channel_log(self, channel_id, text):
        """
        Alias for :class:`dooray.DoorayMessenger.send_channel_message`
        """
        return self.send_channel_message(channel_id, text)

    def join_channel(self, channel_id, member_ids):
        """
        Add members to a messenger channel.

        :calls: `POST /messenger/v1/channels/{channel-id}/members/join \
            <https://helpdesk.dooray.com/share/pages/9wWo-xwiR66BO5LGshgVTg/2939987647631384419>`_
        :param channel_id: Channel ID
        :type channel_id: str
        :param member_ids: List of member IDs
        :type member_ids: str or list
        :return: :class:`dooray.DoorayObjects.DoorayResponse`
        """
        data = {
            'memberIds': DoorayMessenger._get_member_id_list(member_ids),
        }

        resp = self._request('POST', f'/messenger/v1/channels/{channel_id}/members/join', json=data)

        return dooray.DoorayObjects.DoorayResponse(resp.json())

    def leave_channel(self, channel_id, member_ids):
        """
        Remove members from a messenger channel.

        :calls: `POST /messenger/v1/channels/{channel-id}/members/leave \
            <https://helpdesk.dooray.com/share/pages/9wWo-xwiR66BO5LGshgVTg/2939987647631384419>`_
        :param channel_id: Channel ID
        :type channel_id: str
        :param member_ids: List of member IDs
        :type member_ids: str or list
        :return: :class:`dooray.DoorayObjects.DoorayResponse`
        """
        data = {
            'memberIds': DoorayMessenger._get_member_id_list(member_ids),
        }

        resp = self._request('POST', f'/messenger/v1/channels/{channel_id}/members/leave', json=data)

        return dooray.DoorayObjects.DoorayResponse(resp.json())

    def create_channel(self, title, member_ids, id_type='memberId', channel_type='private', capacity=100):
        """
        Create a new messenger channel.

        :calls: `POST /messenger/v1/channels \
            <https://helpdesk.dooray.com/share/pages/9wWo-xwiR66BO5LGshgVTg/2939987647631384419>`_
        :param title: Title of the channel
        :type title: str
        :param member_ids: Member IDs of the channel members
        :type member_ids: list
        :param id_type: Type of the member IDs. Can be 'memberId' or 'email'. Default is 'memberId'.
        :type id_type: str
        :param channel_type: Type of the channel. Can be 'private' or 'public'. Default is 'private'.
        :type channel_type: str
        :param capacity: Capacity of the channel. Default is 100.
        :type capacity: int
        :return: :class:`dooray.DoorayObjects.DoorayResponse` of :class:`dooray.DoorayObjects.Relation`
        """
        # TODO Creating 'private' channel with the same name and the same member
        #  does not return CHANNEL_ALREADY_EXISTS_ERROR(-300101)
        # TODO Creating 'direct' channel returns HTTP status code 500
        # TODO Handle when member_ids is a string
        data = {
            'memberIds': DoorayMessenger._get_member_id_list(member_ids),
            'capacity': capacity,
            'type': channel_type,
            'title': title,
        }
        params = {
            'idType': id_type,
        }
        resp = self._request('POST', f'/messenger/v1/channels', params=params, json=data)

        return dooray.DoorayObjects.DoorayResponse(resp.json(), dooray.DoorayObjects.Relation)


class DoorayProject(DoorayBase):
    """
    This is the class to access the Dooray! Project API

    Instead of instantiating this class directly, use :class:`dooray.Dooray.project`
    """

    def __init__(
            self,
            token=None,
            endpoint=DEFAULT_ENDPOINT,
            user_agent="PyDooray/Python",
    ):
        super().__init__(token, endpoint, user_agent)

    # Project > Projects
    def is_creatable(self, code):
        """
        Test if a project is creatable.

        :calls: `GET /project/v1/projects/is-creatable \
            <https://helpdesk.dooray.com/share/pages/9wWo-xwiR66BO5LGshgVTg/2939987647631384419>`_
        :param code: Project name
        :type code: str
        :return: True if creatable, False otherwise
        """
        data = {
            'code': code,
        }

        try:
            self._request('POST', f'/project/v1/projects/is-creatable', json=data)
        except BadHttpResponseStatusCode:
            return False

        return True

    def create(self, code, description, scope='private'):
        """
        Create a new project.

        :calls: `POST /project/v1/projects \
            <https://helpdesk.dooray.com/share/pages/9wWo-xwiR66BO5LGshgVTg/2939987647631384419>`_
        :param code: Project name
        :type code: str
        :param description: Project description
        :type description: str
        :param scope: Project scope. Can be 'private' or 'public'. Default is 'private'.
        :type scope: str
        :return: :class:`dooray.DoorayObjects.DoorayResponse` of :class:`dooray.DoorayObjects.Relation`
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
        Get a project information.

        :calls: `GET /project/v1/projects/{project-id} \
            <https://helpdesk.dooray.com/share/pages/9wWo-xwiR66BO5LGshgVTg/2939987647631384419>`_
        :param project_id: Project ID
        :type project_id: str
        :return: :class:`dooray.DoorayObjects.DoorayResponse` of :class:`dooray.Project.Project`
        """
        resp = self._request('GET', f'/project/v1/projects/{project_id}')

        return dooray.DoorayObjects.DoorayResponse(resp.json(), dooray.Project.Project)

    def get_workflows(self, project_id):
        """
        Get a project workflows.

        :calls: `GET /project/v1/projects/{project-id}/workflows \
            <https://helpdesk.dooray.com/share/pages/9wWo-xwiR66BO5LGshgVTg/2939987647631384419>`_
        :param project_id: Project ID
        :type project_id: str
        :return: :class:`dooray.DoorayObjects.DoorayResponse` of :class:`dooray.Project.Workflow`
        """
        resp = self._request('GET', f'/project/v1/projects/{project_id}/workflows')

        return dooray.DoorayObjects.DoorayListResponse(resp.json(), dooray.Project.Workflow)

    # Project > Projects > EmailAddress
    def create_email_address(self, project_id, email_address, name):
        """
        Create a new project email address.

        :calls: `POST /project/v1/projects/{project-id}/email-addresses \
            <https://helpdesk.dooray.com/share/pages/9wWo-xwiR66BO5LGshgVTg/2939987647631384419>`_
        :param project_id: Project ID
        :type project_id: str
        :param email_address: Email address
        :type email_address: str
        :param name: Name
        :type name: str
        :return: :class:`dooray.DoorayObjects.DoorayResponse` of :class:`dooray.DoorayObjects.Relation`
        """
        data = {
            'emailAddress': email_address,
            'name': name,
        }

        resp = self._request('POST', f'/project/v1/projects/{project_id}/email-addresses', json=data)

        return dooray.DoorayObjects.DoorayResponse(resp.json(), dooray.DoorayObjects.Relation)

    def get_email_address(self, project_id, email_address_id):
        """
        Get a project email address.

        :calls: `GET /project/v1/projects/{project-id}/email-addresses/{email-address-id} \
            <https://helpdesk.dooray.com/share/pages/9wWo-xwiR66BO5LGshgVTg/2939987647631384419>`_
        :param project_id: Project ID
        :type project_id: str
        :param email_address_id: Email address ID
        :type email_address_id: str
        :return: :class:`dooray.DoorayObjects.DoorayResponse` of :class:`dooray.Project.EmailAddress`
        """

        resp = self._request('GET', f'/project/v1/projects/{project_id}/email-addresses/{email_address_id}')

        return dooray.DoorayObjects.DoorayResponse(resp.json(), dooray.Project.EmailAddress)

    # TODO Email delete API needed

    # Project > Projects > Tags
    def create_tag(self, project_id, name=None, color=None):
        """
        Create a new tag for a project.

        :calls: `POST /project/v1/projects/{project-id}/tags \
            <https://helpdesk.dooray.com/share/pages/9wWo-xwiR66BO5LGshgVTg/2939987647631384419>`_
        :param project_id: Project ID
        :type project_id: str
        :param name: Name of the tag
        :type name: str
        :param color: Color of the tag in hexadecimal format. For example, 'FFFFFF'
        :type color: str
        :return: :class:`dooray.DoorayObjects.DoorayResponse` of :class:`dooray.DoorayObjects.Relation`
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
        Get a project tag.

        :calls: `GET /project/v1/projects/{project-id}/tags/{tag-id} \
            <https://helpdesk.dooray.com/share/pages/9wWo-xwiR66BO5LGshgVTg/2939987647631384419>`_
        :param project_id: Project ID
        :type project_id: str
        :param tag_id: Tag ID
        :type tag_id: str
        :return: :class:`dooray.DoorayObjects.DoorayResponse` of :class:`dooray.Project.Tag`
        """

        resp = self._request('GET', f'/project/v1/projects/{project_id}/tags/{tag_id}')

        return dooray.DoorayObjects.DoorayResponse(resp.json(), dooray.Project.Tag)

    # TODO Tag delete API needed

    # Project > Projects > Milestones
    def create_milestone(self, project_id, name, start_at, end_at):
        """
        Create a new milestone for a project.

        :calls: `POST /project/v1/projects/{project-id}/milestones \
            <https://helpdesk.dooray.com/share/pages/9wWo-xwiR66BO5LGshgVTg/2939987647631384419>`_
        :param project_id: Project ID
        :type project_id: str
        :param name: Name of the milestone
        :type name: str
        :param start_at: Start date of the milestone in 'YYYY-MM-DD+ZZ' format. For example, '2019-01-01+00:00'
        :type start_at: str
        :param end_at: End date of the milestone in 'YYYY-MM-DD+ZZ' format. For example, '2019-01-01+00:00'
        :type end_at: str
        :return: :class:`dooray.DoorayObjects.DoorayResponse` of :class:`dooray.DoorayObjects.Relation`
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
        Get milestones of a project.

        :calls: `GET /project/v1/projects/{project-id}/milestones \
            <https://helpdesk.dooray.com/share/pages/9wWo-xwiR66BO5LGshgVTg/2939987647631384419>`_
        :param project_id: Project ID
        :type project_id: str
        :param page: Page number. Starts from 0. Default is 0.
        :type page: int
        :param size: Number of items per page. Default is 20.
        :type size: int
        :param status: Filter milestones by status. Default is None.
        :type status: 'open' | 'closed'
        :return: :class:`dooray.DoorayObjects.DoorayListResponse` of :class:`dooray.Project.Milestone`
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
        Get a milestone in a project.

        :calls: `GET /project/v1/projects/{project-id}/milestones/{milestone-id} \
            <https://helpdesk.dooray.com/share/pages/9wWo-xwiR66BO5LGshgVTg/2939987647631384419>`_
        :param project_id: Project ID
        :type project_id: str
        :param milestone_id: Milestone ID
        :type milestone_id: str
        :return: :class:`dooray.DoorayObjects.DoorayResponse` of :class:`dooray.Project.Milestone`
        """

        resp = self._request('GET', f'/project/v1/projects/{project_id}/milestones/{milestone_id}')
        # TODO in case of milestone_id is wrong, returns 200 OK with 'SERVER_GENERAL_ERROR', not a json object

        return dooray.DoorayObjects.DoorayResponse(resp.json(), dooray.Project.Milestone)

    def update_milestone(self, project_id, milestone_id, name, status, start_at, end_at):
        """
        Update a milestone.

        :calls: `PUT /project/v1/projects/{project-id}/milestones/{milestone-id} \
            <https://helpdesk.dooray.com/share/pages/9wWo-xwiR66BO5LGshgVTg/2939987647631384419>`_
        :param project_id: Project ID
        :type project_id: str
        :param milestone_id: Milestone ID
        :type milestone_id: str
        :param name: Name of the milestone
        :param status: Status of the milestone.
        :type status:  'open' | 'closed'
        :param start_at: Start date of the milestone in 'YYYY-MM-DD+ZZ' format. For example, '2019-01-01+00:00'
        :type start_at: str
        :param end_at: End date of the milestone in 'YYYY-MM-DD+ZZ' format. For example, '2019-01-01+00:00'
        :type end_at: str
        :return: :class:`dooray.DoorayObjects.DoorayResponse`
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
        Delete a milestone in a project.

        :calls: `DELETE /project/v1/projects/{project-id}/milestones/{milestone-id} \
            <https://helpdesk.dooray.com/share/pages/9wWo-xwiR66BO5LGshgVTg/2939987647631384419>`_
        :param project_id: Project ID
        :type project_id: str
        :param milestone_id: Milestone ID
        :type milestone_id: str
        :return: :class:`dooray.DoorayObjects.DoorayResponse`
        """

        resp = self._request('DELETE', f'/project/v1/projects/{project_id}/milestones/{milestone_id}')

        return dooray.DoorayObjects.DoorayResponse(resp.json())

    # Project > Projects > Hooks
    def create_hook(self, project_id, url, send_events):
        """
        Create a hook in a project.

        :calls: `POST /project/v1/projects/{project-id}/hooks \
            <https://helpdesk.dooray.com/share/pages/9wWo-xwiR66BO5LGshgVTg/2939987647631384419>`_
        :param project_id: Project ID
        :type project_id: str
        :param url: URL of the hook
        :type url: str
        :param send_events: Events list to be sent to the hook. Possible events are as following:
            "postCreated", "postCommentCreated", "postTagChanged", "postDueDateChanged", "postWorkflowChanged"
        :type send_events: list
        :return: :class:`dooray.DoorayObjects.DoorayResponse` of :class:`dooray.DoorayObjects.Relation`
        """
        assert url is not None and isinstance(url, str), url
        assert send_events is not None and isinstance(send_events, list), send_events
        # TODO send_events must contains subset of
        #  [ "postCreated", "postCommentCreated", "postTagChanged", "postDueDateChanged", "postWorkflowChanged" ]

        data = {
            'url': url,
            'sendEvents': send_events,
        }

        resp = self._request('POST', f'/project/v1/projects/{project_id}/hooks', json=data)

        return dooray.DoorayObjects.DoorayResponse(resp.json(), dooray.DoorayObjects.Relation)

    # TODO delete Hook API needed

    # Project > Projects > Members
    def add_member(self, project_id, member_id, role='member'):
        """
        Add a member to a project.

        :calls: `POST /project/v1/projects/{project-id}/members \
            <https://helpdesk.dooray.com/share/pages/9wWo-xwiR66BO5LGshgVTg/2939987647631384419>`_
        :param project_id: Project ID
        :type project_id: str
        :param member_id: Member ID
        :type member_id: str
        :param role: Role of the member. Default is 'member'
        :type role: 'member' | 'admin'
        :return: :class:`dooray.DoorayObjects.DoorayResponse` of :class:`dooray.Project.ProjectMember`
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
        Get a member of a project.

        :calls: `GET /project/v1/projects/{project-id}/members/{member-id} \
            <https://helpdesk.dooray.com/share/pages/9wWo-xwiR66BO5LGshgVTg/2939987647631384419>`_
        :param project_id: Project ID
        :type project_id: str
        :param member_id: Member ID
        :type member_id: str
        :return: :class:`dooray.DoorayObjects.DoorayResponse` of :class:`dooray.Project.ProjectMember`
        """
        resp = self._request('GET', f'/project/v1/projects/{project_id}/members/{member_id}')

        return dooray.DoorayObjects.DoorayResponse(resp.json(), dooray.Project.ProjectMember)

    # Project > Projects > MemberGroups
    def get_member_groups(self, project_id, page=0, size=20):
        """
        Get member groups of a project.

        :calls: `GET /project/v1/projects/{project-id}/member-groups \
            <https://helpdesk.dooray.com/share/pages/9wWo-xwiR66BO5LGshgVTg/2939987647631384419>`_
        :param project_id: Project ID
        :type project_id: str
        :param page: Page number. Starts from 0. Default is 0
        :type page: int
        :param size: Number of items per page. Default is 20
        :type size: int
        :return: :class:`dooray.DoorayObjects.DoorayListResponse` of :class:`dooray.Project.MemberGroup`
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
        Get a member group of a project.

        :calls: `GET /project/v1/projects/{project-id}/member-groups/{member-group-id} \
            <https://helpdesk.dooray.com/share/pages/9wWo-xwiR66BO5LGshgVTg/2939987647631384419>`_
        :param project_id: Project ID
        :type project_id: str
        :param member_group_id: Member group ID
        :type member_group_id: str
        :return: :class:`dooray.DoorayObjects.DoorayResponse` of :class:`dooray.Project.MemberGroup`
        """

        resp = self._request('GET', f'/project/v1/projects/{project_id}/member-groups/{member_group_id}')

        return dooray.DoorayObjects.DoorayResponse(resp.json(), dooray.Project.MemberGroup)

    # Project > Projects > Template
    def create_template(self, project_id, template):
        """
        Create a post template to a project.

        :calls: `POST /project/v1/projects/{project-id}/templates \
            <https://helpdesk.dooray.com/share/pages/9wWo-xwiR66BO5LGshgVTg/2939987647631384419>`_
        :param project_id: Project ID
        :type project_id: str
        :param template: Template object to write. See :class:`dooray.TemplateBuilder`
        :return: :class:`dooray.DoorayObjects.DoorayResponse` of :class:`dooray.DoorayObjects.Relation`
        """
        # TODO html support for 'body' and 'guide'
        resp = self._request('POST', f'/project/v1/projects/{project_id}/templates', json=template.to_json_dict())

        return dooray.DoorayObjects.DoorayResponse(resp.json(), dooray.DoorayObjects.Relation)

    def get_templates(self, project_id, page=0, size=20):
        """
        Get post templates of a project.

        :calls: `GET /project/v1/projects/{project-id}/templates \
            <https://helpdesk.dooray.com/share/pages/9wWo-xwiR66BO5LGshgVTg/2939987647631384419>`_
        :param project_id: Project ID
        :type project_id: str
        :param page: Page number. Starts from 0. Default is 0
        :type page: int
        :param size: Number of items per page. Default is 20
        :type size: int
        :return: :class:`dooray.DoorayObjects.DoorayListResponse` of :class:`dooray.Project.ReadTemplate`
        """
        params = {}

        if page is not None:
            params['page'] = page
        if size is not None:
            params['size'] = size

        resp = self._request('GET', f'/project/v1/projects/{project_id}/templates', params=params)

        return dooray.DoorayObjects.DoorayListResponse(resp.json(), dooray.Project.ReadTemplate, page=page, size=size)

    def get_template(self, project_id, template_id, interpolation=False):
        """
        Get a post template of a project.

        :calls: `GET /project/v1/projects/{project-id}/templates/{template-id} \
            <https://helpdesk.dooray.com/share/pages/9wWo-xwiR66BO5LGshgVTg/2939987647631384419>`_
        :param project_id: Project ID
        :type project_id: str
        :param template_id: Template ID
        :type template_id: str
        :param interpolation: If true, returns the interpolated template. Default is false
        :type interpolation: bool
        :return: :class:`dooray.DoorayObjects.DoorayResponse` of :class:`dooray.Project.ReadTemplate`
        """
        params = {}
        if interpolation:
            params['interpolation'] = 'true'

        resp = self._request('GET', f'/project/v1/projects/{project_id}/templates/{template_id}', params=params)

        return dooray.DoorayObjects.DoorayResponse(resp.json(), dooray.Project.ReadTemplate)

    def update_template(self, project_id, template_id, template):
        """
        Update a post template of a project.

        :calls: `PUT /project/v1/projects/{project-id}/templates/{template-id} \
            <https://helpdesk.dooray.com/share/pages/9wWo-xwiR66BO5LGshgVTg/2939987647631384419>`_
        :param project_id: Project ID
        :type project_id: str
        :param template_id: Template ID
        :type template_id: str
        :param template: Template object to write. See :class:`dooray.TemplateBuilder`
        :return: :class:`dooray.DoorayObjects.DoorayResponse`
        """
        # TODO html support for 'body' and 'guide'
        resp = self._request(
            'PUT',
            f'/project/v1/projects/{project_id}/templates/{template_id}',
            json=template.to_json_dict()
        )

        return dooray.DoorayObjects.DoorayResponse(resp.json())

    def delete_template(self, project_id, template_id):
        """
        Delete a post template of a project.

        :calls: `DELETE /project/v1/projects/{project-id}/templates/{template-id} \
            <https://helpdesk.dooray.com/share/pages/9wWo-xwiR66BO5LGshgVTg/2939987647631384419>`_
        :param project_id: Project ID
        :type project_id: str
        :param template_id: Template ID
        :type template_id: str
        :return: :class:`dooray.DoorayObjects.DoorayResponse`
        """
        resp = self._request('DELETE', f'/project/v1/projects/{project_id}/templates/{template_id}')

        return dooray.DoorayObjects.DoorayResponse(resp.json())

    # Project > Projects > Posts
    def create_post(self, project_id, post):
        """
        Create a post to a project.

        :calls: `POST /project/v1/projects/{project-id}/posts \
            <https://helpdesk.dooray.com/share/pages/9wWo-xwiR66BO5LGshgVTg/2939987647631384419>`_
        :param project_id: Project ID
        :type project_id: str
        :param post: The post object to be written. See :class:`dooray.PostBuilder` for more details.
        :return: :class:`dooray.DoorayObjects.DoorayResponse` of :class:`dooray.DoorayObjects.Relation`
        """
        resp = self._request('POST', f'/project/v1/projects/{project_id}/posts', json=post.to_json_dict())
        # TODO 'parentPostId' seems not working correctly
        # TODO html support for 'body'

        return dooray.DoorayObjects.DoorayResponse(resp.json(), dooray.DoorayObjects.Relation)

    def get_posts(self, project_id,
                  page=0, size=20,
                  from_email_address=None,
                  from_member_ids=None,
                  to_member_ids=None,
                  cc_member_ids=None,
                  tag_ids=None,
                  parent_post_id=None,
                  post_workflow_classes=None,
                  post_workflow_ids=None,
                  milestone_ids=None,
                  created_at=None,
                  updated_at=None,
                  due_at=None,
                  order=None
                  ):
        """
        Get posts of a project which match the given criteria.

        :calls: `GET /project/v1/projects/{project-id}/posts \
            <https://helpdesk.dooray.com/share/pages/9wWo-xwiR66BO5LGshgVTg/2939987647631384419>`_
        :param project_id: Project ID
        :type project_id: str
        :param page: Page number. Starts from 0. Default is 0.
        :type page: int
        :param size: Number of posts per page. Default is 20.
        :type size: int
        :param from_email_address: Email address of the sender. Default is None.
        :type from_email_address: str
        :param from_member_ids: Member ID of the sender. Default is None.
        :type from_member_ids: str
        :param to_member_ids: Member ID of the receiver. Default is None.
        :type to_member_ids: str
        :param cc_member_ids: Member ID of the CC receiver. Default is None.
        :type cc_member_ids: str
        :param tag_ids: Project tag ID. Default is None.
        :type tag_ids: str
        :param parent_post_id: Parent post ID. Default is None.
        :type parent_post_id: str
        :param post_workflow_classes: Post workflow classes. Default is None.
        :type post_workflow_classes: str or list of str
        :param post_workflow_ids: Post workflow IDs. Default is None.
        :type post_workflow_ids: str or list of str
        :param milestone_ids: Milestone ID. Default is None.
        :type milestone_ids: str
        :param created_at: Created at. See below for the date format. Default is None.
        :type created_at: str
        :param updated_at: Updated at. See below for the date format. Default is None.
        :type updated_at: str
        :param due_at: Due at. See below for the date format. Default is None.
        :type due_at: str
        :param order: Sort order of the returned posts. Possible values are 'postDueAt', 'postUpdatedAt', 'createdAt',\
            '-postDueAt', '-postUpdatedAt' and '-createdAt'. '-' means reverse order. Default is None.
        :type order: str
        :return: :class:`dooray.DoorayObjects.DoorayListResponse` of :class:`dooray.Project.ReadPost`
        :date format: Possible values are as follows:

        * today
        * thisweek: A week starts from Monday
        * prev-{N}d: N is an integer. Example: prev-7d
        * next-{N}d: N is an integer. Example: next-7d
        * {YYYY-MM-DDThh:mm:ssZ}~{YYYY-MM-DDThh:mm:ssZ}: A range of dates in ISO8601 format. \
        Example: 2019-01-01T00:00:00Z~2019-01-02T00:00:00Z
        """
        params = {}

        # TODO *_ids may need to be converted from list to comma separated string
        if page is not None:
            params['page'] = page
        if size is not None:
            params['size'] = size
        if from_email_address is not None:
            params['fromEmailAddress'] = from_email_address
        if from_member_ids is not None:
            params['fromMemberIds'] = from_member_ids
        if to_member_ids is not None:
            params['toMemberIds'] = to_member_ids
        if cc_member_ids is not None:
            params['ccMemberIds'] = cc_member_ids
        if tag_ids is not None:
            params['ccMemberIds'] = tag_ids
        if parent_post_id is not None:
            params['parentPostId'] = parent_post_id
        if post_workflow_ids is not None:
            params['postWorkflowIds'] = post_workflow_ids
        if post_workflow_classes is not None:
            params['postWorkflowClasses'] = post_workflow_classes
        if milestone_ids is not None:
            params['milestoneIds'] = milestone_ids
        if created_at is not None:
            params['createdAt'] = created_at
        if updated_at is not None:
            params['updatedAt'] = updated_at
        if due_at is not None:
            params['dueAt'] = due_at
        if order is not None:
            params['order'] = order

        resp = self._request('GET', f'/project/v1/projects/{project_id}/posts', params=params)

        return dooray.DoorayObjects.DoorayListResponse(resp.json(), dooray.Project.ReadPost, page=page, size=size)

    def get_post(self, project_id, post_id):
        """
        Get a post.

        :calls: `GET /project/v1/projects/{project-id}/posts/{post-id} \
            <https://helpdesk.dooray.com/share/pages/9wWo-xwiR66BO5LGshgVTg/2939987647631384419>`_
        :param project_id: Project ID.
        :type project_id: str
        :param post_id: Post ID.
        :type post_id: str
        :return: :class:`dooray.DoorayObjects.DoorayResponse` of :class:`dooray.Project.ReadPost`
        """

        resp = self._request('GET', f'/project/v1/projects/{project_id}/posts/{post_id}')

        return dooray.DoorayObjects.DoorayResponse(resp.json(), dooray.Project.ReadPost)

    def update_post(self, project_id, post_id, post):
        """
        Update a post.

        :calls: `PUT /project/v1/projects/{project-id}/posts/{post-id} \
            <https://helpdesk.dooray.com/share/pages/9wWo-xwiR66BO5LGshgVTg/2939987647631384419>`_
        :param project_id: Project ID.
        :type project_id: str
        :param post_id: Post ID.
        :type post_id: str
        :param post: The post object to be written. See :class:`dooray.PostBuilder` for more details.
        :return: :class:`dooray.DoorayObjects.DoorayResponse`
        """
        # TODO 'parentPostId' seems not working correctly
        # TODO html support for 'body'
        resp = self._request('PUT', f'/project/v1/projects/{project_id}/posts/{post_id}', json=post.to_json_dict())

        return dooray.DoorayObjects.DoorayResponse(resp.json())

    def set_post_workflow_for_member(self, project_id, post_id, member_id, workflow_id):
        """
        Set a workflow of a post for a member.

        :calls: `PUT /project/v1/projects/{project-id}/posts/{post-id}/to/{member-id} \
            <https://helpdesk.dooray.com/share/pages/9wWo-xwiR66BO5LGshgVTg/2939987647631384419>`_
        :param project_id: Project ID.
        :type project_id: str
        :param post_id: Post ID.
        :type post_id: str
        :param member_id: Member ID.
        :type member_id: str
        :param workflow_id: Workflow ID.
        :type workflow_id: str
        :return: :class:`dooray.DoorayObjects.DoorayResponse`
        """
        data = {
            'workflowId': workflow_id
        }
        resp = self._request('PUT', f'/project/v1/projects/{project_id}/posts/{post_id}/to/{member_id}', json=data)

        return dooray.DoorayObjects.DoorayResponse(resp.json())

    def set_post_workflow(self, project_id, post_id, workflow_id):
        """
        Set a workflow of a post.

        :calls: `PUT /project/v1/projects/{project-id}/posts/{post-id}/set-workflow \
            <https://helpdesk.dooray.com/share/pages/9wWo-xwiR66BO5LGshgVTg/2939987647631384419>`_
        :param project_id: Project ID.
        :type project_id: str
        :param post_id: Post ID.
        :type post_id: str
        :param workflow_id: Workflow ID.
        :type workflow_id: str
        :return: :class:`dooray.DoorayObjects.DoorayResponse`
        """
        data = {
            'workflowId': workflow_id
        }
        resp = self._request('POST', f'/project/v1/projects/{project_id}/posts/{post_id}/set-workflow', json=data)

        return dooray.DoorayObjects.DoorayResponse(resp.json())

    def set_post_as_done(self, project_id, post_id):
        """
        Set a post as done.

        :calls: `PUT /project/v1/projects/{project-id}/posts/{post-id}/set-done \
            <https://helpdesk.dooray.com/share/pages/9wWo-xwiR66BO5LGshgVTg/2939987647631384419>`_
        :param project_id: Project ID.
        :type project_id: str
        :param post_id: Post ID.
        :type post_id: str
        :return: :class:`dooray.DoorayObjects.DoorayResponse`
        """

        resp = self._request('POST', f'/project/v1/projects/{project_id}/posts/{post_id}/set-done')

        return dooray.DoorayObjects.DoorayResponse(resp.json())

    # TODO delete post API needed

    # Project > Projects > Posts > Logs
    def create_post_log(self, project_id, post_id, content):
        """
        Add a log to a post.

        :calls: `POST /project/v1/projects/{project-id}/posts/{post-id}/logs \
            <https://helpdesk.dooray.com/share/pages/9wWo-xwiR66BO5LGshgVTg/2939987647631384419>`_
        :param project_id: Project ID.
        :type project_id: str
        :param post_id: Post ID.
        :type post_id: str
        :param content: The content of the log.
        :type content: str
        :return: :class:`dooray.DoorayObjects.DoorayResponse` of :class:`dooray.DoorayObjects.Relation`
        """
        data = {
            'body': {
                'content': content,
                'mimeType': 'text/x-markdown'
            }
        }
        resp = self._request('POST', f'/project/v1/projects/{project_id}/posts/{post_id}/logs', json=data)
        # TODO html support for 'body'

        return dooray.DoorayObjects.DoorayResponse(resp.json(), dooray.DoorayObjects.Relation)

    def get_post_logs(self, project_id, post_id, page=None, size=None, order=None):
        """
        Get logs of a post.

        :calls: `GET /project/v1/projects/{project-id}/posts/{post-id}/logs \
            <https://helpdesk.dooray.com/share/pages/9wWo-xwiR66BO5LGshgVTg/2939987647631384419>`_
        :param project_id: Project ID.
        :type project_id: str
        :param post_id: Post ID.
        :type post_id: str
        :param page: Page number. Starts from 0. Default is 0.
        :type page: int
        :param size: Number of logs per page. Default is 20.
        :type size: int
        :param order: Order of logs. Possible values are 'createdAt' and '-createdAt'. Default is None.
        :type order: str
        :return: :class:`dooray.DoorayObjects.DoorayListResponse` of :class:`dooray.Project.PostLog`
        """
        params = {}
        if page is not None:
            params['page'] = page
        if size is not None:
            params['size'] = size
        if order is not None:
            params['order'] = order

        resp = self._request('GET', f'/project/v1/projects/{project_id}/posts/{post_id}/logs', params=params)

        return dooray.DoorayObjects.DoorayListResponse(resp.json(), dooray.Project.PostLog, page=page, size=size)

    def get_post_log(self, project_id, post_id, log_id):
        """
        Get a log of a post.

        :calls: `GET /project/v1/projects/{project-id}/posts/{post-id}/logs/{log-id} \
            <https://helpdesk.dooray.com/share/pages/9wWo-xwiR66BO5LGshgVTg/2939987647631384419>`_
        :param project_id: Project ID.
        :type project_id: str
        :param post_id: Post ID.
        :type post_id: str
        :param log_id: Log ID.
        :type log_id: str
        :return: :class:`dooray.DoorayObjects.DoorayResponse` of :class:`dooray.Project.PostLog`
        """
        resp = self._request('GET', f'/project/v1/projects/{project_id}/posts/{post_id}/logs/{log_id}')

        return dooray.DoorayObjects.DoorayResponse(resp.json(), dooray.Project.PostLog)

    def update_post_log(self, project_id, post_id, log_id, content):
        """
        Update a log of a post.

        :calls: `PUT /project/v1/projects/{project-id}/posts/{post-id}/logs/{log-id} \
            <https://helpdesk.dooray.com/share/pages/9wWo-xwiR66BO5LGshgVTg/2939987647631384419>`_
        :param project_id: Project ID.
        :type project_id: str
        :param post_id: Post ID.
        :type post_id: str
        :param log_id: Log ID.
        :type log_id: str
        :param content: The content of the log.
        :type content: str
        :return: :class:`dooray.DoorayObjects.DoorayResponse`
        """
        data = {
            'body': {
                'content': content,
                'mimeType': 'text/x-markdown'
            }
        }
        # TODO html support for 'body'
        resp = self._request('PUT', f'/project/v1/projects/{project_id}/posts/{post_id}/logs/{log_id}', json=data)

        return dooray.DoorayObjects.DoorayResponse(resp.json())

    def delete_post_log(self, project_id, post_id, log_id):
        """
        Delete a log of a post.

        :calls: `DELETE /project/v1/projects/{project-id}/posts/{post-id}/logs/{log-id} \
            <https://helpdesk.dooray.com/share/pages/9wWo-xwiR66BO5LGshgVTg/2939987647631384419>`_
        :param project_id: Project ID.
        :type project_id: str
        :param post_id: Post ID.
        :type post_id: str
        :param log_id: Log ID.
        :type log_id: str
        :return: :class:`dooray.DoorayObjects.DoorayResponse`
        """
        resp = self._request('DELETE', f'/project/v1/projects/{project_id}/posts/{post_id}/logs/{log_id}')

        return dooray.DoorayObjects.DoorayResponse(resp.json())
