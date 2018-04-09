import flask

blueprint = flask.Blueprint(
    'directory_search', __name__, template_folder='templates')

from . import routes
