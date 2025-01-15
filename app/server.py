# create flask app
from apiflask import APIFlask
app = APIFlask(__name__, "PAC Test Server", version="1.0.0", docs_path="/docs")

# add routes
from routes.other import register_other_routes
register_other_routes(app)
from routes.pac import register_pac_routes
register_pac_routes(app)
from routes.eval import register_eval_routes
register_eval_routes(app)

# add "status" and "status_code" fields to the default flask errors
@app.error_processor
def handle_error(error):
    return {
        'status': 'failed',
        'status_code': error.status_code,
        'message': error.message,
        'detail': error.detail
    }, error.status_code, error.headers


if __name__ == '__main__':
    # start flask app server
    app.run(port=8080, host="0.0.0.0")
