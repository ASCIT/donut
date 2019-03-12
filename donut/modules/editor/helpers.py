import flask
import os
import glob
import re
import pymysql.cursors
from donut import auth_utils
from donut.modules.editor.edit_permission import EditPermission
# In seconds
TIMEOUT = 60 * 3


def change_lock_status(title, new_lock_status, default=False, forced=False):
    """
    This is called when a user starts or stops editing a
    page
    """
    if default:
        return
    #if this function is called from
    # is_locked due to the page being expired...
    if forced:
        update_lock_query(title, new_lock_status)
        return
    # This is mainly because there were pages already created that weren't in
    # the database.
    create_page_in_database(title)
    uid = auth_utils.get_user_id(flask.session['username'])
    query = """SELECT last_edit_uid FROM webpage_files_locks WHERE title = %s"""
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
    query = """
    UPDATE webpage_files_locks SET locked = %s, last_edit_time = NOW(), last_edit_uid = %s WHERE title = %s
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
    create_page_in_database(title)

    query = """
    SELECT locked, TIMESTAMPDIFF(SECOND, last_edit_time, NOW()) as expired FROM webpage_files_locks WHERE title = %s
    """
    with flask.g.pymysql_db.cursor() as cursor:
        cursor.execute(query, title)
        res = cursor.fetchone()

    # Locking the file times out after 3 minutes (since we are
    # updating the last access time every 1 minute, and we generously account for
    # some lag ).
    if res['expired'] >= TIMEOUT:
        change_lock_status(title, False, forced=True)
        return False
    return res['locked']


def create_page_in_database(title):
    """
    There are some pages that exist but do not have entries in the 
    database. 
    """
    query = """
    INSERT INTO webpage_files_locks (title) VALUES (%s) ON DUPLICATE KEY UPDATE locked = locked
    """
    with flask.g.pymysql_db.cursor() as cursor:
        cursor.execute(query, title)


def rename_title(old_filename, new_filename):
    """
    Changes the file name of an html file
    Need to look for paths
    """
    old_path = os.path.join(flask.current_app.root_path,
                            flask.current_app.config["UPLOAD_WEBPAGES"],
                            old_filename + '.md')
    new_path = os.path.join(flask.current_app.root_path,
                            flask.current_app.config["UPLOAD_WEBPAGES"],
                            new_filename + '.md')

    remove_file_from_db(old_filename)

    if os.path.exists(old_path) and not os.path.exists(new_filename):
        os.rename(old_path, new_path)


def read_markdown(name):
    '''
    Reads in the mark down text from a file.
    '''

    path = os.path.join(flask.current_app.root_path,
                        flask.current_app.config['UPLOAD_WEBPAGES'])
    cur_file = read_file(os.path.join(path, name + '.md'))
    return cur_file


def read_file(path):
    '''
    Reads in a file
    '''
    if not os.path.isfile(path):
        return ''

    with open(path) as f:
        return f.read()


def get_links():
    '''
    Get links for all created webpages
    '''
    links, root = get_glob()
    results = {}
    for filename in links:
        link = flask.url_for('uploads.display', url=filename)
        results[filename] = link
    return results


def remove_link(filename):
    '''
    Get rid of matching filenames
    '''
    filename = filename.replace("_", " ")
    links, path = get_glob(clean_links=False)
    for i in links:
        name = i.replace(path + '/', '').replace('.md', '').replace("_", " ")
        if filename == name:
            os.remove(i)
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
    query = """DELETE FROM webpage_files_locks WHERE title = %s"""
    with flask.g.pymysql_db.cursor() as cursor:
        cursor.execute(query, filename)


def check_duplicate(filename):
    """
    Check to see if there are duplicate file names
    """
    links, path = get_glob()
    filename = filename.replace('_', ' ')

    for name in links:
        if filename == name:
            return True
    return False


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


def write_markdown(markdown, title):
    """
    Creates an html file that was just created,
    as well as the routes for flask
    """
    root = os.path.join(flask.current_app.root_path,
                        flask.current_app.config["UPLOAD_WEBPAGES"])

    title = title.replace(' ', '_')
    path = os.path.join(root, title + ".md")
    create_page_in_database(title)
    # Writing to the new html file
    with open(path, 'w') as f:
        f.write(markdown)
