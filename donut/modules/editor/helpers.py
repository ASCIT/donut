import flask
import os
import glob
import re
import pymysql.cursors
from donut import auth_utils
from donut.modules import groups
from donut.modules.editor.edit_permission import EditPermission
# In seconds
TIMEOUT = 60 * 3


def change_lock_status(title, new_lock_status, default=False, forced=False):
    """
    This is called when a user starts or stops editing a
    page
    """
    title = title.replace(" ", "_")
    if default:
        return
    # If this function is called from
    # is_locked due to the page being expired...
    if forced:
        update_lock_query(title, new_lock_status)
        return
    # This is mainly because there were pages already created that weren't in
    # the database.
    uid = auth_utils.get_user_id(flask.session['username'])
    query = """SELECT last_edit_uid FROM webpage_files WHERE title = %s"""
    with flask.g.pymysql_db.cursor() as cursor:
        cursor.execute(query, title)
        res = cursor.fetchone()
    # If the page isn't locked before OR if the last user who edited this
    # Is the same person
    if not is_locked(title) or res['last_edit_uid'] == uid:
        update_lock_query(title, new_lock_status)


def update_lock_query(title, new_lock_status):
    """
    Query for updating lock status
    """
    title = title.replace(" ", "_")
    query = """
    UPDATE webpage_files 
        SET locked = %s, last_edit_time = NOW(), last_edit_uid = %s 
        WHERE title = %s
    """
    with flask.g.pymysql_db.cursor() as cursor:
        cursor.execute(
            query, (new_lock_status,
                    auth_utils.get_user_id(flask.session['username']), title))


def is_locked(title, default=False):
    """
    Gets the edit lock status of the current request page. 
    If we are landing in the default page, automatically return True
    """
    if default:
        return False
    title = title.replace(" ", "_")
    query = """
    SELECT locked, TIMESTAMPDIFF(SECOND, last_edit_time, NOW()) as expired 
        FROM webpage_files WHERE title = %s
    """
    with flask.g.pymysql_db.cursor() as cursor:
        cursor.execute(query, title)
        res = cursor.fetchone()
    if res == None:
        return False

    # Locking the file times out after 3 minutes (since we are
    # updating the last access time every 1 minute, and we generously account for
    # some lag ).
    if res['expired'] >= TIMEOUT:
        change_lock_status(title, False, forced=True)
        return False
    return res['locked']


def create_page_in_database(title, content):
    """
    There are some pages that exist but do not have entries in the 
    database. 
    """
    title = title.replace(" ", "_")
    query = """
    INSERT INTO webpage_files (title, content) VALUES (%s, %s) ON DUPLICATE KEY UPDATE locked = locked, content = %s
    """
    with flask.g.pymysql_db.cursor() as cursor:
        cursor.execute(query, [title, content, content])


def rename_title(old_filename, new_filename):
    """
    Changes the file name of an html file
    """
    old_filename = old_filename.replace(" ", "_")
    new_filename = new_filename.replace(" ", "_")
    query = """
    UPDATE webpage_files SET title = %s WHERE title = %s
    """
    with flask.g.pymysql_db.cursor() as cursor:
        cursor.execute(query, [new_filename, old_filename])


def read_markdown(title):
    title = title.replace(" ", "_")
    query = """SELECT content FROM webpage_files 
    WHERE title = %s"""
    with flask.g.pymysql_db.cursor() as cursor:
        cursor.execute(query, [title])
        res = cursor.fetchone()
    return res['content'] if res != None else None


def read_file(path):
    '''
    Reads in a file
    '''
    if not os.path.isfile(path):
        return ''

    with open(path) as f:
        return f.read()


def get_links():
    query = """SELECT title FROM webpage_files"""
    with flask.g.pymysql_db.cursor() as cursor:
        cursor.execute(query, [])
    res = cursor.fetchall()
    results = {
        key['title']: flask.url_for('uploads.display', url=key['title'])
        for key in res
    }
    return results


### TODO: this functino literally has no purpose but I need to remember to get rid of it.
def remove_link(filename):
    remove_file_from_db(filename)


def get_glob(clean_links=True):
    """
    Grabs the list of files from a preset path. 
    """
    path = os.path.join(flask.current_app.root_path,
                        flask.current_app.config['UPLOAD_WEBPAGES'])
    filenames = glob.glob(path + '/*')
    if clean_links:
        filenames = clean_file_names(path, filenames)
    return (filenames, path)


def clean_file_names(path, links):
    """
    Stripes a few things from the glob links
    """
    return [
        link.replace(path + '/', '').replace('.md', '').replace('_', ' ')
        for link in links
    ]


def remove_file_from_db(filename):
    """
    Removes the information for a file from the db
    """
    filename = filename.replace(' ', '_')
    query = """DELETE FROM webpage_files WHERE title = %s"""
    with flask.g.pymysql_db.cursor() as cursor:
        cursor.execute(query, filename)


def check_duplicate(filename):
    """
    Check to see if there are duplicate file names
    """
    filename = filename.replace(' ', '_')
    query = """SELECT title FROM webpage_files WHERE title = %s"""
    with flask.g.pymysql_db.cursor() as cursor:
        cursor.execute(query, [filename])
        res = cursor.fetchone()
    return False if res is None else True


def check_title(title):
    """
    Makes sure the title is valid,
    Allows all numbers and characters. Allows ".", "_", "-"
    """
    return len(title) < 100 and re.match(r'^[0-9a-zA-Z./\-_: ]*$',
                                         title) != None


def check_edit_page_permission():
    """
    Checks if the user has permission to edit a page
    """
    return auth_utils.check_login() and auth_utils.check_permission(
        flask.session['username'], EditPermission.ABLE)
