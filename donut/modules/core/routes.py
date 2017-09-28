import flask
import json

from donut.modules.core import blueprint, helpers


@blueprint.route("/1/members/")
def get_members_list():
    """GET /1/members/"""
    # Create a dict of the passed in attributes which are filterable
    filterable_attrs = [
        "uid", "last_name", "first_name", "middle_name", "email", "entry_year",
        "graduation_year", "zip"
    ]
    attrs = {
        tup: flask.request.args[tup]
        for tup in flask.request.args if tup in filterable_attrs
    }

    # Get the fields to return if they were passed in
    fields = None
    if "fields" in flask.request.args:
        fields = [f.strip() for f in flask.request.args["fields"].split(',')]

    return json.dumps(helpers.get_member_list_data(fields=fields, attrs=attrs))


@blueprint.route("/1/members/<int:user_id>/")
def get_members(user_id):
    """GET /1/members/<int:user_id>/"""
    return json.dumps(helpers.get_member_data(user_id))


@blueprint.route("/1/organizations/")
def get_organizations_list():
    """GET /1/organizations/"""
    # Create a dict of the passed in attributes which are filterable
    filterable_attrs = ["org_id", "org_name", "type"]
    attrs = {
        tup: flask.request.args[tup]
        for tup in flask.request.args if tup in filterable_attrs
    }

    # Get the fields to return if they were passed in
    fields = None
    if "fields" in flask.request.args:
        fields = [f.strip() for f in flask.request.args["fields"].split(',')]
    return json.dumps(
        helpers.get_organization_list_data(fields=fields, attrs=attrs))


@blueprint.route("/1/groups/")
def get_groups_list():
    # Create a dict of the passed in attribute which are filterable
    filterable_attrs = ["group_id", "group_name", "group_desc"]
    attrs = {
        tup: flask.request.args[tup]
        for tup in flask.request.args if tup in filterable_attrs
    }
    fields = None
    if "fields" in flask.request.args:
        fields = [f.strip() for f in flask.request.args["fields"].split(',')]
    return json.dumps(helpers.get_group_list_data(fields=fields, attrs=attrs))


@blueprint.route("/1/organizations/<int:org_id>/", methods=["GET", "POST"])
def get_organizations(org_id):
    """GET /1/organizations/<int:org_id>/"""
    return json.dumps(helpers.get_organization_data(org_id))
