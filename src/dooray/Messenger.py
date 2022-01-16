import dooray.DoorayObjects


class Channel:
    def __init__(self, data):
        self.id = data['id']
        """"""
        self.title = data['title']
        """"""
        self.organization = dooray.DoorayObjects.Relation(data['organization'])
        """
        :type: :class:`dooray.DoorayObjects.Relation`
        """
        self.type = data['type']
        """
        The type of the channel. Possible values are `direct`, `private`, `me` and `bot`.
        """
        self.users = Users(data['users'])
        """
        :type: :class:`dooray.Messenger.Users`
        """
        self.me = Me(data['me'])
        """
        :type: :class:`dooray.Messenger.Me`
        """
        self.capacity = data['capacity']
        """"""
        self.status = data['status']
        """
        The status of the channel. Possible values are `system`, `normal`, `archived` and `deleted`.
        """
        self.created_at = data['createdAt']
        """"""
        self.updated_at = data['updatedAt']
        """"""
        self.archived_at = data['archivedAt']
        """"""
        self.displayed = data['displayed']
        """
        :type: bool
        """
        # TODO document says there exists 'role' but it is not. self.role = data['role']

    def __repr__(self):
        return f"{{ 'id': '{self.id}', 'title': '{self.title}', 'organization': '{self.organization}', " \
               f"'type': '{self.type}', 'users': '{self.users}', 'me': '{self.me}', 'capacity': '{self.capacity}', " \
               f"'status': '{self.status}', 'created_at': '{self.created_at}', 'updated_at': '{self.updated_at}', " \
               f"'archived_at': '{self.archived_at}', 'displayed': '{self.displayed}' }}"


class Users:
    def __init__(self, data):
        self.participants = [Participant(e) for e in data['participants']]
        """
        :type: list of :class:`dooray.DoorayObjects.Participant`
        """

    def __repr__(self):
        return f"{{ 'participants': '{self.participants}' }}"


class Participant:
    def __init__(self, data):
        self.type = data['type']
        """
        Type of the participant.
        """
        self.member = OrganizationMember(data['member'])
        """
        :type: :class:`dooray.Messenger.OrganizationMember`
        """

    def __repr__(self):
        return f"{{ 'type': '{self.type}', 'member': '{self.member}' }}"


class Me(Participant):
    def __init__(self, data):
        super().__init__(data)
        self.role = data['role']
        """
        Role of the user in the channel. Possible values are `admin`, `member` and `creator`.
        """

    def __repr__(self):
        return f"{{ 'type': '{self.type}', 'member': '{self.member}', 'role': '{self.role}' }}"


class OrganizationMember:
    def __init__(self, data):
        self.organizationMemberId = data['organizationMemberId']
        """"""

    def __repr__(self):
        return f"{{ 'organizationMemberId': '{self.organizationMemberId}' }}"
