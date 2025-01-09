from urllib.parse import urlparse
from apiflask.validators import Validator
from marshmallow import ValidationError


class URLValidator(Validator):
    def __init__(self, message=None):
        if message is None:
            message = "The string is not a valid URL."
        self.message = message

    def __call__(self, value):
        try:
            parsed = urlparse(value)
            # Check scheme and hostname
            if not parsed.scheme or not parsed.netloc:
                raise ValidationError(self.message)
            return
        except Exception:
            raise ValidationError(self.message)
