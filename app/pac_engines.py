import requests

# imports from other parts of this app
from classes.eval_data import EvalData, EvalResponse, EngineResult

FLAG_EVALUATION = "evaluation"
FLAG_VALIDATION = "validation"
FLAG_SRC_IP = "src_ip"

# List of known "pac-engines"
engines = [
    {"name": "v8", "url": "http://localhost:8081/", "flags": [FLAG_EVALUATION, FLAG_VALIDATION, FLAG_SRC_IP]},
    {"name": "winhttp", "url": "http://localhost:8082/", "flags": [FLAG_EVALUATION, FLAG_VALIDATION]},
    {"name": "eslint", "url": "http://localhost:8083/", "flags": [FLAG_VALIDATION]},
]


def call_engines(data: EvalData) -> EvalResponse:
    eval_resp = EvalResponse(data)

    for engine in engines:
        engine_name = engine["name"]
        engine_flags = engine.get("flags", [])

        try:
            res = requests.post(
                engine["url"],
                json=data.engine_payload(),
                timeout=5
            )

            if res.status_code == 200:
                eval_resp.register_engine(EngineResult(
                    engine=engine_name,
                    success="success",
                    proxy=res.json().get("proxy", "<undefined>"),
                    flags=engine_flags,
                ))
            else:
                try:
                    body=res.json()
                    eval_resp.register_engine(EngineResult(
                        engine=engine_name,
                        success="failed",
                        error=body.get("error", ""), # "Unknown Error"),
                        error_code=body.get("error_code", 1),
                        message=body.get("message", "No Message"),
                        flags=engine_flags
                    ))
                except ValueError:
                    eval_resp.register_engine(EngineResult(
                        engine=engine_name,
                        success="failed",
                        message=f"Engine responded with status {res.status_code}, and response is not a JSON",
                        error=res.text,
                        error_code=res.status_code,
                        flags=engine_flags
                    ))
        except requests.exceptions.Timeout:
            eval_resp.register_engine(EngineResult(
                engine=engine_name,
                success="failed",
                error="Request to engine timed out",
                error_code=500,
                flags=engine_flags
            ))
        except requests.exceptions.RequestException as e:
            eval_resp.register_engine(EngineResult(
                engine=engine_name,
                success="failed",
                error="Request to engine failed",
                message=str(e),
                error_code=400,
                flags=engine_flags
            ))

    return eval_resp
