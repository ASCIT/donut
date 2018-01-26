import flask
import sqlalchemy
from donut.modules.core import helpers as core


def get_group_list_data(fields=None, attrs={}):
    """
    Queries the database and returns list of group data constrained by the
    specified attributes.

    Arguments:
        fields: The fields to return. If None specified, then default_fields
                are used.
        attrs:  The attributes of the group to filter for.
    Returns:
        result: The fields and corresponding values of groups with desired
                attributes. In the form of a list of dicts with key:value of
                columnname:columnvalue.
    """
    all_returnable_fields = [
        "group_id", "group_name", "group_desc", "type", "anyone_can_send",
        "members_can_send", "newsgroups", "visible", "admin_control_members"
    ]
    default_fields = ["group_id", "group_name", "group_desc", "type"]
    if fields == None:
        fields = default_fields
    else:
        if any(f not in all_returnable_fields for f in fields):
            return "Invalid field"

    # Build the SELECT and FROM clauses
    s = sqlalchemy.sql.select(fields).select_from(sqlalchemy.text("groups"))

    # Build the WHERE clause
    for key, value in list(attrs.items()):
        s = s.where(sqlalchemy.text(key + "= :" + key))

    # Execute the query
    result = flask.g.db.execute(s, attrs).fetchall()

    # Return the rows in the form of a list of dicts
    result = [{f: t for f, t in zip(fields, res)} for res in result]
    return result


group_position_fields = ["pos_id", "pos_name"]


def get_group_positions(group_id):
    """
    Returns a list of all positions for a group with the given id.

    Arguments:
        group_id: The integer id of the group
    """

    query = sqlalchemy.sql.select(group_position_fields).select_from(
        sqlalchemy.text("positions"))
    query = query.where(sqlalchemy.text("group_id = :group_id"))
    positions = flask.g.db.execute(query, group_id=group_id).fetchall()
    return [{
        field: value
        for field, value in zip(group_position_fields, position)
    } for position in positions]


def get_position_holders(pos_id):
    """
    Queries the database and returns a list of all members and their
    Names that current hold the position specified by pos_id

    Arguments:
        pos_id:     The position to look up
    
    Returns:
        results:    A list where each element describes a user who holds the
                    position. Each element is a dict with key:value of
                    columnname:columnvalue
    """
    fields = ["user_id", "first_name", "last_name", "start_date", "end_date"]
    s = sqlalchemy.sql.select(fields).select_from(
        sqlalchemy.text(" position_holders NATURAL JOIN members"))
    s = s.where(sqlalchemy.text("pos_id = :p"))
    result = flask.g.db.execute(s, p=pos_id)

    result = [{f: t for f, t in zip(fields, res)} for res in result]
    return result


def get_group_data(group_id, fields=None):
    """
    Queries the databse and returns member data for the specified group_id.

    Arguments:
        group_id: The group to look up
        fields:   The fields to return. If None are specified, then
                  default_fields are used

    Returns:
        result:   The fields and corresponding values of group with group_id.
                  In the form of a dict with key:value of columnname:columnalue
    """
    all_returnable_fields = [
        "group_id", "group_name", "group_desc", "type", "anyone_can_send",
        "members_can_send", "newsgroups", "visible", "admin_control_members"
    ]
    default_fields = ["group_id", "group_name", "group_desc", "type"]
    if fields is None:
        fields = default_fields
    else:
        if any(f not in all_returnable_fields for f in fields):
            return "Invalid field"

    # Build the SELECT and FROM clauses
    s = sqlalchemy.sql.select(fields).select_from(sqlalchemy.text("groups"))

    # Build the WHERE clause
    s = s.where(sqlalchemy.text("group_id = :g"))

    # Execute the query
    result = flask.g.db.execute(s, g=group_id).first()

    # Check to see if query returned anything
    if result is None:
        return {}

    # Return the row in the form of a dict
    result = {f: t for f, t in zip(fields, result)}
    return result


def get_members_by_group(group_id):
    # Build the SELECT and FROM clauses
    fields = [sqlalchemy.text("user_id")]
    s = sqlalchemy.sql.select(fields).select_from(
        sqlalchemy.text("group_members"))

    # Build the WHERE clause
    s = s.where(sqlalchemy.text("group_id = :g"))

    # Execute the query
    result = flask.g.db.execute(s, g=group_id).fetchall()

    # Get data for each user id
    members = [row['user_id'] for row in result]
    result = core.get_member_data(members)
    return result
