import flask
import json

from donut.modules.committee_sites import blueprint, helpers


@blueprint.route('/BoC')
def boc():
    """Display Boc page."""
    return flask.render_template('BoC.html', BoC=helpers.get_BoC_member())


@blueprint.route('/BoC/defendants')
def defendants():
    """Display Boc defendant page."""
    return flask.render_template('BoC.defendants.html')


@blueprint.route('/BoC/witnesses')
def witnesses():
    """Display Boc witnesses page."""
    return flask.render_template('BoC.witnesses.html')


@blueprint.route('/BoC/FAQ')
def FAQ():
    """Display Boc FAQ page."""
    return flask.render_template('BoC.FAQ.html')


@blueprint.route('/BoC/reporters')
def reporters():
    """Display Boc reporters page."""
    return flask.render_template('BoC.reporters.html')


@blueprint.route('/BoC/bylaws')
def bylaws():
    """Display Boc bylaws  page."""
    return flask.render_template('BoC.bylaws.html')


@blueprint.route('/CRC')
def CRC():
    """Display CRC page."""
    return flask.render_template('CRC.html', CRC=helpers.get_CRC_member())
