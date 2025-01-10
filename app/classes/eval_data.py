from dataclasses import field
from typing import List, Optional
from apiflask.validators import OneOf
from marshmallow import post_dump
from marshmallow_dataclass import dataclass

# imports from other parts of this app
from classes.pac import PAC


@dataclass
class EvalData:
    pac: PAC
    dest_host: str
    src_ip: str

    def __init__(self, pac: PAC, dest_host: str, src_ip: str):
        self.pac = pac
        self.dest_host = dest_host
        self.src_ip = src_ip

    def simple(self) -> dict:
        return {
            "pac": self.pac.uid,
            "src_ip": self.src_ip,
            "dest_host": self.dest_host,
        }

    def engine_payload(self) -> dict:
        return {
            "pac": {
                "uid": self.pac.uid,
                "url": f"http://127.0.0.1:8080/pac/{self.pac.uid}",
                "content": self.pac.content,
            },
            "src_ip": self.src_ip,
            "dest_host": self.dest_host,
        }

@dataclass
class EngineResult:
    engine: str
    status: str = field(metadata={
        "required": True,
        "validate": OneOf(["success", "failed"]),
    })
    flags: List[str] = field(default_factory=list)
    error_code: Optional[int] = None
    error: Optional[str] = field(default="")
    message: Optional[str] = field(default="")
    proxy: Optional[str] = field(default="")

    @post_dump
    def remove_skip_values(self, data, **kwargs):
        # remove all fields of type None or "" from the exported json
        return {
            key: value for key, value in data.items()
            if value not in [None, ""]
        }


@dataclass
class EvalResponse:
    request: EvalData
    status: str = field(default="success")
    results: List[EngineResult] = field(default_factory=list)

    def __init__(self, eval_data: EvalData):
        self.request = eval_data
        self.results = []

    def register_engine(self, er: EngineResult):
        self.results.append(er)
