class ResponseHeader:
    def __init__(self, data):
        self.is_successful = data['isSuccessful']
        """
        Tell if the request was successful or not.
        
        :type: bool
        """
        self.result_code = data['resultCode']
        """
        The result code of the request.
        
        :type: int
        """
        self.result_message = data['resultMessage']
        """
        The result message of the request.
        
        :type: str
        """

    def __repr__(self):
        return f"{{ 'result_code': {self.result_code}, 'result_message': '{self.result_message}'," \
               f"'is_successful': {self.is_successful} }}"


class DoorayResponse:
    """
    The response of the request. It contains the response header and the response result.
    The type of the `result` differs by the request.

    For example, :class:`dooray.DoorayMessenger.create_channel` returns this object with
    the `result` of :class:`dooray.DoorayObjects.Relation` object.
    Therefore, you can access the response result like this:

    Example::

        import dooray

        d = dooray.Dooray(API_TOKEN)
        response = d.messenger.create_channel(title='test', ...)
        channel_id = response.result.id
    """
    def __init__(self, data, obj=None):
        self.header = ResponseHeader(data['header'])
        """
        The header of the response.
        
        :type: :class:`dooray.DoorayObjects.ResponseHeader`
        """
        if obj is not None:
            self.result = obj(data['result'])
            """
            The result of the response.
            
            :type: Differs by the request.
            """

    def __repr__(self):
        return f"{{ 'header': {self.header}, 'result': {self.result} }}"


class DoorayListResponse(DoorayResponse):
    """
    The list response of the request. It contains the response header and the response result.
    The type of the `result` is a list of objects which differ by the request.
    In addition, the pagination information like `total_count`, `page` and `size` is also included.

    For example, :class:`dooray.DoorayMessenger.get_channels` returns this object with
    the `result` as the list of :class:`dooray.Messenger.Channel` object.
    Therefore, you can access the response result like this:

    Example::

        import dooray

        d = dooray.Dooray(API_TOKEN)
        response = d.messenger.get_channels( ... )
        for channel in response.result:
            print(channel.title)
    """
    def __init__(self, data, obj, page=0, size=20):
        super().__init__(data)
        self.total_count = data['totalCount']
        """
        The total count of the response.
        
        :type: int
        """
        self.page = page
        """
        The page number of the response. Starts from 0.
        
        :type: int
        """
        self.size = size
        """
        The size of the response.

        :type: int
        """
        self.result = []
        """
        The result of the response in list form.
        
        :type: list of response objects which differ by the request.
        """
        for e in data['result']:
            self.result.append(obj(e))
        if self.size is None:
            self.page = 0
            self.size = self.total_count

    def __repr__(self):
        return f"{{ 'header': {self.header}, 'result': {[e for e in self.result]}, " \
               f"'total_count': {self.total_count}, 'page': {self.page}, 'size': {self.size} }}"


class Relation:
    def __init__(self, data):
        self.id = data['id']
        """
        The id from the result.
        """

    def __repr__(self):
        return f"{{ 'id': '{self.id}' }}"
