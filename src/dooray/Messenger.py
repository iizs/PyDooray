import dooray.DoorayObjects


class Channel:
    def __init__(self, data):
        self.id = data['id']
        self.title = data['title']
        self.organization = dooray.DoorayObjects.Relation(data['organization'])
        self.type = data['type']
        self.users = Users(data['users'])
        self.me = Me(data['me'])
        self.capacity = data['capacity']
        self.status = data['status']
        self.created_at = data['createdAt']
        self.updated_at = data['updatedAt']
        self.archived_at = data['archivedAt']
        self.displayed = data['displayed']
        # TODO document says there exists 'role' but it is not. self.role = data['role']

    def __repr__(self):
        return f"{{ 'id': '{self.id}', 'title': '{self.title}', 'organization': '{self.organization}', " \
               f"'type': '{self.type}', 'users': '{self.users}', 'me': '{self.me}', 'capacity': '{self.capacity}', " \
               f"'status': '{self.status}', 'created_at': '{self.created_at}', 'updated_at': '{self.updated_at}', " \
               f"'archived_at': '{self.archived_at}', 'displayed': '{self.displayed}' }}"


class Users:
    def __init__(self, data):
        self.participants = [ Participants(e) for e in data['participants'] ]

    def __repr__(self):
        return f"{{ 'participants': '{self.participants}' }}"


class Participants:
    def __init__(self, data):
        self.type = data['type']
        self.member = Member(data['member'])

    def __repr__(self):
        return f"{{ 'type': '{self.type}', 'member': '{self.member}' }}"


class Me(Participants):
    def __init__(self, data):
        super().__init__(data)
        self.role = data['role']

    def __repr__(self):
        return f"{{ 'type': '{self.type}', 'member': '{self.member}', 'role': '{self.role}' }}"


class Member:
    def __init__(self, data):
        self.organizationMemberId = data['organizationMemberId']

    def __repr__(self):
        return f"{{ 'organizationMemberId': '{self.organizationMemberId}' }}"
