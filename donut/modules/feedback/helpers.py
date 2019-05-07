from donut import email_utils
from donut.modules.feedback import email_templates
import flask
import pymysql.cursors


def send_update_email(group, email, complaint_id):
    '''
    Sends an email to [email] of poster and BoD
    '''
    EMAIL = "{}@donut.caltech.edu".format(group)
    msg = email_templates.added_message.format(get_link(group, complaint_id))
    subject = "Received {} Feedback".format(group)
    try:
        email_utils.send_email(', '.join((email, EMAIL)), msg, subject)
        return True
    except:
        return False


def register_complaint(group, data, notification=True):
    '''
    Inputs a complaint into the database and returns the complaint id
    associated with this complaint
    data should be a dict with keys 'course', 'msg' and optionally 'name', 'email'
    if required fields are missing, returns false
    '''
    if not (data and data['subject'] and data['msg']): return False
    # Register complaint
    query = """
    INSERT INTO {}_complaint_info (subject, status, uuid) 
    VALUES (%s, %s, UNHEX(REPLACE(UUID(), '-', '')))
    """.format(group)
    status = 'new_msg'
    with flask.g.pymysql_db.cursor() as cursor:
        cursor.execute(query, (data['subject'], status))
        complaint_id = cursor.lastrowid
    # Add email to db if applicable
    if data['email']:
        for email in data['email'].split(','):
            add_email(group, complaint_id, email.strip(), False)
    # Add message to database
    add_msg(group, complaint_id, data['msg'], data['name'], notification)
    return complaint_id


def add_email(group, complaint_id, email, notification=True):
    '''
    Adds an email to list of addresses subscribed to this complaint
    returns false if complaint_id is invalid
    '''
    if not get_subject(group, complaint_id): return False
    query = """
    INSERT INTO {}_complaint_emails (complaint_id, email)
    VALUES (%s, %s)
    """.format(group)
    with flask.g.pymysql_db.cursor() as cursor:
        try:
            cursor.execute(query, (complaint_id, email))
        except pymysql.err.IntegrityError:
            return False
    if notification:
        send_update_email(group, email, complaint_id)
    return True


def remove_email(group, complaint_id, email):
    '''
    Removes 'email' from the list of emails subscribed to this complaint
    returns False if complaint_id is invalid
    '''
    if not get_subject(group, complaint_id): return False
    query = 'DELETE FROM {}_complaint_emails WHERE complaint_id = %s AND email = %s'.format(
        group)
    with flask.g.pymysql_db.cursor() as cursor:
        cursor.execute(query, (complaint_id, email))
    return True


def add_msg(group, complaint_id, message, poster, notification=True):
    '''
    Adds a message to a complaint in the database
    and updates status of complaint to 'new_msg'
    if poster is None or an empty string, it will be replaced with
    "(anonymous)"
    If complaint_id is invalid, returns False
    '''
    if not get_subject(group, complaint_id): return False
    # Add the message
    query = """
    INSERT INTO {}_complaint_messages (complaint_id, message, poster, time)
    VALUES (%s, %s, %s, NOW())
    """.format(group)
    # Update the status to new_msg
    query2 = 'UPDATE {}_complaint_info SET status = "new_msg" WHERE complaint_id = %s'.format(
        group)
    if not poster:
        poster = '(anonymous)'
    with flask.g.pymysql_db.cursor() as cursor:
        cursor.execute(query, (complaint_id, message, poster))
        cursor.execute(query2, complaint_id)
    if notification:
        query = 'SELECT email FROM {}_complaint_emails WHERE complaint_id = %s'.format(
            group)
        with flask.g.pymysql_db.cursor() as cursor:
            cursor.execute(query, complaint_id)
            res = cursor.fetchall()
        for row in res:
            send_update_email(group, row['email'], complaint_id)


def get_link(group, complaint_id):
    '''
    Gets a (fully qualified) link to the view page for this complaint id
    '''
    query = 'SELECT HEX(uuid) AS uuid FROM {}_complaint_info WHERE complaint_id = %s'.format(
        group)
    with flask.g.pymysql_db.cursor() as cursor:
        cursor.execute(query, complaint_id)
        res = cursor.fetchone()
        if not res:
            return None
        uuid = res['uuid']
    return flask.url_for(
        'feedback.feedback_view_complaint',
        group=group,
        id=uuid,
        _external=True)


