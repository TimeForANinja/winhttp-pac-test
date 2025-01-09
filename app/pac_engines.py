import requests

# imports from other parts of this app
from classes.eval_data import EvalData, EvalResponse, EngineResult

# Map of known "pac-engines"
engines = {
    "v8": "http://localhost:8081/",
    "winhttp": "http://localhost:8082/",
    "eslint": "http://localhost:8083/",
}


def call_engines(data: EvalData) -> EvalResponse:
    eval_resp = EvalResponse(data)

    for engine_name, engine_url in engines.items():
        try:
            res = requests.post(
                engine_url,
                json=data.engine_payload(),
                timeout=5
            )

            if res.status_code == 200:
                eval_resp.register_engine(EngineResult(
                    engine=engine_name,
                    success="success",
                    response=res.json(),
                ))
            else:
                try:
                    body=res.json()
                    eval_resp.register_engine(EngineResult(
                        engine=engine_name,
                        success="failed",
                        error=body.error,
                        error_code=body.error_code,
                        message=body.message
                    ))
                except ValueError:
                    eval_resp.register_engine(EngineResult(
                        engine=engine_name,
                        success="failed",
                        message=f"Engine responded with status {res.status_code}, and response is not a JSON",
                        error=res.text,
                        error_code=res.status_code
                    ))
        except requests.exceptions.Timeout:
            eval_resp.register_engine(EngineResult(
                engine=engine_name,
                success="failed",
                error="Request to engine timed out",
                error_code=500
            ))
        except requests.exceptions.RequestException as e:
            eval_resp.register_engine(EngineResult(
                engine=engine_name,
                success="failed",
                error="Request to engine failed",
                message=str(e),
                error_code=400
            ))

    return eval_resp
