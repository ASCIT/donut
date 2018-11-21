import flask
import json
from flask import jsonify

from donut.modules.groups import blueprint, helpers
from donut.validation_utils import validate_exists, validate_int, validate_date


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
    return jsonify(helpers.get_group_list_data(fields=fields, attrs=attrs))


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
            validate_exists(form, "pos_name"),
        ]
        if not all(validations):
            return jsonify({'success': False})
        else:
            helpers.add_position(int(form["group_id"]), form["pos_name"])
            return jsonify({'success': True})


@blueprint.route("/1/positions/delete/", methods=["POST"])
def del_position():
    form = flask.request.form
    validations = [
        validate_exists(form, "group_id") and validate_int(form["group_id"]),
        validate_exists(form, "pos_id")
    ]
    if not all(validations):
        return jsonify({'success': False})
    helpers.delete_position(int(form["pos_id"]))
    return jsonify({'success': True})


@blueprint.route("/1/groups/<int:group_id>/")
def get_groups(group_id):
    """GET /1/groups/<int:group_id>/"""
    return jsonify(helpers.get_group_data(group_id))


@blueprint.route("/1/groups/<int:group_id>/members/")
def get_group_members(group_id):
    """GET /1/groups/<int:group_id>/"""
    return jsonify(helpers.get_members_by_group(group_id))


@blueprint.route("/1/positions/<int:pos_id>/direct/", methods=["GET"])
def get_direct_pos_holders(pos_id):
    """GET /1/positions/<int:pos_id>/direct"""
    return jsonify(helpers.get_direct_position_holders(pos_id))


@blueprint.route("/1/positions/<int:pos_id>/", methods=["GET"])
def get_pos_holders(pos_id):
    """GET /1/positions/<int:pos_id>/"""
    return jsonify(helpers.get_position_holders(pos_id))


@blueprint.route("/1/positions/<int:pos_id>/", methods=["POST"])
def create_pos_holder(pos_id):
    form = flask.request.form
    validations = [
        validate_exists(form, "user_id") and validate_int(form["user_id"]),
        validate_exists(form, "start_date")
        and validate_date(form["start_date"]),
        validate_exists(form, "end_date") and validate_date(form["end_date"])
    ]
    if not all(validations):
        return jsonify({'success': False})
    helpers.create_position_holder(pos_id,
                                   int(form["user_id"]), form["start_date"],
                                   form["end_date"])
    return jsonify({'success': True})


@blueprint.route("/1/positions/<int:pos_id>/delete/", methods=["POST"])
def delete_pos_holder(pos_id):
    form = flask.request.form
    validations = [
        validate_exists(form, "user_id") and validate_int(form["user_id"]),
    ]
    if not all(validations):
        return jsonify({'success': False})
    helpers.delete_position_holder(pos_id, form["user_id"])
    return jsonify({'success': True})
