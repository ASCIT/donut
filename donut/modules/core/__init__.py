import flask
blueprint = flask.Blueprint('core', __name__, template_folder='templates')

import donut.modules.core.routes
