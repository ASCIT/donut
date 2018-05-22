import flask
from donut.modules.bodfeedback import blueprint
from donut.modules.bodfeedback import helpers
from donut import auth_utils


@blueprint.route('/bodfeedback')
def bodfeedback():
    return flask.render_template('bodfeedback.html')


# submit feedback form
@blueprint.route('/bodfeedback/submit', methods=['POST'])
def bodfeedback_submit():
    fields = ['name', 'email', 'subject', 'msg']
    required = ['subject', 'msg']
    data = {}
    for field in fields:
        data[field] = flask.request.form.get(field)
    for field in required:
        if (data[field] == ""):
            flask.flash('Please fill in all required fields (marked with *)',
                        'error')
            return flask.redirect(flask.url_for('bodfeedback.bodfeedback'))
    complaint_id = helpers.register_complaint(data)
    if data['email'] != "":
        helpers.send_confirmation_email(data['email'], complaint_id)
    flask.flash('Success. Link: ' + helpers.get_link(complaint_id))
    return flask.redirect(flask.url_for('bodfeedback.bodfeedback'))


# api endpoint with all visible data
@blueprint.route('/1/bodfeedback/view/<uuid:id>')
def bodfeedback_api_view_complaint(id):
    if not (helpers.get_id(id)):
        return flask.render_template("404.html")
    complaint_id = helpers.get_id(id)
    #pack all the data we need into a dict
    return flask.jsonify(helpers.get_all_fields(complaint_id))


# view a complaint
@blueprint.route('/bodfeedback/view/<uuid:id>')
def bodfeedback_view_complaint(id):
    if not (helpers.get_id(id)):
        return flask.render_template("404.html")
    complaint_id = helpers.get_id(id)
    complaint = helpers.get_all_fields(complaint_id)
    complaint['uuid'] = id
    return flask.render_template('complaint.html', complaint=complaint)


# add a message to this post
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
    if data['message'] == "":
        flask.abort(400)
        return
    helpers.add_msg(complaint_id, data['message'], data['poster'])
    return flask.jsonify({
        'poster': data['poster'],
        'message': data['message']
    })


# allow bod members to see a summary
@blueprint.route('/bodfeedback/view/summary')
def bodfeedback_view_summary():
    #authenticate

    #get a list containing data for each post
    complaints = helpers.get_new_posts()
    #add links to each complaint
    for complaint in complaints:
        complaint['link'] = helpers.get_link(complaint['complaint_id'])
    return flask.render_template('summary.html', complaints=complaints)


# mark a complaint read
@blueprint.route('/1/bodfeedback/markRead/<uuid:id>')
def bodfeedback_mark_read(id):
    #authenticate

    complaint_id = helpers.get_id(id)
    if helpers.mark_read(complaint_id) == False:
        flask.abort(400)
        return
    else:
        return 'Success'


# mark a complaint unread
@blueprint.route('/1/bodfeedback/markUnread/<uuid:id>')
def bodfeedback_mark_unread(id):
    #authenticate

    complaint_id = helpers.get_id(id)
    if helpers.mark_unread(complaint_id) == False:
        flask.abort(400)
        return
    else:
        return 'Success'


# add an email to this complaint
@blueprint.route('/1/bodfeedback/<uuid:id>/addEmail/<email>')
def bodfeedback_add_email(id, email):
    complaint_id = helpers.get_id(id)
    sucess = helpers.add_email(complaint_id, email)
    if not success: return "Failed to add email"
    return "Success!"


# remove an email from this complaint
@blueprint.route('/1/bodfeedback/<uuid:id>/removeEmail/<email>')
def bodfeedback_remove_email(id, email):
    complaint_id = helpers.get_id(id)
    success = helpers.remove_email(complaint_id, email)
    if not success: return "Failed to remove email"
    return "Success!"
