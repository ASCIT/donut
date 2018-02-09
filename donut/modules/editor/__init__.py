import flask
blueprint = flask.Blueprint('editor', __name__, template_folder='templates')

import donut.modules.editor.routes
