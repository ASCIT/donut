import flask
import json
from flask import jsonify, redirect

from donut import auth_utils
from donut.modules.core import blueprint, helpers
from donut.validation_utils import validate_email, validate_matches

VALID_EXTENSIONS = set(['png', 'jpg', 'jpeg'])
VALID_EXTENSIONS |= set(ext.upper() for ext in VALID_EXTENSIONS)


@blueprint.route("/1/members/")
def get_members_list():
    """GET /1/members/"""
    # Create a dict of the passed in attributes which are filterable
    filterable_attrs = [
        "uid", "last_name", "first_name", "middle_name", "email", "entry_year",
        "graduation_year", "zip"
    ]
    attrs = {
        tup: flask.request.args[tup]
        for tup in flask.request.args if tup in filterable_attrs
    }

    # Get the fields to return if they were passed in
    fields = None
    if "fields" in flask.request.args:
        fields = [f.strip() for f in flask.request.args["fields"].split(',')]

    return jsonify(helpers.get_member_list_data(fields=fields, attrs=attrs))


@blueprint.route("/1/members/<int:user_id>/")
def get_members(user_id):
    """GET /1/members/<int:user_id>/"""
    filterable_attrs = [
        "uid", "last_name", "first_name", "middle_name", "email", "entry_year",
        "graduation_year", "zip"
    ]

    # Get the fields to return if they were passed in
    fields = None
    if "fields" in flask.request.args:
        fields = [f.strip() for f in flask.request.args["fields"].split(',')]

    return jsonify(helpers.get_member_data(user_id, fields=fields))


@blueprint.route("/1/members/<int:user_id>/groups/")
def get_group_list_of_member(user_id):
    '''GET /1/members/<int:user_id>/groups/
       List all groups that a member is in
    '''
    return jsonify(helpers.get_group_list_of_member(user_id))


# Routes for interacting with your directory page


@blueprint.route('/1/users/me')
def my_directory_page():
    return redirect(
        flask.url_for(
            'directory_search.view_user',
            user_id=auth_utils.get_user_id(flask.session['username'])))


@blueprint.route('/1/users/me/edit')
def edit_user():
    user_id = auth_utils.get_user_id(flask.session['username'])
    name = helpers.get_preferred_name(user_id)
    gender = helpers.get_gender(user_id)
    return flask.render_template('edit_user.html', name=name, gender=gender)


@blueprint.route('/1/users/me/image', methods=['POST'])
def set_image():
    user_id = auth_utils.get_user_id(flask.session['username'])

    def flash_error(message):
        flask.flash(message)
        return redirect(flask.url_for('.edit_user'))

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


@blueprint.route('/1/users/me/name', methods=['POST'])
def set_name():
    user_id = auth_utils.get_user_id(flask.session['username'])
    helpers.set_member_field(user_id, 'preferred_name',
                             flask.request.form['name'] or None)
    return redirect(
        flask.url_for('directory_search.view_user', user_id=user_id))


@blueprint.route('/1/users/me/gender', methods=['POST'])
def set_gender():
    user_id = auth_utils.get_user_id(flask.session['username'])
    helpers.set_member_field(user_id, 'gender_custom',
                             flask.request.form['gender'] or None)
    return redirect(
        flask.url_for('directory_search.view_user', user_id=user_id))


@blueprint.route('/1/users/me/email', methods=('POST', ))
def set_email():
    username = flask.session.get('username')
    if username is None:
        flask.abort(403)

    email = flask.request.form['email']
    valid = validate_email(email) and \
        validate_matches(email, flask.request.form['email2'])
    if not valid:
        return redirect(flask.url_for('.edit_user'))

    user_id = auth_utils.get_user_id(username)
    helpers.set_member_field(user_id, 'email', email)
    return redirect(
        flask.url_for('directory_search.view_user', user_id=user_id))


# TODO: remove timezone after COVID
@blueprint.route('/1/users/me/tz', methods=['POST'])
def set_timezone():
    user_id = auth_utils.get_user_id(flask.session['username'])
    timezone = flask.request.form['timezone']
    timezone = int(timezone) if timezone else None
    helpers.set_member_field(user_id, 'timezone', timezone)
    return redirect(
        flask.url_for('directory_search.view_user', user_id=user_id))
