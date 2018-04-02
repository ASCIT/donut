import flask
blueprint = flask.Blueprint(
    'uploads',
    __name__,
    template_folder='templates',
    static_folder='static',
    static_url_path='/donut/modules/uploads/static')

import donut.modules.uploads.routes
