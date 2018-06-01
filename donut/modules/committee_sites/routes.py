import flask
import json

from donut.modules.committee_sites import blueprint, helpers
from donut.resources import Permissions
from donut.auth_utils import check_permission


@blueprint.route('/BoC')
def boc():
    """Display Boc page."""
    return flask.render_template(
        'BoC.html',
        BoC=helpers.get_BoC_member(),
        permission=check_permission(Permissions.ADMIN))


@blueprint.route('/BoC/defendants')
def defendants():
    """Display Boc defendant page."""
    return flask.render_template(
        'BoC_Defendants.html', permission=check_permission(Permissions.ADMIN))


@blueprint.route('/BoC/witness')
def witnesses():
    """Display Boc witness page."""
    return flask.render_template(
        'BoC_Witness.html', permission=check_permission(Permissions.ADMIN))


@blueprint.route('/BoC/FAQ')
def FAQ():
    """Display Boc FAQ page."""
    return flask.render_template(
        'BoC_FAQ.html', permission=check_permission(Permissions.ADMIN))


@blueprint.route('/BoC/reporters')
def reporters():
    """Display Boc reporters page."""
    return flask.render_template(
        'BoC_Reporters.html', permission=check_permission(Permissions.ADMIN))


@blueprint.route('/BoC/bylaws')
def bylaws():
    """Display Boc bylaws page."""
    return flask.render_template(
        'BoC_Bylaws.html', permission=check_permission(Permissions.ADMIN))


@blueprint.route('/ascit/bylaws')
def ascit_bylaws():
    """Display ASCIT bylaws page"""
    return flask.render_template(
        'ASCIT_Bylaws.html', permission=check_permission(Permissions.ADMIN))


@blueprint.route('/honor_system_handbook')
def honor_system_handbook():
    """Display the honor system faculty handbook"""
    return flask.render_template(
        'The_Honor_System.html',
        permission=check_permission(Permissions.ADMIN))


@blueprint.route('/CRC')
def CRC():
    """Display CRC page."""
    return flask.render_template(
        'CRC.html',
        CRC=helpers.get_CRC_member(),
        permission=check_permission(Permissions.ADMIN))
