import flask
blueprint = flask.Blueprint('flights', __name__, template_folder='templates')

from . import routes