def get_id(group, uuid):
    '''
    Returns the complaint_id associated with a uuid
    or false if the uuid is not found
    '''
    query = 'SELECT complaint_id FROM {}_complaint_info WHERE uuid = UNHEX(%s)'.format(
        group)
    with flask.g.pymysql_db.cursor() as cursor:
        cursor.execute(query, uuid)
        if not cursor.rowcount:
            return False
        return cursor.fetchone()['complaint_id']


def get_messages(group, complaint_id):
    '''
    Returns timestamps, posters, messages, and message_id's on this complaint
    in ascending order of timestamp
    '''
    query = """
    SELECT time, poster, message, message_id FROM {}_complaint_messages 
    WHERE complaint_id = %s ORDER BY time
    """.format(group)
    with flask.g.pymysql_db.cursor() as cursor:
        cursor.execute(query, complaint_id)
        return cursor.fetchall()


def get_summary(group, complaint_id):
    '''
    Returns a dict with the following fields: subject, status
    '''
    query = 'SELECT subject, status FROM {}_complaint_info WHERE complaint_id = %s'.format(
        group)
    with flask.g.pymysql_db.cursor() as cursor:
        cursor.execute(query, complaint_id)
        return cursor.fetchone()


def get_subject(group, complaint_id):
    '''
    Returns the suject or None if complaint_id is invalid
    '''
    res = get_summary(group, complaint_id)
    return res['subject'] if res else None


def get_status(group, complaint_id):
    '''
    Returns the status of a post or None if complaint_id is invalid
    '''
    res = get_summary(group, complaint_id)
    return res['status'] if res else None


def mark_read(group, complaint_id):
    '''
    Sets the status of this complaint to 'read'
    returns False if complaint_id is invalid
    '''
    if get_status(group, complaint_id) is None:
        return False
    query = "UPDATE {}_complaint_info SET status = 'read' WHERE complaint_id = %s".format(
        group)
    with flask.g.pymysql_db.cursor() as cursor:
        cursor.execute(query, complaint_id)


def mark_unread(group, complaint_id):
    '''
    Sets the status of this complaint to 'new_msg'
    returns False if complaint_id is invalid
    '''
    if get_status(group, complaint_id) is None:
        return False
    query = "UPDATE {}_complaint_info SET status = 'new_msg' WHERE complaint_id = %s".format(
        group)
    with flask.g.pymysql_db.cursor() as cursor:
        cursor.execute(query, complaint_id)


def get_emails(group, complaint_id):
    '''
    Returns a list of subscribed emails for this complaint (which may be empty)
    or an empty list if complaint_id is invalid
    '''
    query = 'SELECT email FROM {}_complaint_emails WHERE complaint_id = %s'.format(
        group)
    with flask.g.pymysql_db.cursor() as cursor:
        cursor.execute(query, complaint_id)
        res = cursor.fetchall()
    return [row['email'] for row in res]


def get_all_fields(group, complaint_id):
    '''
    Returns a dict with emails, messages, subject, status
    Returns None if complaint_id is invalid
    '''
    if not get_subject(group, complaint_id):
        return None
    data = {
        'emails': get_emails(group, complaint_id),
        'messages': get_messages(group, complaint_id),
        'subject': get_subject(group, complaint_id),
        'status': get_status(group, complaint_id)
    }
    return data


def get_new_posts(group):
    '''
    Returns all posts with status 'new_msg' and their associated list
    of messages. Will be an array of dicts with keys complaint_id, subject,
    status, uuid, message, poster, time
    Note that message and poster refer to the latest comment on this complaint
    '''
    query = """SELECT post.complaint_id AS complaint_id, post.subject AS subject,
    post.status AS status, post.uuid AS uuid, comment.message AS message, 
    comment.poster AS poster, comment.time AS time 
    FROM {0}_complaint_info post
    NATURAL JOIN {0}_complaint_messages comment
    INNER JOIN (
    SELECT complaint_id, max(time) AS time 
    FROM {0}_complaint_messages GROUP BY complaint_id
    ) maxtime
    ON maxtime.time = comment.time AND maxtime.complaint_id = comment.complaint_id
    WHERE post.status = 'new_msg'
    """.format(group)
    with flask.g.pymysql_db.cursor() as cursor:
        cursor.execute(query)
        return cursor.fetchall()