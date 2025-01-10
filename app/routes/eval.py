from dataclasses import field
from apiflask import APIFlask
from apiflask.validators import Length
from marshmallow_dataclass import dataclass

# imports from other parts of this app
from classes.eval_data import EvalData, EvalResponse
from classes.pac import PAC
from pac_engines import call_engines
from pac_storage import get_pac, add_pac
from routes.schemas.pac_uid import PACId
from validators.url import IPValidator, HostnameValidator


@dataclass
class EvalInput:
    dest_host: str = field(metadata={
        "required": True,
        "validate": HostnameValidator('"dest_host" must be a valid URL'),
        "description": "The destination host URL",
    })
    src_ip: str = field(metadata={
        "required": True,
        "validate": IPValidator('"src_ip" must be a valid URL'),
        "description": "The source IP URL",
    })


@dataclass
class EvalWithPacInput(EvalInput):
    content: str = field(metadata={
        "required": True,
        "validate": Length(min=1),
        "description": "The content of the PAC"
    })


def register_eval_routes(app: APIFlask):
    @app.post('/api/v1/eval')
    @app.doc(tags=['Eval'], summary='Evaluate PAC', description='Evaluate a PAC')
    @app.input(EvalWithPacInput.Schema, location='json', arg_name="eval_data")
    @app.output(EvalResponse.Schema)
    def r_evaluate_after_adding_pac_function(eval_data: EvalWithPacInput):
        pac = PAC.new_pac(eval_data.content)
        add_pac(pac)

        ed = EvalData(pac, eval_data.dest_host, eval_data.src_ip)
        result = call_engines(ed)
        return result


    @app.post('/api/v1/eval/<string:uid>')
    @app.doc(tags=['Eval'], summary='Evaluate PAC by UID', description='Evaluate a PAC by UID')
    @app.input(PACId.Schema, location='path', arg_name="pid")
    @app.input(EvalInput.Schema, location='json', arg_name="eval_data")
    @app.output(EvalResponse.Schema)
    def r_evaluate_by_uid_function(pid: PACId, uid: str, eval_data: EvalInput):
        pac = get_pac(pid.uid)

        ed = EvalData(pac, eval_data.dest_host, eval_data.src_ip)
        result = call_engines(ed)
        return result
