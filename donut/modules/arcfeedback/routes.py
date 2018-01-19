import flask
from donut.modules.arcfeedback import blueprint


@blueprint.route('/arcfeedback')
def arcfeedback():
    return flask.render_template('arcfeedback.html')

@blueprint.route('/arcfeedback/submit', methods=['POST'])
def arcfeedback_submit():
    return
