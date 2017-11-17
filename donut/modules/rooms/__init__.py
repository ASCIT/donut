import flask

blueprint = flask.Blueprint('rooms', __name__, template_folder='templates')

import donut.modules.rooms.routes
