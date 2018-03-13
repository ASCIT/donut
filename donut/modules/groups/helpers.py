import flask
import pymysql.cursors
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

    query = "SELECT " + ', '.join(fields) + " FROM `groups` "
    if attrs:
        query += "WHERE "
        query += " AND ".join([key + "= %s" for key in attrs.keys()])
    values = list(attrs.values())

    # Execute the query
    with flask.g.pymysql_db.cursor() as cursor:
        cursor.execute(query, values)
        return list(cursor.fetchall())


def get_group_positions(group_id):
    """
    Returns a list of all positions for a group with the given id.

    Arguments:
        group_id: The integer id of the group
    """
    query = "SELECT `pos_id`, `pos_name` FROM `positions` "
    query += "WHERE `group_id` = %s"

    with flask.g.pymysql_db.cursor() as cursor:
        cursor.execute(query, [group_id])
        return list(cursor.fetchall())


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
    query = "SELECT " + ', '.join(fields) + " "
    query += "FROM `position_holders` NATURAL JOIN `members` "
    query += "WHERE `pos_id` = %s"

    with flask.g.pymysql_db.cursor() as cursor:
        cursor.execute(query, [pos_id])
        return cursor.fetchall()


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

    query = "SELECT " + ', '.join(fields) + " FROM `groups` "
    query += "WHERE `group_id` = %s"

    with flask.g.pymysql_db.cursor() as cursor:
        cursor.execute(query, [group_id])
        result = cursor.fetchone()

    return result or {}


def get_position_data(fields=None):
    all_returnable_fields = [
        "user_id", "group_id", "pos_id", "first_name", "last_name",
        "start_date", "end_date", "group_name", "pos_name"
    ]
    default_fields = [
        "user_id", "group_id", "pos_id", "first_name", "last_name",
        "start_date", "end_date", "group_name", "pos_name"
    ]

    if fields is None:
        fields = default_fields
    else:
        if any(f not in all_returnable_fields for f in fields):
            return "Invalid field"

    query = "SELECT " + ', '.join(fields) + " "
    query += "FROM `members` NATURAL JOIN `positions` NATURAL JOIN `groups` "
    query += "NATURAL JOIN `position_holders` "

    with flask.g.pymysql_db.cursor() as cursor:
        cursor.execute(query)
        return cursor.fetchall()


def get_members_by_group(group_id):
    query = "SELECT `user_id` FROM `group_members` "
    query += "WHERE `group_id` = %s"

    with flask.g.pymysql_db.cursor() as cursor:
        cursor.execute(query, [group_id])
        result = cursor.fetchall()

    # Get data for each user id
    members = [row['user_id'] for row in result]
    result = core.get_member_data(members)
    return result
