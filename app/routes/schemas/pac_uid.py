from dataclasses import field
from marshmallow_dataclass import dataclass

# imports from other parts of this app
from validators.exists_pac import ExistsPACValidator


@dataclass
class PACId:
    """The UID by which a PAC is stored and referenced in Memory"""
    uid: str = field(metadata={
        'required': True,
        'validate': ExistsPACValidator("PAC with this UID does not exist."),
    })
