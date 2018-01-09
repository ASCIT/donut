
import flask
blueprint = flask.Blueprint(
    'committee_sites', __name__, template_folder='templates')

import donut.modules.committee_sites.routes

