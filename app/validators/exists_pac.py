from apiflask.validators import Validator
from marshmallow import ValidationError

# imports from other parts of this app
from pac_storage import has_pac


class ExistsPACValidator(Validator):
    """Validator to check if a PAC exists in the in-memory storage."""
    def __init__(self, message=None):
        if message is None:
            message = "The specified resource does not exist."
        self.message = message

    def __call__(self, value):
        # Custom logic to check if the PAC exists
        if not has_pac(value):
            raise ValidationError(self.message)
