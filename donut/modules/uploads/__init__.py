import flask
blueprint = flask.Blueprint('uploads', __name__, template_folder='templates')

import donut.modules.uploads.routes
