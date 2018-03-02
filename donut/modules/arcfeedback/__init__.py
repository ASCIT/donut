import flask
blueprint = flask.Blueprint(
    'arcfeedback', __name__, template_folder='templates')

import donut.modules.arcfeedback.routes
