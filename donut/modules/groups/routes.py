import flask
import json
from flask import jsonify

from donut.modules.groups import blueprint, helpers
from donut.validation_utils import (validate_exists, validate_int)


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


@blueprint.route("/1/positions/", methods=["POST", "GET"])
def get_positions():
    if flask.request.method == "GET":
        return jsonify(helpers.get_position_data())
    if flask.request.method == "POST":
        form = flask.request.form
        validations = [
            validate_exists(form, "group_id")
            and validate_int(form["group_id"]),
            validate_exists(form, "pos_name")
        ]
        if not all(validations):
            return json.dumps({
                'success': False
            })
        else:
            helpers.add_position(int(form["group_id"]), form["pos_name"])
            return json.dumps({
                'success': True
            })


@blueprint.route("/1/positions/delete/", methods=["POST"])
def del_position():
    form = flask.request.form
    validations = [
        validate_exists(form, "group_id") and validate_int(form["group_id"]),
        validate_exists(form, "pos_id")
    ]
    if not all(validations):
        return json.dumps({'success': False})
    else:
        helpers.delete_position(int(form["pos_id"]))
        return json.dumps({
            'success': True
        })


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
    """GET /1/positions/<int:pos_id>/"""
    return jsonify(helpers.get_position_holders(pos_id))


@blueprint.route(
    "/1/position/<int:group_id>/name/<pos_name>", methods=['POST'])
def add_position(group_id, pos_name):
    """POST /1/position/<int:group_id>/name/<pos_name>"""
