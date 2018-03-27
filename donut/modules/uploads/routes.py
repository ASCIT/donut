import flask
import json

from donut.modules.uploads import blueprint, helpers


@blueprint.route('/<path:url>')
def display(url):
    page = helpers.readPage(url.lower())
    return flask.render_template('page.html', page=page, title=url)
