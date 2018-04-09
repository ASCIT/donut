import flask

from . import blueprint, helpers


@blueprint.route('/1/surveys')
def list_surveys():
    return flask.render_template('list_surveys.html')
