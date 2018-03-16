import flask
blueprint = flask.Blueprint(
    'committee_sites', __name__, template_folder='templates', static_folder='static', static_url_path='/donut/modules/committee_sites/static'))

import donut.modules.committee_sites.routes
