from datetime import date
import flask
import json
import mimetypes
from flask import jsonify, redirect

from donut.auth_utils import get_user_id, is_caltech_user, login_redirect
from donut.validation_utils import validate_exists, validate_int
from . import blueprint, helpers
from ..groups.helpers import create_position_holder, end_position_holder


@blueprint.route('/directory')
def directory_search():
    if not is_caltech_user():
        return login_redirect()

    return flask.render_template(
        'directory_search.html',
        manage_members_houses=helpers.get_manage_members_houses(),
        houses=helpers.get_houses(),
        options=helpers.get_options(),
        residences=helpers.get_residences(),
        grad_years=helpers.get_grad_years())


@blueprint.route('/1/users/<int:user_id>')
def view_user(user_id):
    if not is_caltech_user():
        return login_redirect()

    user = helpers.get_user(user_id)
    username = flask.session.get('username')
    hidden_fields = helpers.get_hidden_fields(username, user_id)
    user = {key: value for key, value in user.items() if key not in hidden_fields}
    is_me = username is not None and get_user_id(username) == user_id
    return flask.render_template(
        'view_user.html',
        user=user,
        is_me=is_me,
        user_id=user_id)


@blueprint.route('/1/users/<int:user_id>/image')
def get_image(user_id):
    if not is_caltech_user():
        flask.abort(401)

    extension, image = helpers.get_image(user_id)
    response = flask.make_response(image)
    response.headers.set('Content-Type',
                         mimetypes.guess_type('img.' + extension)[0])
    return response


@blueprint.route('/1/users/search/<name_query>')
def search_by_name(name_query):
    if not is_caltech_user():
        flask.abort(401)

    return jsonify(helpers.get_users_by_name_query(name_query))


@blueprint.route('/1/users', methods=['GET', 'POST'])
def search():
    if not is_caltech_user():
        flask.abort(401)

    if flask.request.method == 'POST':
        form = flask.request.form
        page = 1
        per_page = 10
    else:
        form = flask.request.args
        page = int(form['page'])
        total = int(form['total'])
        per_page = int(form['per_page'])
    name = form['name']
    if name.strip() == '':
        name = None
    house_id = form['house_id']
    if house_id:
        house_id = int(house_id)
    else:
        house_id = None
    option_id = form['option_id']
    if option_id:
        option_id = int(option_id)
    else:
        option_id = None
    building_id = form['building_id']
    if building_id:
        building_id = int(building_id)
    else:
        building_id = None
    grad_year = form['grad_year']
    if grad_year:
        grad_year = int(grad_year)
    else:
        grad_year = None
    # TODO: remove timezone after COVID
    tz_from = form.get('timezone_from')
    tz_to = form.get('timezone_to')
    tz_from = int(tz_from) if tz_from else None
    tz_to = int(tz_to) if tz_to else None
    offset = (page - 1) * per_page
    args = dict(
        name=name,
        house_id=house_id,
        option_id=option_id,
        building_id=building_id,
        grad_year=grad_year,
        username=form['username'],
        email=form['email'],
        tz_from=tz_from,
        tz_to=tz_to)
    if flask.request.method == 'POST':
        total = helpers.execute_search(**args)
    offset = (page - 1) * per_page
    users = helpers.execute_search(**args, offset=offset, per_page=per_page)
    if total == 1:  #1 result
        return redirect(
            flask.url_for(
                'directory_search.view_user', user_id=users[0]['user_id']))
    show_images = form.get('show_images')
    query_info = {k: ('' if v is None else v) for k, v in args.items()}
    query_info['total'] = total
    query_info['show_images'] = show_images
    return flask.render_template(
        'search_results.html',
        users=users,
        show_images=show_images,
        total=total,
        per_page=per_page,
        page=page,
        query_info=query_info)


@blueprint.route('/house_members')
def manage_members():
    manage_houses = helpers.get_manage_members_houses()
    house_members = {}
    for house in manage_houses:
        positions = helpers.get_house_member_positions(house)
        house_members[house] = [
            {**position, 'members': helpers.get_members(position['pos_id'])}
            for position in positions
        ]
    return flask.render_template(
        'manage_house_members.html',
        manage_houses=manage_houses,
        house_members=house_members)


@blueprint.route('/house_members/<int:pos_id>', methods=('POST', ))
def add_member(pos_id):
    house = helpers.get_position_house(pos_id)
    if house not in helpers.get_manage_members_houses():
        flask.abort(403)

    form = flask.request.form
    if not validate_exists(form, 'user_id'):
        return flask.redirect(flask.url_for('.manage_members'))
    user_id = form['user_id']
    if not validate_int(user_id, flash_errors=False):
        flask.flash('Please select a user')
        return flask.redirect(flask.url_for('.manage_members'))

    create_position_holder(pos_id, int(user_id), date.today(), None)
    flask.flash('Added member')
    return flask.redirect(flask.url_for('.manage_members'))


@blueprint.route('/house_members/<int:hold_id>/remove')
def remove_member(hold_id):
    house = helpers.get_held_position_house(hold_id)
    if house not in helpers.get_manage_members_houses():
        flask.abort(403)

    end_position_holder(hold_id)
    flask.flash('Removed member')
    return flask.redirect(flask.url_for('.manage_members'))
