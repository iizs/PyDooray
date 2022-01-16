class Member:
    def __init__(self, data):
        self.id = data['id']
        """"""
        self.name = data['name']
        """"""
        self.user_code = data['userCode'] if 'userCode' in data else None
        """"""
        self.external_email_address = data['externalEmailAddress'] if 'externalEmailAddress' in data else None
        """"""

    def __repr__(self):
        return f"{{ 'id': '{self.id}', 'name': '{self.name}', 'user_code': '{self.user_code}', " \
               f"'external_email_address': '{self.external_email_address}' }}"
