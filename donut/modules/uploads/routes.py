import flask
import json

from donut.modules.uploads import blueprint, helpers


@blueprint.route('/boop')
def boop():
    flask.render_template('boop.html')

@blueprint.route('/aaa')
def aaa():
	flask.render_template('aaa.html')

@blueprint.route('/ss')
def ss():
	flask.render_template('ss.html')

