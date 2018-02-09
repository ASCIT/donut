import flask
from donut.modules.arcfeedback import blueprint
from donut.modules.arcfeedback import helpers


@blueprint.route('/arcfeedback')
def arcfeedback():
    return flask.render_template('arcfeedback.html')

# submit feedback form
@blueprint.route('/arcfeedback/submit', methods=['POST'])
def arcfeedback_submit():
    fields = ['name', 'email', 'course', 'msg']
    required = ['course', 'msg']
    data = {}
    for field in fields:
        data[field] = flask.request.form.get(field)
    for field in required:
        if (data[field] == ""):
            flask.flash('Please fill in all required fields (marked with *)', 'error')
            return flask.redirect(flask.url_for('arcfeedback.arcfeedback'))
    complaint_id = helpers.register_complaint(data)
    if data['email'] != "":
        helpers.send_confirmation_email(data['email'], complaint_id)
    flask.flash('Success. Link: ' + helpers.get_link(complaint_id))
    return flask.redirect(flask.url_for('arcfeedback.arcfeedback'))


# api endpoint with all visible data
@blueprint.route('/1/arcfeedback/view/<uuid:id>')
def arcfeedback_api_view_complaint(id):
    if not (helpers.get_id(id)):
        return flask.render_template("404.html")
    complaint_id = helpers.get_id(id)
    #pack all the data we need into a dict
    return flask.jsonify(helpers.get_all_fields(complaint_id)) #flask.render_template('complaint.html', data=data)


# view a complaint
@blueprint.route('/arcfeedback/view/<uuid:id>')
def arcfeedback_view_complaint(id):
    if not (helpers.get_id(id)):
        return flask.render_template("404.html")
    complaint_id = helpers.get_id(id)
    data = helpers.get_all_fields(complaint_id)
    return flask.render_template('complaint.html', data=data)

# TODO: summary page for arc members