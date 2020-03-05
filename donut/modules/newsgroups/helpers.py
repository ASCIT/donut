from donut import email_utils
import flask
import smtplib
from donut.modules.core.helpers import get_name_and_email
from donut.modules.groups import helpers as groups


def get_past_messages(group_id, limit=5):
    """Returns a list of past sent messages"""

    query = """
    SELECT newsgroup_post_id, subject, message, time_sent, user_id, post_as
    FROM newsgroup_posts WHERE group_id=%s ORDER BY time_sent DESC LIMIT %s
    """
    with flask.g.pymysql_db.cursor() as cursor:
        cursor.execute(query, (group_id, limit))
        return cursor.fetchall()


def get_newsgroups():
    """Gets all newsgroups."""

    query = '''
    SELECT group_name, group_id FROM groups 
    WHERE newsgroups=1
    '''
    with flask.g.pymysql_db.cursor() as cursor:
        cursor.execute(query)
        return cursor.fetchall()


def get_my_newsgroups(user_id, send=False):
    """Gets groups user is a member of (includes indirectly).
    If send is true, only gets newsgroups user can send to
    """

    query = '''SELECT DISTINCT g.group_name, g.group_id
    FROM positions p LEFT JOIN position_relations pr
    ON p.pos_id=pr.pos_id_to
    INNER JOIN position_holders ph ON ph.pos_id=p.pos_id OR
    pr.pos_id_from=ph.pos_id
    INNER JOIN groups g ON p.group_id=g.group_id
    WHERE ph.user_id=%s AND g.newsgroups=1'''
    if send:
        query += ''' AND p.send=1 
        UNION DISTINCT SELECT group_name, group_id
        FROM groups 
        WHERE groups.newsgroups=1
        AND groups.anyone_can_send=1'''
    with flask.g.pymysql_db.cursor() as cursor:
        cursor.execute(query, user_id)
        return cursor.fetchall()


def get_user_actions(user_id, group_id):
    """Gets allowed actions for user."""

    if not user_id:
        return None
    query = """
    SELECT p.send AS send, p.control AS control, p.receive AS receive
    FROM positions p LEFT JOIN position_relations pr
    ON p.pos_id=pr.pos_id_to
    INNER JOIN position_holders ph ON ph.pos_id=p.pos_id OR
    pr.pos_id_from=ph.pos_id
    WHERE ph.user_id=%s AND p.group_id=%s"""
    res = None
    with flask.g.pymysql_db.cursor() as cursor:
        cursor.execute(query, (user_id, group_id))
        res = cursor.fetchall()
    actions = {'send': False, 'control': False, 'receive': False}
    if not res:
        return actions
    else:
        for a in actions:
            for pos in res:
                if pos[a]:
                    actions[a] = True
                    break
        return actions


def apply_subscription(user_id, group_id):
    '''
    Inserts into groups table with the position "Applicant"
    '''
    query = """
    INSERT INTO group_applications(group_id, user_id)
    VALUES (%s, %s) ON DUPLICATE KEY update user_id=user_id
    """
    with flask.g.pymysql_db.cursor() as cursor:
        cursor.execute(query, (group_id, user_id))


def unsubscribe(user_id, group_id):
    if not user_id:
        return None
    query = """
    UPDATE position_holders 
    SET receive = 0
    WHERE user_id = %s AND pos_id IN (
    SELECT p.pos_id FROM positions p LEFT JOIN position_relations pr
    ON p.pos_id=pr.pos_id_to
    INNER JOIN position_holders ph ON ph.pos_id=p.pos_id OR
    pr.pos_id_from=ph.pos_id
    WHERE ph.user_id=%s AND p.group_id=%s)
    """
    with flask.g.pymysql_db.cursor() as cursor:
        cursor.execute(query, (user_id, user_id, group_id))


def get_applications(group_id):
    '''
    Selects all applicants to a newgroups 
    '''
    query = """
    SELECT * FROM group_applications WHERE group_id = %s
    """
    with flask.g.pymysql_db.cursor() as cursor:
        cursor.execute(query, (group_id))
        res = cursor.fetchall()
    for i in res:
        data = get_name_and_email(i['user_id'])
        i['name'] = data['full_name']
        i['email'] = data['email']
    return res


def remove_application(user_id, group_id):
    '''
    Admin has denied a person for their newgroup membership. 
    '''
    query = """
    DELETE FROM group_applications 
    WHERE user_id = %s AND group_id = %s
    """
    with flask.g.pymysql_db.cursor() as cursor:
        cursor.execute(query, (user_id, group_id))


def send_email(data):
    """Sends email to newsgroup."""

    query = """
   SELECT DISTINCT members.email
   FROM positions p 
   LEFT JOIN position_relations pr ON p.pos_id=pr.pos_id_to
   INNER JOIN position_holders ph 
   ON ph.pos_id=p.pos_id OR pr.pos_id_from=ph.pos_id
   NATURAL JOIN members
   WHERE group_id=%s AND p.receive=1 AND ph.receive=1
   """
    emails = None
    with flask.g.pymysql_db.cursor() as cursor:
        cursor.execute(query, data['group'])
        emails = ','.join([item['email'] for item in cursor.fetchall()])
    if not emails:
        return True
    try:
        email_utils.send_email(
            emails, data['msg'], data['subject'], group=data['group'])
        return True
    except smtplib.SMTPException:
        return False


def insert_email(user_id, data):
    """Insert email into db."""

    query = """
    INSERT INTO newsgroup_posts 
    (group_id, subject, message, user_id, post_as)
    VALUES (%s, %s, %s, %s, %s)
    """
    with flask.g.pymysql_db.cursor() as cursor:
        cursor.execute(query, (data['group'], data['subject'], data['msg'],
                               user_id, data['poster']))


def get_post(post_id):
    query = """
    SELECT group_name, group_id, subject, message, post_as, user_id, time_sent 
    FROM newsgroup_posts
    NATURAL JOIN groups
    WHERE newsgroup_post_id=%s
    """
    with flask.g.pymysql_db.cursor() as cursor:
        cursor.execute(query, post_id)
        return cursor.fetchone()


def get_owners(group_id):
    """Get users with control access to group."""

    query = """
    SELECT ph.user_id, p.pos_name 
    FROM positions p 
    LEFT JOIN position_relations pr ON p.pos_id=pr.pos_id_to
    INNER JOIN position_holders ph
    ON ph.pos_id=p.pos_id OR pr.pos_id_from=ph.pos_id
    WHERE p.control=1
    AND p.group_id=%s
    """
    with flask.g.pymysql_db.cursor() as cursor:
        cursor.execute(query, group_id)
        return cursor.fetchall()


def get_posting_positions(group_id, user_id):
    """Get positions user can send as in a group."""

    query = """
    SELECT p.pos_name, p.pos_id 
    FROM positions p INNER JOIN position_holders ph 
    ON p.pos_id=ph.pos_id
    WHERE p.group_id=%s
    AND ph.user_id=%s
    AND p.send=1
    """
    with flask.g.pymysql_db.cursor() as cursor:
        cursor.execute(query, (group_id, user_id))
        return cursor.fetchall()
