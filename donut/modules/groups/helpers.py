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
    Names that current hold the position specified by pos_id. This includes
    the case where person A holds position Y because he holds position X
    and Y is linked to X

    Arguments:
        pos_id:     The position to look up -- may be a single int or a list of int's

    Returns:
        results:    A list where each element describes a user who holds the
                    position. Each element is a dict with key:value of
                    columnname:columnvalue
    """
    if isinstance(pos_id, list):
        if not pos_id:
            return []
    else:
        pos_id = [pos_id]

    query = f"""
        SELECT DISTINCT user_id, full_name, hold_id, start_date, end_date
        FROM current_position_holders NATURAL JOIN members_full_name
        WHERE pos_id IN ({', '.join('%s' for id in pos_id)})
    """

    with flask.g.pymysql_db.cursor() as cursor:
        cursor.execute(query, pos_id)
        return cursor.fetchall()


def get_positions_held(user_id):
    ''' Returns a list of all position id's held (directly or indirectly)
    by the given user. If no positions are found, [] is returned. '''
    query = 'SELECT DISTINCT pos_id FROM current_position_holders WHERE user_id = %s'
    with flask.g.pymysql_db.cursor() as cursor:
        cursor.execute(query, user_id)
        res = cursor.fetchall()
    return [row['pos_id'] for row in res]


def get_position_id(group_name, position_name):
    ''' Returns the position id associated with the given group name and
    position name '''
    query = '''SELECT pos_id FROM positions WHERE pos_name = %s
    AND group_id = (SELECT min(group_id) FROM groups WHERE group_name = %s)'''
    with flask.g.pymysql_db.cursor() as cursor:
        cursor.execute(query, (position_name, group_name))
        res = cursor.fetchone()
    return res and res['pos_id']


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


def get_position_data(fields=None, include_houses=True, order_by=None):
    """
    Queries database for all instances where an individual holds a position.
    This includes when person A directly holds position Y, or when person A
    indirectly holds Y by holding position X and with
    an entry in the position relation table that links position X to position Y.

    Arguments:
        fields:   The fields to return. If None are specified, then
                  default_fields are used
        include_houses: Whether to include house membership positions
        order_by: Fields to order the results by, in ascending order
    Returns:
        result    A list where each element is a dict corresponding to a person holding
                  a position. key:value pairs are columnname:columnevalue
    """
    all_returnable_fields = [
        "user_id", "full_name", "group_id", "group_name", "pos_id", "pos_name",
        "start_date", "end_date"
    ]
    default_fields = [
        "user_id", "full_name", "group_id", "group_name", "pos_id", "pos_name"
    ]

    if fields is None:
        fields = default_fields
    else:
        if any(f not in all_returnable_fields for f in fields):
            return "Invalid field"

    # construct query
    query = f"""
        SELECT DISTINCT {', '.join(fields)}
        FROM positions
        NATURAL JOIN current_position_holders
        NATURAL JOIN members_full_name
        NATURAL JOIN groups
    """

    if not include_houses:
        query += ' WHERE pos_id NOT IN (SELECT pos_id FROM house_positions)'
    if order_by:
        if not all(field in fields for field in order_by):
            return "Invalid ORDER BY fields"
        query += " ORDER BY " + ', '.join(order_by)

    with flask.g.pymysql_db.cursor() as cursor:
        cursor.execute(query)
        return cursor.fetchall()


def add_position(group_id, pos_name, send=False, control=False, receive=True):
    '''
    Inserts new position into the database associated
    with the given group and with the given name

    Arguments:
        group_id: the id of the group you want to insert the position into
        pos_name: name of the position to be created
    '''
    # Construct the statement
    s = """
        INSERT INTO positions (group_id, pos_name, send, control, receive)
        VALUES (%s, %s, %s, %s, %s)
    """
    # Execute query
    with flask.g.pymysql_db.cursor() as cursor:
        cursor.execute(s, (group_id, pos_name, send, control, receive))


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


def end_position_holder(hold_id):
    """
    Sets the end of the given position hold to yesterday,
    thereby removing the user from the position.
    """
    query = """
        UPDATE position_holders
        SET end_date = SUBDATE(CURRENT_DATE, 1)
        WHERE hold_id = %s
    """
    with flask.g.pymysql_db.cursor() as cursor:
        cursor.execute(query, hold_id)


def create_group(group_name,
                 group_desc="",
                 group_type="",
                 newsgroups=False,
                 anyone_can_send=False,
                 members_can_send=False,
                 visible=False,
                 admin_control_members=True):
    """
    Creates a group with the given group_id, group name and other specifications

    Arguments:
        group_name: The group name
        group_desc: Description of group (if there is any)
        group_type: Type of group
        newgroups: Toggles if group is a news group
        anyone_can_send: Toggles if anyone can send emails to this group
        memberse_can_send: Toggles if members can send emails to this group
        visible: Toggles if the group is visible
        admin_control_members: toggles if administrator can control membership
    """
    query = """INSERT INTO groups (group_name, group_desc, type,
        newsgroups, anyone_can_send, members_can_send, visible,
        admin_control_members) VALUES (%s, %s, %s, %s, %s, %s, %s, %s)"""
    with flask.g.pymysql_db.cursor() as cursor:
        cursor.execute(query, (group_name, group_desc, group_type, newsgroups,
                               anyone_can_send, members_can_send, visible,
                               admin_control_members))
        new_group_id = cursor.lastrowid
    add_position(new_group_id, "Member")
    return new_group_id


def delete_group(group_id):
    '''
    Deletes the group specified with the group_id and all assocaited
    position holders entries and positions

    Arguments:
        group_id: id of the group to be deleted
    '''
    s = "DELETE FROM groups WHERE group_id=%s"
    with flask.g.pymysql_db.cursor() as cursor:
        cursor.execute(s, group_id)


def get_members_by_group(group_id):
    '''
    Queries the database and returns a list of all users associated with
    a particular group either because a) They hold a position in the group
    or b) They hold a position linked to another position in the group

    Arguments:
        group_id: id of group in question

    Returns:
        List where each element is a JSON representing the data of each
        person
    '''
    query = """
        SELECT DISTINCT user_id
        FROM positions NATURAL JOIN current_position_holders
        WHERE group_id = %s
    """

    with flask.g.pymysql_db.cursor() as cursor:
        cursor.execute(query, [group_id])
        result = cursor.fetchall()

    # Get data for each user id
    members = [row['user_id'] for row in result]
    result = core.get_member_data(members)
    return result


def is_user_in_group(user_id, group_id):
    """
    Returns whether the given user holds any position in the given group
    """
    query = """
        SELECT pos_id
        FROM current_position_holders NATURAL JOIN positions
        WHERE user_id = %s AND group_id = %s
        LIMIT 1
    """
    with flask.g.pymysql_db.cursor() as cursor:
        cursor.execute(query, [user_id, group_id])
        return cursor.fetchone() is not None


def get_group_id(group_name):
    """
    Returns the group_id for a group
    """
    query = """
    SELECT group_id FROM groups WHERE group_name = %s
    """
    with flask.g.pymysql_db.cursor() as cursor:
        cursor.execute(query, group_name)
        res = cursor.fetchone()
    return None if res is None else res['group_id']


def can_control(user_id, group_id):
    """
    Returns whether the given user has control privileges for the given group.
    """
    query = """
        SELECT pos_id
        FROM current_position_holders NATURAL JOIN positions
        WHERE user_id = %s AND group_id = %s AND control = 1
        LIMIT 1
    """
    with flask.g.pymysql_db.cursor() as cursor:
        cursor.execute(query, (user_id, group_id))
        return cursor.fetchone() is not None


def get_position_group(pos_id):
    """
    Returns the group_id of the group that the given position belongs to.
    """
    query = 'SELECT group_id FROM positions WHERE pos_id = %s'
    with flask.g.pymysql_db.cursor() as cursor:
        cursor.execute(query, pos_id)
        position = cursor.fetchone()
        return position and position['group_id']


def get_hold_group(hold_id):
    """
    Returns the group_id of the group that
    the given (direct) position hold belongs to.
    """
    query = """
        SELECT group_id
        FROM current_direct_position_holders NATURAL JOIN positions
        WHERE hold_id = %s
    """
    with flask.g.pymysql_db.cursor() as cursor:
        cursor.execute(query, hold_id)
        position = cursor.fetchone()
        return position and position['group_id']
