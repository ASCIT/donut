import flask
from flask import Markup
from donut.modules.feedback import blueprint
from donut.modules.feedback import helpers
from donut import auth_utils
from donut.modules.feedback.permissions import BOD_PERMISSIONS, ARC_PERMISSIONS, DONUT_PERMISSIONS
from donut.default_permissions import Permissions as default_permissions
from donut.modules.feedback.groups import Groups
permissions = {
    'bod': BOD_PERMISSIONS,
    'arc': ARC_PERMISSIONS,
    'donut': DONUT_PERMISSIONS
}


@blueprint.route('/feedback/<group>')
def feedback(group):
    if group not in Groups:
        return flask.abort(404)
    summary = False
    if auth_utils.check_login():
        perms = auth_utils.get_permissions(flask.session['username'])
        if default_permissions.ADMIN in perms or permissions[group].SUMMARY in perms:
            summary = True
    return flask.render_template(
        'feedback.html', summary=summary, group=group, msg=Groups[group])


# Submit feedback form
@blueprint.route('/feedback/<group>/submit', methods=['POST'])
def feedback_submit(group):
    if group not in Groups:
        return flask.abort(404)
    fields = ['name', 'email', 'subject', 'msg', 'ombuds']
    data = {}
    for field in fields:
        data[field] = flask.request.form.get(field)
    complaint_id = helpers.register_complaint(group, data)
    flask.flash(
        Markup('Success (you may want to save this link): <a href="' +
               helpers.get_link(group, complaint_id) + '">View Complaint</a>'))
    return flask.redirect(flask.url_for('feedback.feedback', group=group))


# View a complaint
@blueprint.route('/feedback/<group>/view/<id>')
def feedback_view_complaint(group, id):
    if group not in Groups or not helpers.get_id(group, id):
        return flask.abort(404)
    complaint_id = helpers.get_id(group, id)
    complaint = helpers.get_all_fields(group, complaint_id)
    complaint['uuid'] = id
    perms = set()
    if auth_utils.check_login():
        perms = auth_utils.get_permissions(flask.session['username'])
    bodperms = set(permissions[group])
    if default_permissions.ADMIN not in perms:
        bodperms &= perms
    namedperms = [permissions[group](perm).name for perm in bodperms]
    return flask.render_template(
        'complaint.html', complaint=complaint, perms=namedperms, group=group)


# Add a message to this post
@blueprint.route('/1/feedback/<group>/add/<id>', methods=['POST'])
def feedback_add_msg(group, id):
    if group not in Groups:
        return flask.abort(404)
    complaint_id = helpers.get_id(group, id)
    if not complaint_id:
        return flask.abort(400)
    fields = ['message', 'poster']
    data = {}
    for field in fields:
        data[field] = flask.request.form.get(field)
    if not data['message']:
        return flask.abort(400)
    helpers.add_msg(group, complaint_id, data['message'], data['poster'])
    return flask.redirect(
        flask.url_for('feedback.feedback_view_complaint', group=group, id=id))


# Allow bod members to see a summary
@blueprint.route('/feedback/<group>/view/summary')
def feedback_view_summary(group):
    if group not in Groups:
        return flask.abort(404)
    if 'username' not in flask.session or not auth_utils.check_permission(
            flask.session['username'], permissions[group].SUMMARY):
        return flask.abort(403)
    # Get a list containing data for each post
    complaints = helpers.get_new_posts(group)
    # Add links to each complaint
    for complaint in complaints:
        complaint['link'] = helpers.get_link(group, complaint['complaint_id'])
    return flask.render_template(
        'summary.html', complaints=complaints, group=group)


# Mark a complaint read
@blueprint.route('/1/feedback/<group>/markRead/<id>')
def feedback_mark_read(group, id):
    if group not in Groups:
        return flask.abort(404)
    # Authenticate
    if 'username' not in flask.session or not auth_utils.check_permission(
            flask.session['username'], permissions[group].TOGGLE_READ):
        return flask.abort(403)
    complaint_id = helpers.get_id(group, id)
    if helpers.mark_read(group, complaint_id) == False:
        return flask.abort(400)
    return 'Success'


# Mark a complaint unread
@blueprint.route('/1/feedback/<group>/markUnread/<id>')
def feedback_mark_unread(group, id):
    if group not in Groups:
        return flask.abort(404)
    # Authenticate
    if 'username' not in flask.session or not auth_utils.check_permission(
            flask.session['username'], permissions[group].TOGGLE_READ):
        return flask.abort(403)
    complaint_id = helpers.get_id(group, id)
    if helpers.mark_unread(group, complaint_id) == False:
        return flask.abort(400)
    return 'Success'


# Add an email to this complaint
@blueprint.route('/1/feedback/<group>/addEmail/<id>', methods=['POST'])
def feedback_add_email(group, id):
    if group not in Groups:
        return flask.abort(404)
    if 'username' not in flask.session or not auth_utils.check_permission(
            flask.session['username'], permissions[group].ADD_REMOVE_EMAIL):
        return flask.abort(403)
    complaint_id = helpers.get_id(group, id)
    if not complaint_id:
        return flask.abort(400)
    data = {}
    data['email'] = flask.request.form.get('email')
    if data['email']:
        helpers.add_email(group, complaint_id, data['email'])
    return flask.redirect(
        flask.url_for('feedback.feedback_view_complaint', group=group, id=id))


# Remove an email from this complaint
@blueprint.route('/1/feedback/<group>/removeEmail/<id>', methods=['POST'])
def feedback_remove_email(group, id):
    if group not in Groups:
        return flask.abort(404)
    if 'username' not in flask.session or not auth_utils.check_permission(
            flask.session['username'], permissions[group].ADD_REMOVE_EMAIL):
        return flask.abort(403)
    complaint_id = helpers.get_id(group, id)
    if not complaint_id:
        return flask.abort(400)
    data = flask.request.form.getlist('emails')
    for em in data:
        helpers.remove_email(group, complaint_id, em)
    return flask.redirect(
        flask.url_for('feedback.feedback_view_complaint', group=group, id=id))


# Set the spoken to ombuds status
@blueprint.route('/1/feedback/arc/arc_ombuds/<id>', methods=['POST'])
def arc_ombuds(id):
    if 'username' not in flask.session:
        return flask.abort(403)
    complaint_id = helpers.get_id('arc', id)
    if not complaint_id:
        return flask.abort(400)
    ombuds = flask.request.form.get('ombuds')
    if ombuds is None:
        return flask.abort(400)
    helpers.set_ombuds(complaint_id, ombuds)
    return flask.redirect(
        flask.url_for('feedback.feedback_view_complaint', group='arc', id=id))
