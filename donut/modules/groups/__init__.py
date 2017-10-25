import flask
blueprint = flask.Blueprint('groups',__name__, template_folder='templates')

import donut.modules.groups.routes
