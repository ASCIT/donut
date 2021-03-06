from donut import email_utils
from donut.modules.feedback import email_templates
import flask
import pymysql.cursors
from donut.modules.feedback.groups import groupInt, groupName
import donut.modules.groups.helpers as groups
import donut.modules.newsgroups.helpers as newsgroups


def send_update_email(group, email, complaint_id):
    '''
    Sends an email to [email] of poster and group
    '''
    msg = email_templates.added_message.format(group,
                                               get_link(group, complaint_id))
    subject = "Received {} Feedback".format(group)
    try:
        email_utils.send_email(email, msg, subject, group=group)
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
    INSERT INTO complaint_info (org, subject, resolved, ombuds, uuid)
    VALUES (%s, %s, FALSE, %s, UNHEX(REPLACE(UUID(), '-', '')))
    """
    if 'ombuds' not in data:
        data['ombuds'] = 0
    with flask.g.pymysql_db.cursor() as cursor:
        cursor.execute(query, (groupInt[group], data['subject'],
                               data['ombuds']))
        complaint_id = cursor.lastrowid
    # Add email to db if applicable
    if data['email']:
        for email in data['email'].split(','):
            add_email(groupInt[group], complaint_id, email.strip(), False)
    # Add message to database
    add_msg(group, complaint_id, data['msg'], data['name'], notification)
    return complaint_id


def send_to_group(group, data, complaint_id=None):
    group_id = groups.get_group_id(groupName[group])
    data['group'] = group_id
    data['group_name'] = group
    data['poster'] = "{} Feedback".format(group)
    data['plain'] = data['msg']
    if complaint_id:
        data['plain'] += "\nLink to the issue: {}".format(
            get_link(group, complaint_id))
    data['msg'] = None
    newsgroups.send_email(data)


def add_email(group, complaint_id, email, notification=True):
    '''
    Adds an email to list of addresses subscribed to this complaint
    returns false if complaint_id is invalid
    '''
    if not get_subject(group, complaint_id): return False
    query = """
    INSERT INTO complaint_emails (complaint_id, email)
    VALUES (%s, %s)
    """
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
    query = 'DELETE FROM complaint_emails WHERE complaint_id = %s AND email = %s'
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
    subject = get_subject(group, complaint_id)
    if not subject:
        return False
    # Add the message
    query = """
    INSERT INTO complaint_messages (complaint_id, message, poster, time)
    VALUES (%s, %s, %s, NOW())
    """
    # Update the status to new_msg
    query2 = 'UPDATE complaint_info SET resolved = FALSE WHERE complaint_id = %s'
    if not poster:
        poster = '(anonymous)'
    with flask.g.pymysql_db.cursor() as cursor:
        cursor.execute(query, (complaint_id, message, poster))
        cursor.execute(query2, complaint_id)
    if notification:
        data = {'msg': message, 'subject': subject}
        send_to_group(group, data, complaint_id)
        query = 'SELECT email FROM complaint_emails WHERE complaint_id = %s'
        with flask.g.pymysql_db.cursor() as cursor:
            cursor.execute(query, complaint_id)
            res = cursor.fetchall()
        for row in res:
            send_update_email(group, row['email'], complaint_id)


def get_link(group, complaint_id):
    '''
    Gets a (fully qualified) link to the view page for this complaint id
    '''
    query = 'SELECT HEX(uuid) AS uuid FROM complaint_info WHERE complaint_id = %s'
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
    query = 'SELECT complaint_id FROM complaint_info WHERE org = %s AND uuid = UNHEX(%s)'
    with flask.g.pymysql_db.cursor() as cursor:
        cursor.execute(query, (groupInt[group], uuid))
        if not cursor.rowcount:
            return False
        return cursor.fetchone()['complaint_id']


def get_messages(group, complaint_id):
    '''
    Returns timestamps, posters, messages, and message_id's on this complaint
    in ascending order of timestamp
    '''
    query = """
    SELECT time, poster, message, message_id FROM complaint_messages
    WHERE complaint_id = %s ORDER BY time
    """.format(group)
    with flask.g.pymysql_db.cursor() as cursor:
        cursor.execute(query, (complaint_id))
        return cursor.fetchall()


def get_summary(group, complaint_id):
    '''
    Returns a dict with the following fields: subject, status
    '''
    query = 'SELECT subject, resolved FROM complaint_info WHERE complaint_id = %s'
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
    return res['resolved'] if res else None


def set_resolved(group, complaint_id, status):
    '''
    Sets the status of this complaint to resolved/unresolved
    '''
    query = "UPDATE complaint_info SET resolved=%s WHERE complaint_id = %s"
    with flask.g.pymysql_db.cursor() as cursor:
        cursor.execute(query, (status, complaint_id))


def get_emails(group, complaint_id):
    '''
    Returns a list of subscribed emails for this complaint (which may be empty)
    or an empty list if complaint_id is invalid
    '''
    query = 'SELECT email FROM complaint_emails WHERE complaint_id = %s'
    with flask.g.pymysql_db.cursor() as cursor:
        cursor.execute(query, complaint_id)
        res = cursor.fetchall()
    return [row['email'] for row in res]


def get_ombuds(complaint_id):
    '''
    Returns whether the person has already talked to an ombuds/TA/instructor about
    their problem.
    '''
    query = 'SELECT ombuds FROM complaint_info WHERE complaint_id = %s'
    with flask.g.pymysql_db.cursor() as cursor:
        cursor.execute(query, complaint_id)
        return cursor.fetchone()['ombuds']


def set_ombuds(complaint_id, ombuds):
    '''
    Sets the status of whether the user has spoken to an ombuds/TA/instructor.
    '''
    query = "UPDATE complaint_info SET ombuds = %s WHERE complaint_id = %s"
    with flask.g.pymysql_db.cursor() as cursor:
        cursor.execute(query, [ombuds, complaint_id])


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
        'resolved': get_status(group, complaint_id)
    }
    if group == 'arc':
        data['ombuds'] = get_ombuds(complaint_id)
    return data


def get_posts(group, view_unresolved):
    '''
    Returns posts and their associated list
    of messages.
    If view_all is false, only returns unresolved posts.
    Will be an array of dicts with keys complaint_id, subject,
    resolved, uuid, message, poster, time
    Note that message and poster refer to the latest comment on this complaint
    '''
    query = """SELECT post.complaint_id AS complaint_id, post.subject AS subject,
    post.resolved AS resolved, post.uuid AS uuid, comment.message AS message,
    comment.poster AS poster, comment.time AS time
    FROM complaint_info post
    NATURAL JOIN complaint_messages comment
    INNER JOIN (
    SELECT complaint_id, max(time) AS time
    FROM complaint_messages
    GROUP BY complaint_id
    ) maxtime
    ON maxtime.time = comment.time AND maxtime.complaint_id = comment.complaint_id
    WHERE post.org = %s
    """
    if view_unresolved:
        query += " AND post.resolved = FALSE"
    query += " ORDER BY comment.time DESC"
    with flask.g.pymysql_db.cursor() as cursor:
        cursor.execute(query, groupInt[group])
        return cursor.fetchall()
