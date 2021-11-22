class ResponseHeader:
    def __init__(self, data):
        self.is_successful = data['isSuccessful']
        self.result_code = data['resultCode']
        self.result_message = data['resultMessage']

    def __repr__(self):
        return f'{{ result_code: {self.result_code}, result_message: \'{self.result_message}\',' \
               f' is_successful: {self.is_successful} }}'


class DoorayResponse:
    def __init__(self, data):
        self.header = ResponseHeader(data['header'])
        self.result = None

    def __repr__(self):
        return f'{{ header: {self.header}, result: {self.result} }}'


class DoorayListResponse(DoorayResponse):
    def __init__(self, data, obj, page=0, size=20):
        super().__init__(data)
        self.total_count = data['totalCount']
        self.page = page
        self.size = size
        self.result = []
        for e in data['result']:
            self.result.append(obj(e))

    def __repr__(self):
        return f'{{ header: {self.header}, result: {[e for e in self.result]}, ' \
               f'total_count: {self.total_count}, page: {self.page}, size: {self.size} }}'
