import flask
import json

from donut.modules.committee_sites import blueprint, helpers


@blueprint.route('/editor')
def editor():
    return flask.render_template('editor_page.html')
