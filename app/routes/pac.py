from dataclasses import field
from apiflask import APIFlask, Schema, abort
from apiflask.fields import String, List, Nested
from apiflask.validators import Length, OneOf
from marshmallow_dataclass import dataclass

# imports from other parts of this app
from classes.pac import PAC, ShortPac
from pac_storage import has_pac, list_pac, add_pac, get_pac
from routes.schemas.pac_uid import PACId


@dataclass
class InputCreatePAC:
    """Input for creating a new PAC."""
    content: str = field(
        metadata={
            'required': True,
            "validate": Length(min=1),
            "description": "The content of the PAC"
        }
    )

class GenericOutput(Schema):
    status = String(required=True, validate=OneOf(["success", "failed"]),
                    metadata={"description": "Status of the response, e.g., 'success'"})

class PacListOutput(GenericOutput):
    """Output for listing all PACs."""
    pacs = List(Nested(ShortPac.Schema), required=True, description="List of PACs")

class PacDetailsOutput(GenericOutput):
    """Output for getting a single PAC, including the Content."""
    pac = Nested(PAC.Schema, required=True, metadata={"description": "Status of the response, e.g., 'success'"})

def register_pac_routes(app: APIFlask):
    @app.get('/api/v1/pac')
    @app.doc(tags=['PAC'], summary='List all PACs', description='List all PACs in the database')
    @app.output(PacListOutput)
    def r_list_all_pacs():
        return {"status": "success", "pacs": list_pac()}

    @app.get('/api/v1/pac/<string:uid>')
    @app.doc(tags=['PAC'], summary='Get PAC by UID', description='Get PAC by UID')
    @app.input(PACId.Schema, location='path', arg_name="pid")
    @app.output(PacDetailsOutput)
    def r_get_pac(pid: PACId, uid: str):
        if not has_pac(pid.uid):
            return abort(404, "PAC not found")
        return {"status": "success", "pac": get_pac(pid.uid)}

    @app.get('/pac/<string:uid>')
    @app.doc(tags=['PAC'], summary='Get PAC Content by UID', description='Get PAC by UID. This Endpoints also sets the Content-Type to "application/x-ns-proxy-autoconfig" as expected for a PAC.')
    @app.input(PACId.Schema, location='path', arg_name="pid")
    def r_get_pac_content(pid: PACId, uid: str):
        if not has_pac(pid.uid):
            return abort(404, "PAC not found")
        return get_pac(pid.uid).content, 200, {'Content-Type': 'application/x-ns-proxy-autoconfig'}

    @app.post('/api/v1/pac')
    @app.doc(tags=['PAC'], summary='Add PAC', description='Add a new PAC to the database.')
    @app.input(InputCreatePAC.Schema, arg_name='pac_data')
    @app.output(PacDetailsOutput)
    def r_add_pac(pac_data: InputCreatePAC):
        if not pac_data.content:
            return abort(400, "The 'content' field is required")
        pac = PAC.new_pac(pac_data.content)
        add_pac(pac)
        return {"status": "success", "pac": pac}
