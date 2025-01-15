import time
import uuid
from dataclasses import field
from marshmallow_dataclass import dataclass


@dataclass
class ShortPac:
    """Class representing everything except the PAC content. Used when Listing PACs."""
    uid: str = field(metadata={"description": "Unique identifier for the PAC"})
    added_time: float = field(metadata={"description": "Timestamp when the PAC was added"})


@dataclass
class PAC:
    """Class representing a PAC file as stored on the server in memory"""
    uid: str = field(metadata={"description": "Unique identifier for the PAC"})
    added_time: float = field(metadata={"description": "Timestamp when the PAC was added"})
    content: str = field(metadata={"description": "Unique identifier for the PAC"})

    def __init__(self, uid: str, content: str, added_time: float):
        self.uid = uid
        self.content = content
        self.added_time = added_time

    @staticmethod
    def new_pac(content):
        new_id = uuid.uuid4()
        now = time.time()

        return PAC(uid=str(new_id), content=content, added_time=now)

    def simple(self) -> ShortPac:
        return ShortPac(
            uid=self.uid,
            added_time=self.added_time
        )
