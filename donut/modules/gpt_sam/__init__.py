import flask

blueprint = flask.Blueprint(
    'gpt_sam',
    __name__,
    template_folder='templates',
    static_folder='static',
    static_url_path='/gpt-sam/static'
)

import donut.modules.gpt_sam.routes
