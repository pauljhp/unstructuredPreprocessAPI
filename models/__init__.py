from .request_params import PdfProcessRequestContainer


class User:
    def __init__(self, username: str, password: str = None):
        self.username = username
        self.password = password
