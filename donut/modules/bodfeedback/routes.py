import flask
from flask import Markup
from donut.modules.bodfeedback import blueprint
from donut.modules.bodfeedback import helpers
from donut import auth_utils
from donut.modules.bodfeedback.permissions import bod_permissions
from donut.default_permissions import Permissions as default_permissions


@blueprint.route('/bodfeedback')
def bodfeedback():
    summary = False
    if auth_utils.check_login():
        perms = auth_utils.get_permissions(flask.session['username'])
        if default_permissions.ADMIN in perms or bod_permissions.SUMMARY in perms:
            summary = True
    return flask.render_template('bodfeedback.html', summary=summary)


# Submit feedback form
@blueprint.route('/bodfeedback/submit', methods=['POST'])
def bodfeedback_submit():
    fields = ['name', 'email', 'subject', 'msg']
    required = ['subject', 'msg']
    data = {}
    for field in fields:
        data[field] = flask.request.form.get(field)
    for field in required:
        if not data[field]:
            flask.flash('Please fill in all required fields (marked with *)',
                        'error')
            return flask.redirect(flask.url_for('bodfeedback.bodfeedback'))
    complaint_id = helpers.register_complaint(data)
    flask.flash(
        Markup('Success: <a href="' + helpers.get_link(complaint_id) +
               '">View Complaint</a>'))
    return flask.redirect(flask.url_for('bodfeedback.bodfeedback'))


# API endpoint with all visible data
@blueprint.route('/1/bodfeedback/view/<uuid:id>')
def bodfeedback_api_view_complaint(id):
    if not helpers.get_id(id):
        return flask.render_template("404.html")
    complaint_id = helpers.get_id(id)
    # Pack all the data we need into a dict
    return flask.jsonify(helpers.get_all_fields(complaint_id))


# View a complaint
@blueprint.route('/bodfeedback/view/<uuid:id>')
def bodfeedback_view_complaint(id):
    if not helpers.get_id(id):
        return flask.render_template("404.html")
    complaint_id = helpers.get_id(id)
    complaint = helpers.get_all_fields(complaint_id)
    complaint['uuid'] = id
    perms = set()
    if auth_utils.check_login():
        perms = auth_utils.get_permissions(flask.session['username'])
    bodperms = set(bod_permissions)
    if default_permissions.ADMIN not in perms:
        bodperms &= perms
    namedperms = [bod_permissions(perm).name for perm in bodperms]
    return flask.render_template(
        'complaint.html', complaint=complaint, perms=namedperms)


# Add a message to this post
@blueprint.route('/1/bodfeedback/add/<uuid:id>', methods=['POST'])
def bodfeedback_add_msg(id):
    complaint_id = helpers.get_id(id)
    if not complaint_id:
        flask.abort(400)
        return
    fields = ['message', 'poster']
    data = {}
    for field in fields:
        data[field] = flask.request.form.get(field)
    if not data['message']:
        flask.abort(400)
        return
    helpers.add_msg(complaint_id, data['message'], data['poster'])
    return flask.redirect(
        flask.url_for('bodfeedback.bodfeedback_view_complaint', id=id))


# Allow bod members to see a summary
@blueprint.route('/bodfeedback/view/summary')
def bodfeedback_view_summary():
    if 'username' not in flask.session or not auth_utils.check_permission(
            flask.session['username'], bod_permissions.SUMMARY):
        flask.abort(403)
        return
    # Get a list containing data for each post
    complaints = helpers.get_new_posts()
    # Add links to each complaint
    for complaint in complaints:
        complaint['link'] = helpers.get_link(complaint['complaint_id'])
    return flask.render_template('summary.html', complaints=complaints)


# Mark a complaint read
@blueprint.route('/1/bodfeedback/markRead/<uuid:id>')
def bodfeedback_mark_read(id):
    # Authenticate
    if 'username' not in flask.session or not auth_utils.check_permission(
            flask.session['username'], bod_permissions.TOGGLE_READ):
        flask.abort(403)
        return
    complaint_id = helpers.get_id(id)
    if helpers.mark_read(complaint_id) == False:
        flask.abort(400)
        return
    return 'Success'


# Mark a complaint unread
@blueprint.route('/1/bodfeedback/markUnread/<uuid:id>')
def bodfeedback_mark_unread(id):
    # Authenticate
    if 'username' not in flask.session or not auth_utils.check_permission(
            flask.session['username'], bod_permissions.TOGGLE_READ):
        flask.abort(403)
        return
    complaint_id = helpers.get_id(id)
    if helpers.mark_unread(complaint_id) == False:
        flask.abort(400)
        return
    return 'Success'


# Add an email to this complaint
@blueprint.route('/1/bodfeedback/addEmail/<uuid:id>', methods=['POST'])
def bodfeedback_add_email(id):
    if 'username' not in flask.session or not auth_utils.check_permission(
            flask.session['username'], bod_permissions.ADD_REMOVE_EMAIL):
        flask.abort(403)
        return
    complaint_id = helpers.get_id(id)
    if not complaint_id:
        flask.abort(400)
        return
    data = {}
    data['email'] = flask.request.form.get('email')
    if data['email']:
        helpers.add_email(complaint_id, data['email'])
    return flask.redirect(
        flask.url_for('bodfeedback.bodfeedback_view_complaint', id=id))


# Remove an email from this complaint
@blueprint.route('/1/bodfeedback/removeEmail/<uuid:id>', methods=['POST'])
def bodfeedback_remove_email(id):
    if 'username' not in flask.session or not auth_utils.check_permission(
            flask.session['username'], bod_permissions.ADD_REMOVE_EMAIL):
        flask.abort(403)
        return
    complaint_id = helpers.get_id(id)
    if not complaint_id:
        flask.abort(400)
        return
    data = flask.request.form.getlist('emails')
    if data:
        for em in data:
            helpers.remove_email(complaint_id, em)
    return flask.redirect(
        flask.url_for('bodfeedback.bodfeedback_view_complaint', id=id))
