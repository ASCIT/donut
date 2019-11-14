from donut import email_utils
import flask
from donut.modules.core.helpers import get_name_and_email

def get_past_messages(group_id, limit=10):
    """Returns a list of past sent messages"""
    query = """
    SELECT subject, message, time_sent, user_id FROM
    newsgroup_posts WHERE group_id = %s LIMIT %s
    """
    with flask.g.pymysql_db.cursor() as cursor:
        cursor.execute(query, (group_id, limit))
        res = cursor.fetchall()
    for message in res:
        ### TODO: make a view messages page or smth
        message['url'] = flask.url_for("home") 
        # message['user_url'] = flask.url_for('directory_search.view_user', user_id=user_id)
        # message['name'] = get_name_and_email(user_id)['full_name']
    return res

def get_newsgroups():
    """Gets all newsgroups."""

    query = '''
    SELECT group_name, group_id FROM groups 
    WHERE newsgroups=1
    '''
    with flask.g.pymysql_db.cursor() as cursor:
        cursor.execute(query)
        res = cursor.fetchall()
    return res

def get_my_newsgroups(user_id):
    """Gets list of user is a member of."""

    query = '''
    SELECT group_name, group_id 
    FROM groups NATURAL JOIN positions
    NATURAL JOIN position_holders
    WHERE user_id=%s
    AND groups.newsgroups=1
    '''
    with flask.g.pymysql_db.cursor() as cursor:
        cursor.execute(query, user_id)
        res = cursor.fetchall()
    return res

def get_can_send_groups(user_id):
    query = '''
    SELECT group_name, group_id
    FROM groups NATURAL JOIN positions
    NATURAL JOIN position_holders
    WHERE user_id= %s
    AND groups.newsgroups=1
    AND positions.send=1
    UNION DISTINCT
    SELECT group_name, group_id
    FROM groups 
    WHERE groups.newsgroups=1
    AND groups.anyone_can_send=1
    '''
    res = None
    with flask.g.pymysql_db.cursor() as cursor:
        cursor.execute(query, user_id)
        res = cursor.fetchall()
    return res

def get_user_actions(user_id, group_id):
    """Gets allowed actions for user."""

    if not user_id:
        return None
    query = """
    SELECT p.send AS send, p.control AS control, p.receive AS receive
    FROM groups NATURAL JOIN positions p 
    NATURAL JOIN position_holders
    WHERE user_id=%s AND groups.group_id=%s
    """
    with flask.g.pymysql_db.cursor() as cursor:
        cursor.execute(query, (user_id, group_id))
        res = cursor.fetchone()
    return res

def apply_subscription(user_id, group_id):
    # TODO
    pass

def unsubscribe(user_id, group_id):
    if not username:
        return None
    # TODO
    pass

def send_email(data):
   """Sends email to newsgroup."""

   query = """
   SELECT DISTINCT members.email
   FROM positions p 
   LEFT JOIN position_relations pr ON p.pos_id=pr.pos_id_to
   INNER JOIN position_holders ph 
   ON ph.pos_id=p.pos_id OR pr.pos_id_from=ph.pos_id
   NATURAL JOIN members
   WHERE group_id=%s AND p.receive=1
   """
   emails = []
   with flask.g.pymysql_db.cursor() as cursor:
       cursor.execute(query, data['group'])
       emails = [item['email'] for item in cursor.fetchall()]
   if not emails:
       return True
   emails = list(set(emails))
   try:
       email_utils.newsgroup_send_email(
               emails, 
               data['group_name'],
               data['subject'], 
               data['msg'])
       return True
   except:
       return False

def insert_email(user_id, data):
    query = """
    INSERT INTO newsgroup_posts 
    VALUES (NULL, %s, %s, %s, %s, NULL)
    """
    with flask.g.pymysql_db.cursor() as cursor:
       cursor.execute(query, (data['group'], data['subject'], 
           data['msg'], user_id))
