from dataclasses import field
from typing import List, Optional
from apiflask.validators import OneOf
from marshmallow_dataclass import dataclass

# imports from other parts of this app
from classes.pac import PAC


@dataclass
class EvalData:
    pac: PAC
    dest_url: str
    src_ip: str

    def __init__(self, pac: PAC, dest_url: str, src_ip: str):
        self.pac = pac
        self.dest_url = dest_url
        self.src_ip = src_ip

    def simple(self) -> dict:
        return {
            "pac": self.pac.uid,
            "src_ip": self.src_ip,
            "dest_url": self.dest_url,
        }

    def engine_payload(self) -> dict:
        return {
            "pac": {
                "uid": self.pac.uid,
                "url": f"http://127.0.0.1:8080/pac/{self.pac.uid}",
                "content": self.pac.content,
            },
            "src_ip": self.src_ip,
            "dest_url": self.dest_url,
        }

@dataclass
class EngineResult:
    engine: str
    success: str = field(metadata={
        "required": True,
        "validate": OneOf(["success", "failed"]),
    })
    error_code: Optional[int] = None
    error: Optional[str] = field(default="")
    message: Optional[str] = field(default="")
    response: Optional[dict] = field(default_factory=dict)

@dataclass
class EvalResponse:
    request: EvalData
    success: str = field(default="success")
    results: List[EngineResult] = field(default_factory=list)

    def __init__(self, eval_data: EvalData):
        self.request = eval_data

    def register_engine(self, er: EngineResult):
        self.results.append(er)
