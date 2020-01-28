import flask

blueprint = flask.Blueprint(
    'newsgroups', __name__, template_folder='templates')

from . import routes
