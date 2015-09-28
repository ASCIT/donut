import flask
from donut import constants
from donut.modules.auth import blueprint

@blueprint.route('/login')
def login():
    """Display login page."""
    return flask.render_template('login.html')

@blueprint.route('/login/submit', methods=['POST'])
def login_submit():
    """Handle authentication."""
    # TODO: Add login logic.
    flask.flash('Incorrect username or password. Please try again!')
    return flask.redirect(flask.url_for('auth.login'))

@blueprint.route('/userreg')
def user_reg():
	return flask.render_template('userreg.html')

@blueprint.route('/userreg/submit', methods = ['POST'])
def user_reg_submit():
	return ""

@blueprint.route('/recover', methods = ['POST'])
def recover():
	return ""
