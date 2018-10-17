from donut import email_utils
from donut.modules.bodfeedback import email_templates
import flask
import pymysql.cursors


def send_update_email(email, complaint_id):
    """
    Sends a confirmation email to [address] which should be an
    email address of a user as a string
    """
    msg = email_templates.added_message.format(get_link(complaint_id))
    subject = "Received BoD Feedback"
    email_utils.send_email(email, msg, subject)


def register_complaint(data, notification=True):
    """
    Inputs a complaint into the database and returns the complaint id
    associated with this complaint
    data should be a dict with keys 'course', 'msg' and optionally 'name', 'email'
    if required fields are missing, returns false
    """
    if not data or not data['subject'] or not data['msg']: return False
    # register complaint
    query = """
    INSERT INTO bod_complaint_info (subject, status, uuid)
    VALUES (%s, %s, UUID())
    """
    status = 'new_msg'
    with flask.g.pymysql_db.cursor() as cursor:
        cursor.execute(query, (data['subject'], status))
    complaint_id = cursor.lastrowid
    # add email to db if applicable
    if data['email'] != "":
        emails = [x.strip() for x in data['email'].split(',')]
        for e in emails:
            add_email(complaint_id, e, False)
    # add message to database
    add_msg(complaint_id, data['msg'], data['name'], notification)
    return complaint_id


def add_email(complaint_id, email, notification=True):
    """
    Adds an email to list of addresses subscribed to this complaint
    returns false if complaint_id is invalid
    """
    if not get_subject(complaint_id): return False
    query = """
    INSERT INTO bod_complaint_emails (complaint_id, email)
    VALUES (%s, %s)
    """
    with flask.g.pymysql_db.cursor() as cursor:
        cursor.execute(query, (complaint_id, email))
    if notification:
        send_update_email(email, complaint_id)
    return True


def remove_email(complaint_id, email):
    '''
    Removes 'email' from the list of emails subscribed to this complaint
    returns False if complaint_id is invalid
    '''
    if not get_subject(complaint_id): return False
    query = """
    DELETE FROM bod_complaint_emails WHERE complaint_id = %s AND email = %s
    """
    with flask.g.pymysql_db.cursor() as cursor:
        cursor.execute(query, (complaint_id, email))
    return True


def add_msg(complaint_id, message, poster, notification=True):
    '''
    Adds a message to a complaint in the database
    and updates status of complaint to 'new_msg'
    if poster is None or an empty string, it will be replaced with
    "(anonymous)"
    If complaint_id is invalid, returns False
    '''
    if not get_subject(complaint_id): return False
    #add the message
    query = """
    INSERT INTO bod_complaint_messages (complaint_id, message, poster, time)
    VALUES (%s, %s, %s, NOW())
    """
    # update the status to new_msg
    query2 = """
    UPDATE bod_complaint_info SET status = 'new_msg' WHERE complaint_id = %s
    """
    if poster == "" or poster is None:
        poster = '(anonymous)'
    with flask.g.pymysql_db.cursor() as cursor:
        cursor.execute(query, (complaint_id, message, poster))
        cursor.execute(query2, complaint_id)
    if notification:
        query = """
        SELECT email FROM bod_complaint_emails WHERE complaint_id = %s
        """
        with flask.g.pymysql_db.cursor() as cursor:
            cursor.execute(query, complaint_id)
            res = cursor.fetchall()
        for row in res:
            send_update_email(row['email'], complaint_id)


def get_link(complaint_id):
    """
    Gets a (fully qualified) link to the view page for this complaint id
    """
    query = 'SELECT uuid FROM bod_complaint_info WHERE complaint_id = %s'
    with flask.g.pymysql_db.cursor() as cursor:
        cursor.execute(query, complaint_id)
        res = cursor.fetchone()
        if not res:
            return None
        uuid = res['uuid']
    return flask.url_for(
        'bodfeedback.bodfeedback_view_complaint', id=uuid, _external=True)


