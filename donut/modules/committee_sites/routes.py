import flask
import json

from donut.modules.committee_sites import blueprint, helpers
from donut.resources import Permissions
from donut.auth_utils import check_permission


@blueprint.route('/BoC')
def boc():
    """Display Boc page."""
    if check_permission(Permissions.ADMIN):
        return flask.render_template('BoC.html', BoC=helpers.get_BoC_member(), permission=True)
    return flask.render_template('BoC.html', BoC=helpers.get_BoC_member())


@blueprint.route('/BoC/defendants')
def defendants():
    """Display Boc defendant page."""
    if check_permission(Permissions.ADMIN):
        return flask.render_template('BoC.defendants.html', permission=True)
    return flask.render_template('BoC.defendants.html')


@blueprint.route('/BoC/witnesses')
def witnesses():
    """Display Boc witnesses page."""
    if check_permission(Permissions.ADMIN):
        return flask.render_template('BoC.witnesses.html', permission=True)
    return flask.render_template('BoC.witnesses.html')


@blueprint.route('/BoC/FAQ')
def FAQ():
    """Display Boc FAQ page."""
     if check_permission(Permissions.ADMIN):
        return flask.render_template('BoC.reporters.html', permission=True)
    return flask.render_template('BoC.FAQ.html')


@blueprint.route('/BoC/reporters')
def reporters():
    """Display Boc reporters page."""
    if check_permission(Permissions.ADMIN):
        return flask.render_template('BoC.reporters.html', permission=True)
    return flask.render_template('BoC.reporters.html')


@blueprint.route('/BoC/bylaws')
def bylaws():
    """Display Boc bylaws page."""
    if check_permission(Permissions.ADMIN):
        return flask.render_template('BoC.bylaws.html', permission=True)
    return flask.render_template('BoC.bylaws.html')


@blueprint.route('/ascit/bylaws')
def ascit_bylaws():
    """Display ASCIT bylaws page"""
    if check_permission(Permissions.ADMIN):
        return flask.render_template('ascit_bylaws.html', permission=True)
    return flask.render_template('ascit_bylaws.html')


@blueprint.route('/honor_system_handbook')
def honor_system_handbook():
    """Display the honor system faculty handbook"""
    if check_permission(Permissions.ADMIN):
        return flask.render_template('honor_system_handbook.html', permission=True)
    return flask.render_template('honor_system_handbook.html')


@blueprint.route('/CRC')
def CRC():
    """Display CRC page."""
    if check_permission(Permissions.ADMIN):
        return flask.render_template('CRC.html', CRC=helpers.get_CRC_member(), permission=True)
    return flask.render_template('CRC.html', CRC=helpers.get_CRC_member())
