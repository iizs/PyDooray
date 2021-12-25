import dooray.DoorayObjects
from dooray.Member import Member


class Project:
    def __init__(self, data):
        self.id = data['id']
        self.code = data['code']
        self.description = None if 'description' not in data else data['description']
        self.scope = None if 'scope' not in data else data['scope']
        self.state = None if 'state' not in data else data['state']
        self.type = None if 'type' not in data else data['type']
        self.organization = None if 'organization' not in data else dooray.DoorayObjects.Relation(data['organization'])
        self.wiki = None if 'wiki' not in data else dooray.DoorayObjects.Relation(data['wiki'])
        self.drive = None if 'drive' not in data else dooray.DoorayObjects.Relation(data['drive'])
        # { state, type, organization, wiki, drive } are un-documented

    def __repr__(self):
        return f"{{ 'id': '{self.id}', 'code': '{self.code}', 'description': '{self.description}', " \
               f"'state': '{self.state}', 'type': '{self.type}', 'scope': '{self.scope}', " \
               f"'organization': '{self.organization}', 'wiki': '{self.wiki}', 'drive': {self.drive} }}"


class DisplayName:
    def __init__(self, data):
        self.locale = data['locale']
        self.name = data['name']

    def __repr__(self):
        return f"{{ 'locale': '{self.locale}', 'name': '{self.name}' }}"


class Workflow:
    def __init__(self, data):
        self.id = data['id']
        self.name = data['name']
        self.order = data['order']
        self.workflow_class = data['class']
        self.names = []
        for e in data['names']:
            self.names.append(DisplayName(e))

    def __repr__(self):
        return f"{{ 'id': '{self.id}', 'name': '{self.name}', 'order': '{self.order}', " \
               f"'workflow_class': '{self.workflow_class}', 'names': '{[e for e in self.names]}' }}"


class EmailAddress:
    def __init__(self, data):
        self.id = data['id']
        self.name = data['name']
        self.email_address = data['emailAddress']

    def __repr__(self):
        return f"{{ 'id': '{self.id}', 'name': '{self.name}', 'email_address': '{self.email_address}' }}"


class Tag:
    def __init__(self, data):
        self.id = data['id']
        self.name = data['name']
        self.color = data['color']

    def __repr__(self):
        return f"{{ 'id': '{self.id}', 'name': '{self.name}', 'color': '{self.color}' }}"


class Milestone:
    def __init__(self, data):
        self.id = data['id']
        self.name = data['name']
        self.status = data['status']
        # Milestone without a period do not return 'startedAt' and 'endAt' field.
        self.started_at = data['startedAt'] if 'startedAt' in data else None
        self.ended_at = data['endedAt'] if 'endedAt' in data else None
        self.closed_at = data['closedAt']
        self.created_at = data['createdAt']
        self.updated_at = data['updatedAt']

    def __repr__(self):
        return f"{{ 'id': '{self.id}', 'name': '{self.name}', 'status': '{self.status}', " \
               f"'started_at': '{self.started_at}', 'ended_at': '{self.ended_at}', " \
               f"'closed_at': '{self.closed_at}', 'created_at': '{self.created_at}', " \
               f"'updated_at': '{self.updated_at}'}}"


class ProjectMember:
    def __init__(self, data):
        self.organizationMemberId = data['organizationMemberId']
        self.role = data['role']

    def __repr__(self):
        return f"{{ 'organizationMemberId': '{self.organizationMemberId}', 'role': '{self.role}' }}"


class MemberGroup:
    def __init__(self, data):
        self.id = data['id']
        self.code = data['code']
        self.created_at = data['createdAt']
        self.updated_at = data['updatedAt']
        self.project = Project(data['project'])
        if 'members' in data:
            self.members = [MemberGroupMember(e) for e in data['members']]

    def __repr__(self):
        return f"{{ 'id': '{self.id}', 'code': '{self.code}', " \
               f"'created_at': '{self.created_at}', 'updated_at': '{self.updated_at}', " \
               f"'project': '{self.project}', 'members': {self.members} }}"


class MemberGroupMember:
    def __init__(self, data):
        self.organization_member = Member(data)

    def __repr__(self):
        return f"{self.organization_member}"

