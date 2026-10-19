import mimetypes

import flask

from donut.auth_utils import is_caltech_user, login_redirect
from donut.modules.directory_search import helpers as directory_helpers
from . import blueprint, helpers


@blueprint.route('/name_game')
def name_game():
    if not is_caltech_user():
        return login_redirect()

    filters = helpers.get_filters(flask.request.args)
    if filters is None:
        default_min_year, default_max_year = helpers.get_default_grad_years()
        return flask.render_template(
            'name_game.html',
            game_modes=helpers.GAME_MODE_NAMES,
            houses=helpers.get_houses(),
            majors=helpers.get_majors(),
            default_min_year=default_min_year,
            default_max_year=default_max_year,
            max_people=helpers.MAX_PEOPLE)

    try:
        roster = helpers.make_roster(**filters)
    except ValueError as error:
        flask.flash(str(error))
        return flask.redirect(flask.url_for('.name_game'))

    return flask.render_template(
        'play.html', roster=roster, game_mode=filters['game_mode'])


@blueprint.route('/1/name_game/image/<int:user_id>')
def get_image(user_id):
    """Serves the face of a member of the directory for the game."""
    if not is_caltech_user():
        flask.abort(401)

    extension, image = directory_helpers.get_image(user_id)
    response = flask.make_response(image)
    response.headers.set('Content-Type',
                         mimetypes.guess_type('img.' + extension)[0])
    return response