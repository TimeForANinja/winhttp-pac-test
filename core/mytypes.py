import uuid
import time


# In-memory storage for PAC files
class PAC:
    def __init__(self, id, content, added_time):
        self.id = id
        self.content = content
        self.added_time = added_time

    @staticmethod
    def new_pac(content):
        new_id = uuid.uuid4()
        now = time.time()

        return PAC(id=new_id, content=content, added_time=now)

    def simple(self) -> dict:
        return {
            "id": self.id,
            "added_time": self.added_time
        }
    def full(self) -> dict:
        return {
            "id": self.id,
            "content": self.content,
            "added_time": self.added_time
        }

class EvalData:
    def __init__(self, pac: PAC, dest_url: str, src_ip: str):
        self.pac = pac
        self.dest_url = dest_url
        self.src_ip = src_ip

    def full(self) -> dict:
        return {
            "pac": self.pac.full(),
            "dest_url": self.dest_url,
            "src_ip": self.src_ip,
        }

    def engine_payload(self) -> dict:
        return {
            "dest_url": self.dest_url,
            "src_ip": self.src_ip,
            "pac_url": f"http://127.0.0.1:8080/pac/{self.pac.id}",
            "pac_content": self.pac.content,
        }

class EvalResponse:
    def __init__(self, eval_data: EvalData):
        self.eval_data = eval_data
        self.success = False
        self.message = "sth. went wrong"
        self.engines = []

    def set_status(self, success: bool, message: str):
        self.success = success
        self.message = message

    def register_engine(self, engineName: str, engine: dict, success: bool):
        self.engines.append({
            "engine": engineName,
            "data": engine,
            "success": success,
        })

    def full(self) -> dict:
        return self.eval_data.full() | {
            "success": "success" if self.success else "failed",
            "message": self.message,
            "results": self.engines,
        }
