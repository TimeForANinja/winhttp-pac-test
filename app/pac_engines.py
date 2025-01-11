from concurrent.futures import ThreadPoolExecutor, as_completed
import requests

# imports from other parts of this app
from classes.eval_data import EvalData, EvalResponse, EngineResult

FLAG_EVALUATION = "evaluation"
FLAG_VALIDATION = "validation"
FLAG_SRC_IP = "src_ip"

# List of known "pac-engines"
engines = [
    # for some reason using localhost adds nearly 2 seconds to the request time...
    # so make sure to stick with 127.0.0.1...
    # https://stackoverflow.com/a/50565643
    {"name": "v8", "url": "http://127.0.0.1:8081/", "flags": [FLAG_EVALUATION, FLAG_SRC_IP]},
    {"name": "winhttp", "url": "http://127.0.0.1:8082/", "flags": [FLAG_EVALUATION]},
    {"name": "eslint", "url": "http://127.0.0.1:8083/", "flags": [FLAG_VALIDATION]},
]


def call_engines(data: EvalData) -> EvalResponse:
    eval_resp = EvalResponse(data)

    # According to ChatGPT, this does the requests to the engines in parallel
    with ThreadPoolExecutor() as executor:
        future_to_engine = {
            executor.submit(process_engine, engine, data.engine_payload()): engine
            for engine
            in engines
        }

        for future in as_completed(future_to_engine):
            engine_result = future.result()
            eval_resp.register_engine(engine_result)

    return eval_resp


def process_engine(engine: dict, engine_payload: dict) -> EngineResult:
    engine_name = engine["name"]
    engine_flags = engine.get("flags", [])

    try:
        res = requests.post(
            engine["url"],
            json=engine_payload,
            timeout=5
        )

        if res.status_code == 200:
            return EngineResult(
                engine=engine_name,
                status="success",
                proxy=res.json().get("proxy", "<undefined>"),
                flags=engine_flags,
            )
        else:
            try:
                body=res.json()
                return EngineResult(
                    engine=engine_name,
                    status="failed",
                    error=body.get("error", ""), # "Unknown Error"),
                    error_code=body.get("error_code", 1),
                    message=body.get("message", "No Message"),
                    flags=engine_flags
                )
            except ValueError:
                return EngineResult(
                    engine=engine_name,
                    status="failed",
                    message=f"Engine responded with status {res.status_code}, and response is not a JSON",
                    error=res.text,
                    error_code=res.status_code,
                    flags=engine_flags
                )
    except requests.exceptions.Timeout:
        return EngineResult(
            engine=engine_name,
            status="failed",
            error="Request to engine timed out",
            error_code=500,
            flags=engine_flags
        )
    except requests.exceptions.RequestException as e:
        return EngineResult(
            engine=engine_name,
            status="failed",
            error="Request to engine failed",
            message=str(e),
            error_code=400,
            flags=engine_flags
        )
