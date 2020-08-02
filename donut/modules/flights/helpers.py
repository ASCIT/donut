import flask
import pymysql.cursors
from donut import auth_utils
from donut.modules.groups import helpers as groups


def update(link, visible):
    """
    Update the link and visible settings of the sheet.
    """
    query = """
    DELETE FROM flights;
    INSERT INTO flights (link, visible) 
    VALUES (%s, %s) 
    """
    with flask.g.pymysql_db.cursor() as cursor:
        cursor.execute(query, [link, visible])


def get_settings():
    """
    Gets whether the sheet is visible and link.
    If no sheet has been uploaded, returns not visible and empty link.
    """
    query = 'SELECT visible, link FROM flights'
    with flask.g.pymysql_db.cursor() as cursor:
        cursor.execute(query)
        if not cursor.rowcount:
            return {'visible': False, 'link': ''}
        return cursor.fetchone()


def is_admin():
    """
    Checks if user can control the settings.
    """
    if 'username' not in flask.session:
        return False
    user_id = auth_utils.get_user_id(flask.session['username'])
    ascit_id = groups.get_group_id('ASCIT')
    return auth_utils.is_admin() or groups.is_user_in_group(user_id, ascit_id)
