import flask

blueprint = flask.Blueprint('rooms', __name__, template_folder='templates')

from . import routes
