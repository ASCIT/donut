import flask
from donut.modules.arcfeedback import blueprint


@blueprint.route('/arcfeedback')
def arcfeedback():
    return flask.render_template('arcfeedback.html')

@blueprint.route('/arcfeedback/submit', methods=['POST'])
def arcfeedback_submit():
    fields = ['name', 'email', 'class', 'msg']
    data = {}
    for field in fields:
        data[field] = flask.request.form.get(field)
    if data['class'] != "" and data['msg'] != "":
        flask.flash('Success!')
        return flask.redirect(flask.url_for('home'))
    flask.flash('Class and feedback are required fields!')
    return flask.redirect(flask.url_for('arcfeedback.arcfeedback'))
    
