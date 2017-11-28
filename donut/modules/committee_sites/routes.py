import flask
import json

from donut.modules.committee_sites import blueprint, helpers

@blueprint.route('/BoC')
def boc():
    """Display Boc page."""
    return flask.render_template('BoC.html', helpers.get_BoC_member())
