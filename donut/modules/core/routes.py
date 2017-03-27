import flask

from donut.modules.core import blueprint, helpers

@blueprint.route("/members")
def get_members():
    """GET /1/members"""
    return "hi"
