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

    query = "SELECT " + ', '.join(fields) + " FROM groups "
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
    query = "SELECT pos_id, pos_name FROM positions "
    query += "WHERE group_id = %s"

    with flask.g.pymysql_db.cursor() as cursor:
        cursor.execute(query, [group_id])
        return list(cursor.fetchall())


def get_position_holders(pos_id):
    """
    Queries the database and returns a list of all members and their
    Names that currently hold the position specified by pos_id

    Arguments:
        pos_id:     The position to look up

    Returns:
        results:    A list where each element describes a user who holds the
                    position. Each element is a dict with key:value of
                    columnname:columnvalue
    """
    fields = ["user_id", "first_name", "last_name", "start_date", "end_date"]
    query = "SELECT " + ', '.join(fields) + " "
    query += "FROM position_holders NATURAL JOIN members "
    query += "WHERE pos_id = %s"

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

    query = "SELECT " + ', '.join(fields) + " FROM groups "
    query += "WHERE group_id = %s"

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
    query += "FROM members NATURAL JOIN positions NATURAL JOIN groups "
    query += "NATURAL JOIN position_holders "

    with flask.g.pymysql_db.cursor() as cursor:
        cursor.execute(query)
        return cursor.fetchall()


def add_position(group_id, pos_name):
    ''' 
    Inserts new position into the database associated
    with the given group and with the given name

    Arguments: 
        group_id: the id of the group you want to insert the position into
        pos_name: name of the position to be created
    '''
    # Construct the statement
    s = "INSERT INTO positions (group_id, pos_name) VALUES (%s, %s)"
    # Execute query
    with flask.g.pymysql_db.cursor() as cursor:
        cursor.execute(s, (group_id, pos_name))


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
    # Execute query
    with flask.g.pymysql_db.cursor() as cursor:
        cursor.execute(s)
    # Same as above but now delete from positions table
    s = "DELETE FROM positions WHERE pos_id=%d"
    s = s % pos_id
    with flask.g.pymysql_db.cursor() as cursor:
        cursor.execute(s)


def create_position_holder(pos_id, user_id, start_date, end_date):
    '''
    Inserts row into position_holders table

    Arguments:
        pos_id: id of the position
        user_id: user id of the person that the position is to be assigned
        start_date: Starting date of the holding period, format is 'yyyy-mm-dd'
        end_date: end date of the hold period
    '''
    s = """INSERT INTO position_holders (pos_id, user_id, start_date, 
    end_date) VALUES (%s, %s, %s, %s)"""
    with flask.g.pymysql_db.cursor() as cursor:
        cursor.execute(s, (pos_id, user_id, start_date, end_date))


def get_members_by_group(group_id):
    '''
    Queries the database and returns a list of all users associated with
    a particular group either because a) They hold a position in the group
    or b) They hold a position linked to another position in the group

    Arguments:
        group_id: id of group in question
    
    Returns:
        List where each element is a JSON reprenting the data of each
        person
    '''
    query = "SELECT DISTINCT user_id FROM positions p LEFT JOIN "
    query += "position_relations pr ON p.pos_id=pr.pos_id_to "
    query += "INNER JOIN position_holders ph ON ph.pos_id=p.pos_id OR "
    query += "pr.pos_id_from=ph.pos_id "
    query += "WHERE group_id = %s"

    with flask.g.pymysql_db.cursor() as cursor:
        cursor.execute(query, [group_id])
        result = cursor.fetchall()

    # Get data for each user id
    members = [row['user_id'] for row in result]
    result = core.get_member_data(members)
    return result
