import flask
blueprint = flask.Blueprint('account', __name__, template_folder='templates')

import donut.modules.account.routes
