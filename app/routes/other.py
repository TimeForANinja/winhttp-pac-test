from apiflask import APIFlask

# imports from other parts of this app
from routes.schemas.generic_output import GenericOutput


def register_other_routes(app: APIFlask):
    @app.get('/up')
    @app.doc(summary="Check if the server is up", description="Check if the server is up")
    @app.output(GenericOutput)
    def r_up():
        return {"status": "success"}
