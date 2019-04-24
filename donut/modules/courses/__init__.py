import flask

blueprint = flask.Blueprint('courses', __name__, template_folder='templates')

from . import routes
