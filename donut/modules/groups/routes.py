import flask
import json
from flask import jsonify
from flask import request

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
    return jsonify(helpers.get_group_list_data(fields=fields, attrs=attrs))


@blueprint.route("/1/groups/<int:group_id>/")
def get_groups(group_id):
    """GET /1/groups/<int:group_id>/"""
    return jsonify(helpers.get_group_data(group_id))


@blueprint.route("/1/positions/<int:group_id>/", methods=['GET', 'POST'])
def positions_request(group_id):
    """POST /1/positions/<int:group_id>/"""
    if request.method == "POST":
        add_position(group_id, request.form["pos_id"], request.form["pos_name"])


