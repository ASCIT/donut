import flask
blueprint = flask.Blueprint(
    'marketplace', __name__, template_folder='templates')

import donut.modules.marketplace.routes
