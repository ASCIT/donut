
import flask
blueprint = flask.Blueprint(
    'committe_sites', __name__, template_folder='templates')

import donut.modules.committee_sites.routes

