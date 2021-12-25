class DoorayException(Exception):
    """
    This class is the base of all exceptions raised by PyDooray.
    """
    pass


class BadHttpResponseStatusCode(DoorayException):
    def __init__(self, resp):
        self.message = f'Server has returned HTTP Response Status Code {resp.status_code}'


class ServerGeneralError(DoorayException):
    def __init__(self, resp):
        self.message = f"Server has returned 'SERVER_GENERAL_ERROR'"
