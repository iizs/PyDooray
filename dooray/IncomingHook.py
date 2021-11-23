import dooray.DoorayObjects


class IncomingHook:
    def __init__(self, data):
        self.id = data['id']
        self.name = data['name']
        self.service_type = data['serviceType']
        self.url = data['url']
        self.projects = []
        for e in data['projects']:
            self.projects.append(dooray.DoorayObjects.Relation(e))
        # TODO There exists unknown property, 'channels': []. Need to wait for the update of API document

    def __repr__(self):
        return f"{{ 'id': '{self.id}', 'name': '{self.name}', 'service_type': '{self.service_type}', " \
               f"'url': '{self.url}', 'projects': {[e for e in self.projects]} }}"
