import flask
import json
from flask import jsonify

from donut.modules.groups import blueprint, helpers


@blueprint.route("/1/groups/")
def get_groups_list():
    # Create a dict of the passed in attribute which are filterable
    filterable_attrs = ["group_id", "group_name", "group_desc", "type"]
    attrs = {
        tup: flask.request.args[tup]
        for tup in flask.request.args if tup in filterable_attrs
    }
    fields = None
    if "fields" in flask.request.args:
        fields = [f.strip() for f in flask.request.args["fields"].split(',')]
    return json.dumps(helpers.get_group_list_data(fields=fields, attrs=attrs))


@blueprint.route("/1/groups/<int:group_id>/positions/")
def get_group_positions(group_id):
    """GET /1/groups/<int:group_id>/positions/"""
    return jsonify(helpers.get_group_positions(group_id))


@blueprint.route("/1/positions/")
def get_positions():
    return jsonify(helpers.get_position_data())


@blueprint.route("/1/groups/<int:group_id>/")
def get_groups(group_id):
    """GET /1/groups/<int:group_id>/"""
    return jsonify(helpers.get_group_data(group_id))


@blueprint.route("/1/groups/<int:group_id>/members/")
def get_group_members(group_id):
    """GET /1/groups/<int:group_id>/"""
    return jsonify(helpers.get_members_by_group(group_id))


@blueprint.route("/1/positions/<int:pos_id>/")
def get_pos_holders(pos_id):
    """Get /1/positions/<int:pos_id>/"""
    return jsonify(helpers.get_position_holders(pos_id))
