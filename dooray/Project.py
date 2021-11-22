class Project:
    def __init__(self, data):
        self.id = data['id']
        self.code = data['code']
        self.description = data['description']
        self.scope = data['scope']
        self.state = data['state']
        self.type = data['type']
        self.organization = {'id': data['organization']['id']}
        self.wiki = {'id': data['wiki']['id']}
        self.drive = {'id': data['drive']['id']}

    def __repr__(self):
        return f"{{ 'id': '{self.id}', 'code': '{self.code}', 'description': '{self.description}', " \
               f"'state': '{self.state}', 'type': '{self.type}', 'scope': '{self.scope}', " \
               f"'organization': {self.organization}, 'wiki': {self.wiki},'drive': {self.drive} }}"
