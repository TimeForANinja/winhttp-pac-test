from apiflask import Schema
from apiflask.fields import String
from apiflask.validators import OneOf

# TODO: make sure output is defined for all routes
class GenericOutput(Schema):
    """Every Output Schema should inherit from this class."""
    status = String(required=True, validate=OneOf(["success", "failed"]),
                    metadata={"description": "Status of the response, e.g., 'success'"})
