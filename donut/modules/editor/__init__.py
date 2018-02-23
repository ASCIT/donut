import flask
blueprint = flask.Blueprint('editor', __name__, template_folder='templates', static_folder='static', static_url_path='/donut/modules/editor/static')

import donut.modules.editor.routes
