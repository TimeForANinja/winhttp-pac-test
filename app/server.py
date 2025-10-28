from apiflask import APIFlask
from werkzeug.middleware.proxy_fix import ProxyFix

from pac_storage import init_store

# create flask app
app = APIFlask(__name__, "PAC Test Server", version="1.0.0", docs_path="/docs")

# load env variables into app.config
app.config.from_prefixed_env(prefix='APP')

# allow swagger to be served offline
app.config['SWAGGER_UI_CSS'] = 'static/css/swagger-ui.css'
app.config['SWAGGER_UI_BUNDLE_JS'] = 'static/js/swagger-ui-bundle.js'
app.config['SWAGGER_UI_STANDALONE_PRESET_JS'] = 'static/js/swagger-ui-standalone-preset.js'

# fix for src_ip if used behind a reverse proxy
if app.config.get('PROXY_FIX', 'false').lower() == 'true':
    app.wsgi_app = ProxyFix(app.wsgi_app, x_for=1, x_proto=1, x_host=1, x_prefix=1)

# init pac store
init_store(app)

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
