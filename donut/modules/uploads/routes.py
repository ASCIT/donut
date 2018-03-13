import flask
import json

from donut.modules.uploads import blueprint, helpers


@blueprint.route('/boop')
def boop():
    return flask.render_template('boop.html')

@blueprint.route('/aaa')
def aaa():
    return flask.render_template('aaa.html')

@blueprint.route('/ss')
def ss():
    return flask.render_template('ss.html')

@blueprint.route('/DOESITWORK')
def DOESITWORK():
	return flask.render_template('DOESITWORK.html')

@blueprint.route('/www')
def www():
	return flask.render_template('www.html'
                )

    
@blueprint.route('/qqq')
def qqq():
	return flask.render_template('qqq.html')

@blueprint.route('/eee')
def eee():
	return flask.render_template('eee.html')

@blueprint.route('/ttt')
def ttt():
	return flask.render_template('ttt.html')

@blueprint.route('/fff')
def fff():
	return flask.render_template('fff.html')

@blueprint.route('/ffffff')
def ffffff():
	return flask.render_template('ffffff.html')

@blueprint.route('/zzz')
def zzz():
	return flask.render_template('zzz.html')

@blueprint.route('/test')
def test():
	return flask.render_template('test.html')

@blueprint.route('/test2')
def test2():
	return flask.render_template('test2.html')

@blueprint.route('/test3')
def test3():
	return flask.render_template('test3.html')


@blueprint.route('/test4')
def test4():
	return flask.render_template('test4.html')

@blueprint.route('/rrrrr')
def rrrrr():
	return flask.render_template('rrrrr.html')



