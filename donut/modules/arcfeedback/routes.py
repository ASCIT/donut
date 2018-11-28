import flask
from donut.modules.arcfeedback import blueprint
from donut.modules.arcfeedback import helpers
from donut import auth_utils
from datetime import datetime
from donut.modules.arcfeedback.permissions import arc_permissions
from donut.default_permissions import Permissions as default_permissions


@blueprint.route('/arcfeedback')
def arcfeedback():
    summary = auth_utils.check_login() and \
              auth_utils.check_permission(flask.session['username'],
                                          arc_permissions.SUMMARY)
    return flask.render_template('arcfeedback.html', summary=summary)


# submit feedback form
@blueprint.route('/arcfeedback/submit', methods=['POST'])
def arcfeedback_submit():
    fields = ['name', 'email', 'course', 'msg']
    required = ['course', 'msg']
    max_len = {'name': 50, 'email': 50, 'course': 50, 'msg': 5000}
    data = {}
    for field in fields:
        data[field] = flask.request.form.get(field)
    for field in required:
        if (data[field] == ""):
            flask.flash('Please fill in all required fields (marked with *)',
                        'error')
            return flask.redirect(flask.url_for('arcfeedback.arcfeedback'))
    for field in data:
        if len(data[field]) > max_len[field]:
            flask.flash(
                'Error: field %s exceeded the maximum character length' %
                (field))
            return flask.redirect(flask.url_for('arcfeedback.arcfeedback'))
    complaint_id = helpers.register_complaint(data)
    if data['email'] != "":
        helpers.send_confirmation_email(data['email'], complaint_id)
    flask.flash('Success. Link: ' + helpers.get_link(complaint_id))
    return flask.redirect(flask.url_for('arcfeedback.arcfeedback'))


# api endpoint with all visible data
@blueprint.route('/1/arcfeedback/view/<uuid:id>')
def arcfeedback_api_view_complaint(id):
    complaint_id = helpers.get_id(id)
    if not complaint_id:
        return flask.render_template("404.html")
    # pack all the data we need into a dict
    return flask.jsonify(helpers.get_all_fields(complaint_id))


# view a complaint
@blueprint.route('/arcfeedback/view/<uuid:id>')
def arcfeedback_view_complaint(id):
    if not (helpers.get_id(id)):
        return flask.render_template("404.html")
    complaint_id = helpers.get_id(id)
    complaint = helpers.get_all_fields(complaint_id)
    complaint['uuid'] = id
    perms = set()
    if auth_utils.check_login():
        perms = auth_utils.get_permissions(flask.session['username'])
    if default_permissions.ADMIN in perms:
        arcperms = set(arc_permissions)
    else:
        arcperms = perms & (set(arc_permissions))
    namedperms = [perm.name for perm in arcperms]
    return flask.render_template(
        'complaint.html', complaint=complaint, perms=namedperms)


# add a message to this post
@blueprint.route('/1/arcfeedback/add/<uuid:id>', methods=['POST'])
def arcfeedback_add_msg(id):
    complaint_id = helpers.get_id(id)
    if not complaint_id:
        flask.abort(400)
        return
    fields = ['message', 'poster']
    data = {}
    for field in fields:
        data[field] = flask.request.form.get(field)
    if data['message'] == "":
        flask.abort(400)
        return
    if len(poster) > 50 or len(message) > 5000:
        return flask.jsonify({'ERROR': 'Entered data was too long'})
    helpers.add_msg(complaint_id, data['message'], data['poster'])
    return flask.jsonify({
        'poster': data['poster'],
        'message': data['message'],
        'time': datetime.now().strftime('%b %d %Y %-I:%M%p')
    })


# allow arc members to see a summary
@blueprint.route('/arcfeedback/view/summary')
def arcfeedback_view_summary():
    #authenticate
    if not auth_utils.check_permission(flask.session['username'],
                                       arc_permissions.SUMMARY):
        flask.abort(403)
        return
    #get a list containing data for each post
    complaints = helpers.get_new_posts()
    #add links to each complaint
    for complaint in complaints:
        complaint['link'] = helpers.get_link(complaint['complaint_id'])
    return flask.render_template('summary.html', complaints=complaints)


# mark a complaint read
@blueprint.route('/1/arcfeedback/markRead/<uuid:id>')
def arcfeedback_mark_read(id):
    #authenticate
    if not auth_utils.check_permission(flask.session['username'],
                                       arc_permissions.TOGGLE_READ):
        flask.abort(403)
        return
    complaint_id = helpers.get_id(id)
    if helpers.mark_read(complaint_id) == False:
        flask.abort(400)
        return
    else:
        return 'Success'


# mark a complaint unread
@blueprint.route('/1/arcfeedback/markUnread/<uuid:id>')
def arcfeedback_mark_unread(id):
    #authenticate
    if not auth_utils.check_permission(flask.session['username'],
                                       arc_permissions.TOGGLE_READ):
        flask.abort(403)
        return
    complaint_id = helpers.get_id(id)
    if helpers.mark_unread(complaint_id) == False:
        flask.abort(400)
        return
    else:
        return 'Success'


# add an email to this complaint
@blueprint.route('/1/arcfeedback/<uuid:id>/addEmail', methods=['POST'])
def arcfeedback_add_email(id):
    if not auth_utils.check_permission(flask.session['username'],
                                       arc_permissions.ADD_REMOVE_EMAIL):
        flask.abort(403)
        return
    complaint_id = helpers.get_id(id)
    emails = flask.request.form.get('email')
    emails = emails.split(',')
    emails = [email.strip() for email in emails]
    for email in emails:
        if len(email) > 50:
            flask.flash("An email exceeded the character limit")
            return arcfeedback_view_complaint(id)
    success = helpers.add_email(complaint_id, emails)
    if not success:
        flask.flash("Failed to add email(s)")
    else:
        flask.flash("Success!")
    return arcfeedback_view_complaint(id)


# remove an email from this complaint
@blueprint.route('/1/arcfeedback/<uuid:id>/removeEmail', methods=['POST'])
def arcfeedback_remove_email(id):
    if not auth_utils.check_permission(flask.session['username'],
                                       arc_permissions.ADD_REMOVE_EMAIL):
        flask.abort(403)
        return
    complaint_id = helpers.get_id(id)
    emails = flask.request.form.get('email')
    emails = emails.split(',')
    emails = [email.strip() for email in emails]
    for email in emails:
        if len(email) > 50:
            flask.flash("An email exceeded the character limit")
            return arcfeedback_view_complaint(id)
    for email in emails:
        if not helpers.remove_email(complaint_id, email):
            flask.flash('Failed to remove email: %s' % (email))
            return arcfeedback_view_complaint(id)
    flask.flash('Success!')
    return arcfeedback_view_complaint(id)
