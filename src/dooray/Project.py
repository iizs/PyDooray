import dooray.DoorayObjects


class Project:
    def __init__(self, data):
        self.id = data['id']
        self.code = data['code']
        self.description = data['description']
        self.scope = data['scope']
        self.state = data['state']
        self.type = data['type']
        self.organization = dooray.DoorayObjects.Relation(data['organization'])
        self.wiki = dooray.DoorayObjects.Relation(data['wiki'])
        self.drive = dooray.DoorayObjects.Relation(data['drive'])
        # { state, type, organization, wiki, drive } are un-documented

    def __repr__(self):
        return f"{{ 'id': '{self.id}', 'code': '{self.code}', 'description': '{self.description}', " \
               f"'state': '{self.state}', 'type': '{self.type}', 'scope': '{self.scope}', " \
               f"'organization': {self.organization}, 'wiki': {self.wiki},'drive': {self.drive} }}"


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
