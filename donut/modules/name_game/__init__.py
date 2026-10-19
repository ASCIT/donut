import flask

blueprint = flask.Blueprint(
    'name_game',
    __name__,
    template_folder='templates',
    static_folder='static',
    static_url_path='/name_game/static')

from . import routes