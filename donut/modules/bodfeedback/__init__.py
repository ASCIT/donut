import flask
blueprint = flask.Blueprint(
    'bodfeedback', __name__, template_folder='templates')

import donut.modules.bodfeedback.routes
