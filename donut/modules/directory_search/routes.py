import flask
import json
import mimetypes
from flask import jsonify, redirect

from donut.modules.directory_search import blueprint, helpers

VALID_EXTENSIONS = set(['png', 'jpg', 'jpeg'])
VALID_EXTENSIONS |= set(map(lambda ext: ext.upper(), VALID_EXTENSIONS))


@blueprint.route('/directory')
def directory_search():
    return flask.render_template(
        'directory_search.html',
        houses=helpers.get_houses(),
        options=helpers.get_options(),
        residences=helpers.get_residences(),
        states=helpers.get_states())


@blueprint.route('/1/users/me')
def my_directory_page():
    return redirect(
        flask.url_for(
            'directory_search.view_user',
            user_id=helpers.get_user_id(flask.session['username'])))


@blueprint.route('/1/users/<int:user_id>')
def view_user(user_id):
    user = helpers.get_user(user_id)
    is_me = 'username' in flask.session and helpers.get_user_id(
        flask.session['username']) == user_id
    return flask.render_template(
        'view_user.html', user=user, is_me=is_me, user_id=user_id)


@blueprint.route('/1/users/<int:user_id>/edit')
def edit_user(user_id):
    if user_id != helpers.get_user_id(flask.session['username']):
        raise Exception('Can only edit your own page')
    return flask.render_template('edit_user.html', user_id=user_id)


@blueprint.route('/1/users/<int:user_id>/image', methods=['POST'])
def set_image(user_id):
    if user_id != helpers.get_user_id(flask.session['username']):
        raise Exception('Can only set your own image')

    def flash_error(message):
        flash(message)
        return redirect(
            flask.url_for('directory_search.edit_user', user_id=user_id))

    file = flask.request.files['file']
    if not file.filename:
        return flash_error('No file uploaded')
    extension = file.filename.split('.')[-1]
    if extension not in VALID_EXTENSIONS:
        return flash_error('Unknown image extension')
    file_contents = file.read()
    file.close()
    helpers.set_image(user_id, extension, file_contents)
    return redirect(
        flask.url_for('directory_search.view_user', user_id=user_id))


@blueprint.route('/1/users/<int:user_id>/image', methods=['GET'])
def get_image(user_id):
    extension, image = helpers.get_image(user_id)
    response = flask.make_response(image)
    response.headers.set('Content-Type',
                         mimetypes.guess_type('img.' + extension)[0])
    return response


@blueprint.route('/1/users/search/<name_query>')
def search_by_name(name_query):
    return jsonify(helpers.get_users_by_name_query(name_query))


@blueprint.route('/1/users', methods=['POST'])
def search():
    form = flask.request.form
    name = form['name']
    if name.strip() == '':
        name = None
    house_id = form['house']
    if house_id:
        house_id = int(house_id)
    else:
        house_id = None
    option_id = form['option']
    if option_id:
        option_id = int(option_id)
    else:
        option_id = None
    building_id = form['residence']
    if building_id:
        building_id = int(building_id)
    else:
        building_id = None
    state = form['state'] or None
    show_images = True if 'show_images' in form else None
    users = helpers.execute_search(
        name=name,
        house_id=house_id,
        option_id=option_id,
        building_id=building_id,
        state=state,
        username=form['username'],
        email=form['email'])
    if len(users) == 1:  #1 result
        return redirect(
            flask.url_for(
                'directory_search.view_user', user_id=users[0]['user_id']))

    return flask.render_template(
        'search_results.html', users=users, show_images=show_images)
