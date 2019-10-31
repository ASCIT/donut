import flask

def get_newsgroups():
    """Gets list of newsgroups."""

    query = 'SELECT group_name, group_id FROM groups WHERE newsgroups = TRUE'
    with flask.g.pymysql_db.cursor() as cursor:
        cursor.execute(query)
        res = cursor.fetchall()
    return res

def get_my_newsgroups(username):
    """Gets list of user is a member of."""

    query = '''
    SELECT group_name, group_id 
    FROM groups NATURAL JOIN positions
    NATURAL JOIN position_holders
    NATURAL JOIN users 
    WHERE users.username = %s
    AND groups.newsgroups = TRUE
    '''
    with flask.g.pymysql_db.cursor() as cursor:
        cursor.execute(query, username)
        res = cursor.fetchall()
    return res

def get_can_send_groups(username):
    query = '''
    SELECT group_name, group_id
    FROM groups NATURAL JOIN positions
    NATURAL JOIN position_holders
    NATURAL JOIN users
    WHERE users.username = %s
    AND groups.newsgroups = TRUE
    AND positions.send = TRUE
    UNION DISTINCT
    SELECT group_name, group_id
    FROM groups NATURAL JOIN positions
    NATURAL JOIN position_holders
    WHERE groups.newsgroups = TRUE
    AND groups.anyone_can_send = TRUE
    '''
    res = None
    with flask.g.pymysql_db.cursor() as cursor:
        cursor.execute(query, username)
        res = cursor.fetchall()
    return res

def get_newsgroup_info(group_id):
    """Gets info for newsgroup."""

    query = """
    SELECT group_name, group_desc, anyone_can_send, members_can_send, visible, admin_control_members 
    FROM groups WHERE group_id = %s
    """
    with flask.g.pymysql_db.cursor() as cursor:
        cursor.execute(query, group_id)
        res = cursor.fetchone()
    return res

def get_user_actions(username, group_id):
    """Gets allowed actions for user."""

    if not username:
        return None
    query = """
    SELECT p.send AS send, p.control AS control, p.receive AS receive
    FROM groups NATURAL JOIN positions p NATURAL JOIN position_holders NATURAL JOIN users
    WHERE users.username = %s AND groups.group_id = %s
    """
    with flask.g.pymysql_db.cursor() as cursor:
        cursor.execute(query, (username, group_id))
        res = cursor.fetchone()
    return res

def apply_subscription(username, group_id):
    # TODO
    pass

def positions_held(username, group_id):
    query = """
    SELECT p.pos_id
    FROM groups NATURAL JOIN positions p NATURAL JOIN position_holders NATURAL JOIN users
    WHERE users.username = %s AND groups.group_id = %s
    """
    res = None
    with flask.g.pymysql_db.cursor() as cursor:
        cursor.execute(query, (username, group_id))
        res = cursor.fetchall()
    return res
