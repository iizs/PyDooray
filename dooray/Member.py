class Member:
    def __init__(self, data):
        self.id = data['id']
        self.name = data['name']
        self.user_code = data['userCode']
        self.external_email_address = data['externalEmailAddress']

    def __repr__(self):
        return f"{{ 'id': '{self.id}', 'name': '{self.name}', 'user_code': '{self.user_code}', " \
               f"'external_email_address': '{self.external_email_address}' }}"