def get_id(uuid):
    """
    Returns the complaint_id associated with a uuid
    or false if the uuid is not found
    """
    query = 'SELECT complaint_id FROM bod_complaint_info WHERE uuid = %s'
    with flask.g.pymysql_db.cursor() as cursor:
        cursor.execute(query, str(uuid))
        if not cursor.rowcount:
            return False
        res = cursor.fetchone()
        res = res['complaint_id']
    return res


def get_messages(complaint_id):
    """
    Returns timestamps, posters, messages, and message_id's on this complaint
    in ascending order of timestamp
    """
    query = """
    SELECT time, poster, message, message_id FROM bod_complaint_messages WHERE complaint_id = %s ORDER BY time
    """
    with flask.g.pymysql_db.cursor() as cursor:
        cursor.execute(query, complaint_id)
        res = cursor.fetchall()
    if not res or 'message_id' not in res[0]:
        return None
    return res


def get_summary(complaint_id):
    """
    Returns a dict with the following fields: course, status
    """
    fields = ['subject', 'status']
    query = 'SELECT ' + ', '.join(
        fields) + ' FROM bod_complaint_info WHERE complaint_id = %s'
    with flask.g.pymysql_db.cursor() as cursor:
        cursor.execute(query, complaint_id)
        res = cursor.fetchone()
    return res


def get_subject(complaint_id):
    '''
    Returns the suject or None if complaint_id is invalid
    '''
    res = get_summary(complaint_id)
    return res['subject'] if res else None


def get_status(complaint_id):
    '''
    Returns the status of a post or None if complaint_id is invalid
    '''
    res = get_summary(complaint_id)
    return res['status'] if res else None


def mark_read(complaint_id):
    '''
    Sets the status of this complaint to 'read'
    returns False if complaint_id is invalid
    '''
    query = """
    UPDATE bod_complaint_info SET status = 'read' WHERE complaint_id = %s
    """
    if get_status(complaint_id) is None:
        return False
    with flask.g.pymysql_db.cursor() as cursor:
        cursor.execute(query, complaint_id)


def mark_unread(complaint_id):
    '''
    Sets the status of this complaint to 'new_msg'
    returns False if complaint_id is invalid
    '''
    query = """
    UPDATE bod_complaint_info SET status = 'new_msg' WHERE complaint_id = %s
    """
    if get_status(complaint_id) is None:
        return False
    with flask.g.pymysql_db.cursor() as cursor:
        cursor.execute(query, complaint_id)
        cursor.execute("COMMIT;")  #not sure why this doesn't autocommit


def get_emails(complaint_id):
    """
    Returns a list of subscribed emails for this complaint (which may be empty)
    or an empty list if complaint_id is invalid
    """
    query = 'SELECT email FROM bod_complaint_emails WHERE complaint_id = %s'
    with flask.g.pymysql_db.cursor() as cursor:
        cursor.execute(query, complaint_id)
        res = cursor.fetchall()
    return [row['email'] for row in res]


def get_all_fields(complaint_id):
    '''
    Returns a dict with emails, messages, subject, status
    Returns None if complaint_id is invalid
    '''
    data = {
        'emails': get_emails(complaint_id),
        'messages': get_messages(complaint_id),
        'subject': get_subject(complaint_id),
        'status': get_status(complaint_id)
    }
    return data if data['subject'] else None


def get_new_posts():
    '''
    Returns all posts with status 'new_msg' and their associated list
    of messages. Will be an array of dicts with keys complaint_id, subject,
    status, uuid, message, poster, time
    Note that message and poster refer to the latest comment on this complaint
    '''
    query = """SELECT post.complaint_id AS complaint_id, post.subject AS subject, post.status AS status,
    post.uuid AS uuid, comment.message AS message, comment.poster AS poster, comment.time AS time FROM bod_complaint_info post
    INNER JOIN bod_complaint_messages comment
    ON comment.complaint_id = post.complaint_id
    INNER JOIN (
    SELECT complaint_id, max(time) AS time FROM bod_complaint_messages GROUP BY complaint_id
    ) maxtime
    ON maxtime.time = comment.time AND maxtime.complaint_id = comment.complaint_id
    WHERE post.status = 'new_msg'
    """
    with flask.g.pymysql_db.cursor() as cursor:
        cursor.execute(query)
        res = cursor.fetchall()
    return res
