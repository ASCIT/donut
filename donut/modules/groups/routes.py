import flask
import json

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
