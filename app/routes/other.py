from apiflask import APIFlask
from flask import send_from_directory

# imports from other parts of this app
from routes.schemas.generic_output import GenericOutput


def register_other_routes(app: APIFlask):
    @app.get('/')
    @app.doc(summary="Serve the index page", description="Serve the \"home\"-page")
    def serve_index():
        return send_from_directory('routes', 'index.html')

    @app.get('/up')
    @app.doc(summary="Check if the server is up", description="Endpoint that can be used to check if the server is up. It always returns a simple \"success\" message.")
    @app.output(GenericOutput)
    def r_up():
        return {"status": "success"}
