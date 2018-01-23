import flask
from donut.modules.arcfeedback import blueprint


@blueprint.route('/arcfeedback')
def arcfeedback():
    return flask.render_template('arcfeedback.html')


@blueprint.route('/arcfeedback/submit', methods=['POST'])
def arcfeedback_submit():
    fields = ['name', 'email', 'class', 'msg']
    required = ['class', 'msg']
    data = {}
    for field in fields:
        data[field] = flask.request.form.get(field)
    for field in required:
        if (data[field] == ""):
            flask.flash('Please fill in all required fields (marked with *)', 'error')
            return flask.redirect(flask.url_for('arcfeedback.arcfeedback'))
    flask.flash('Success')
    return flask.redirect(flask.url_for('arcfeedback.arcfeedback'))

