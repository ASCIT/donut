import flask

blueprint = flask.Blueprint('db_admin', __name__, template_folder='templates')

import donut.modules.db_admin.routes
