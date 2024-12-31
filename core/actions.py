import requests
import collections

import .mytypes

pac_store = collections.deque(maxlen=100)

def has_pac(uid: str) -> bool:
    return any(pac.id == uid for pac in pac_store)

def get_pac(uid: str) -> mytypes.PAC:
    for pac in pac_store:
        if pac.id == uid:
            return pac
    raise KeyError(f"PAC with UID {uid} not found")

def add_pac(pac: mytypes.PAC):
    for existing in pac_store:
        if existing.id == pac.id:
            pac_store.remove(existing)
            break
    pac_store.append(pac)

def list_pac() -> list[dict]:
    return [pac.simple() for pac in pac_store]


# Map of known "pac-engines"
engines = {
    "v8": "http://localhost:8081/",
    "winhttp": "http://localhost:8082/"
}

def eval_pac(data: mytypes.EvalData) -> mytypes.EvalResponse:
    eval_resp = mytypes.EvalResponse(data)

    for engine_name, engine_url in engines.items():
        try:
            res = requests.post(
                engine_url,
                json=data.engine_payload(),
                timeout=5
            )

            if res.status_code == 200:
                eval_resp.register_engine(engine_name, res.json(), True)
            else:
                try:
                    eval_resp.register_engine(engine_name, res.json(), False)
                except ValueError:
                    eval_resp.register_engine(engine_name, {
                        "status": "failed",
                        "message": f"Engine responded with status {res.status_code}, and response is not a JSON",
                        "error": res.text,
                        "error_code": res.status_code
                    }, False)
        except requests.exceptions.Timeout:
            eval_resp.register_engine(engine_name, {
                "status": "failed",
                "error": "Request to engine timed out",
                "error_code": 400,
            }, False)
        except requests.exceptions.RequestException as e:
            eval_resp.register_engine(engine_name, {
                "status": "failed",
                "error": "Request to engine failed",
                "message": str(e),
                "error_code": 400,
            }, False)

    return eval_resp
