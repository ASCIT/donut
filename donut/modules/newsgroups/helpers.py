from donut import email_utils
import flask
import smtplib
from donut.modules.core.helpers import get_name_and_email

def get_past_messages(group_id, limit=5):
    """Returns a list of past sent messages"""

    query = """
    SELECT newsgroup_post_id, subject, message, time_sent, user_id 
    FROM newsgroup_posts WHERE group_id=%s LIMIT %s
    """
    with flask.g.pymysql_db.cursor() as cursor:
        cursor.execute(query, (group_id, limit))
        res = cursor.fetchall()
    # Generate who sent the message
    for i in res:
        i['name'] = get_name_and_email(i['user_id'])[0]
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
        cursor.execute(query, [user_id])
        res = cursor.fetchall()
    return res

def get_can_send_groups(user_id):
    """Gets groups that user is allowed to post to."""

    query = '''
    SELECT group_name, group_id
    FROM groups NATURAL JOIN positions
    NATURAL JOIN position_holders
    WHERE user_id=%s 
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
        cursor.execute(query, [user_id])
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
    '''
    Inserts into groups table with the position "Applicant"
    '''
    # TODO: Make sure each is unique!
    query = """
    INSERT INTO group_applications(group_id, user_id)
    VALUES (%s, %s)
    """    
    with flask.g.pymysql_db.cursor() as cursor:
        cursor.execute(query, (group_id, user_id))

def unsubscribe(user_id, group_id):
    if not user_id:
        return None
    # TODO
    pass

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
        (name, email) = get_name_and_email(i['user_id'])
        i['name'] = name
        i['email'] = email
    return res
    
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
   emails = None
   with flask.g.pymysql_db.cursor() as cursor:
       cursor.execute(query, data['group'])
       emails = [item['email'] for item in cursor.fetchall()]
   if not emails:
       return True
   try:
       email_utils.newsgroup_send_email(
               emails, 
               data['group_name'],
               data['poster'],
               data['subject'], 
               data['msg'])
       return True
   except smtplib.SMTPException:
       return False

def insert_email(user_id, data):
    query = """
    INSERT INTO newsgroup_posts 
    (group_id, subject, message, post_as, user_id)
    VALUES (%s, %s, %s, %s, %s)
    """
    with flask.g.pymysql_db.cursor() as cursor:
       cursor.execute(query, (data['group'], data['subject'], 
           data['msg'], data['poster'], user_id))

def get_post(post_id):
    query = """
    SELECT group_name, group_id, subject, message, post_as, user_id, time_sent 
    FROM newsgroup_posts
    NATURAL JOIN groups
    WHERE newsgroup_post_id=%s
    """
    res = None
    with flask.g.pymysql_db.cursor() as cursor:
       cursor.execute(query, post_id)
       res = cursor.fetchone()
    return res

def get_owners(group_id):
    query = """
    SELECT user_id 
    FROM positions NATURAL JOIN position_holders 
    WHERE positions.control=1
    AND positions.group_id=%s
    """
    res = None
    with flask.g.pymysql_db.cursor() as cursor:
        cursor.execute(query, group_id)
        res = cursor.fetchall()
    return res

def post_as(group_id, user_id):
    query = """
    SELECT pos_name, pos_id 
    FROM positions NATURAL JOIN position_holders
    WHERE positions.group_id=%s
    AND position_holders.user_id=%s
    AND positions.send=1
    """
    res = None
    with flask.g.pymysql_db.cursor() as cursor:
        cursor.execute(query, (group_id, user_id))
        res = cursor.fetchall()
    return res
