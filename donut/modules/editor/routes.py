import flask
import json

from donut.modules.committee_sites import blueprint, helpers


@blueprint.route('/editor')
def editor(input_text='Hello World!!!'):
    return flask.render_template('editor_page.html', input_text=input_text)
