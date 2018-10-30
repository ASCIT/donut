import flask

blueprint = flask.Blueprint('voting', __name__, template_folder='templates')

from . import routes
