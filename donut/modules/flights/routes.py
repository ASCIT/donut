import flask
from donut import auth_utils

from . import blueprint, helpers


@blueprint.route('/flights')
def flights():
    if not auth_utils.check_login():
        return flask.abort(403)
    settings = helpers.get_settings()
    return flask.render_template(
        'flights.html',
        visible=settings['visible'],
        link=settings['link'],
        admin=helpers.is_admin())


@blueprint.route('/flights/update', methods=['POST'])
def update():
    if not helpers.is_admin():
        return flask.abort(403)
    link = flask.request.form.get('link')
    visible = 'visible' in flask.request.form
    helpers.update(link, visible)
    return flask.redirect(flask.url_for('flights.settings'))


@blueprint.route('/flights/settings')
def settings():
    if not helpers.is_admin():
        return flask.abort(403)
    settings = helpers.get_settings()
    return flask.render_template(
        'settings.html', visible=settings['visible'], link=settings['link'])
