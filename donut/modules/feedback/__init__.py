import flask
blueprint = flask.Blueprint(
    'feedback', __name__, template_folder='templates')

import donut.modules.feedback.routes
