import flask
from Donut.modules.auth import blueprint

@blueprint.route('/userreg')
def user_reg():
	return flask.render_template('userreg.html')

@blueprint.route('/userreg/submit', methods = ['POST'])
def user_reg_submit():
	return ""

@blueprint.route('/recover', methods = ['POST'])
def recover():
	return ""





