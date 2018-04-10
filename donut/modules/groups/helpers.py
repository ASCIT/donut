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
    
    s = "SELECT "
    for i in range(len(group_position_fields)):
        if i == len(group_position_fields) - 1:
            s = s + group_position_fields[i]
        else:
            s = s + group_position_fields[i] + ","
    s = s + " FROM positions WHERE group_id=" + str(group_id)
    with flask.g.pymysql_db.cursor() as cursor:
        cursor.execute(s)
        result = cursor.fetchall()
    if len(result) == 0:
        return []
    return result


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

    
    s = "SELECT "
    for i in range(len(fields)):
        if i == len(fields) - 1:
            s = s + fields[i]
        else:
            s = s + fields[i] + ","
    s = s + " FROM members NATURAL JOIN positions NATURAL JOIN groups"\
            " NATURAL JOIN position_holders"
    with flask.g.pymysql_db.cursor() as cursor:
        cursor.execute(s)
        result = cursor.fetchall()

    print(result)

    if result is None:
        return {}

    return result


def add_position(group_id, pos_name):
    ''' 
    Inserts new position into the database associated
    with the given group and with the given name

    Arguments: 
        group_id: the id of the group you want to insert the position into
        pos_name: name of the position to be created
    '''
    # Construct the statement
    s = "INSERT INTO positions (group_id, pos_name) VALUES (%d, '%s')"
    s = s % (group_id, pos_name)
    # Execute query
    with flask.g.pymysql_db.cursor() as cursor:
        cursor.execute(s)


def delete_position(pos_id):
    '''
    Deletes the position specified with the pos_id and all assocaited
    position holders entries

    Arguments:
        pos_id: id of the position to be deleted
    '''
    # Construct statements
    s = "DELETE FROM position_holders WHERE pos_id=%d"
    s = s % pos_id
    print(s)
    # Execute query
    with flask.g.pymysql_db.cursor() as cursor:
        cursor.execute(s)
    # Same as above but now delete from positions table
    s = "DELETE FROM positions WHERE pos_id=%d"
    s = s % pos_id
    print(s)
    with flask.g.pymysql_db.cursor() as cursor:
        cursor.execute(s)


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
