import flask
import pymysql.cursors
from donut.auth_utils import get_permissions
from donut.constants import Gender
from donut.resources import Permissions


def get_hidden_fields(viewer_name, viewee_id):
    """
    Returns a set of strings corresponding to fields
    on view_user page for viewee that viewer should not see
    """
    if viewer_name is not None:
        is_me = get_user_id(viewer_name) == viewee_id
        if is_me or Permissions.ADMIN in get_permissions(viewer_name):
            return set()
    return set(['uid', 'birthday', 'phone_string'])


def get_user(user_id):
    query = """
        SELECT
            uid, first_name, middle_name, last_name, preferred_name,
            gender, gender_custom, birthday, entry_year, graduation_year,
            msc, building_name, room, address, city, state, zip, country,
            email, phone, username, extension IS NOT NULL as image
        FROM members
            NATURAL LEFT JOIN buildings
            NATURAL LEFT JOIN images
            NATURAL LEFT JOIN users
        WHERE user_id = %s
    """
    with flask.g.pymysql_db.cursor() as cursor:
        cursor.execute(query, [user_id])
        user = cursor.fetchone()
    if user is not None:
        if user['gender_custom']:
            user['gender_string'] = user['gender_custom']
        elif user['gender'] == Gender.MALE.value:
            user['gender_string'] = 'Male'
        elif user['gender'] == Gender.FEMALE.value:
            user['gender_string'] = 'Female'
        phone = user['phone']
        if phone:
            if len(phone) == 10 and all(['0' <= d <= '9' for d in phone]):
                user['phone_string'] = '(' + phone[:3] + ') '
                user['phone_string'] += phone[3:6] + '-' + phone[6:]
            else:  #what sort of phone number is that
                user['phone_string'] = phone
        place_names = [(user[field] or '').strip()
                       for field in ['city', 'state', 'country']]
        user['hometown_string'] = ', '.join(filter(None, place_names))

        option_query = """
            SELECT option_name, option_type
            FROM member_options NATURAL JOIN options
            WHERE user_id = %s ORDER BY option_type, option_name
        """
        with flask.g.pymysql_db.cursor() as cursor:
            cursor.execute(option_query, [user_id])
            user['options'] = cursor.fetchall()
        groups_query = """
            SELECT group_name, pos_name
            FROM position_holders NATURAL JOIN positions NATURAL JOIN groups
            WHERE group_id NOT IN (SELECT group_id FROM group_houses)
            AND (start_date IS NULL OR start_date < NOW())
            AND (end_date IS NULL OR end_date > NOW())
            AND user_id = %s
        """
        with flask.g.pymysql_db.cursor() as cursor:
            cursor.execute(groups_query, [user_id])
            user['positions'] = cursor.fetchall()
        houses_query = """
            SELECT group_name, pos_name
            FROM group_house_membership NATURAL JOIN groups NATURAL JOIN positions
            WHERE user_id = %s
        """
        with flask.g.pymysql_db.cursor() as cursor:
            cursor.execute(houses_query, [user_id])
            user['houses'] = cursor.fetchall()
    return user


SEARCH_NAME = "CONCAT(IFNULL(preferred_name, ''), ' ', first_name, ' ', last_name)"


def make_name_query(search):
    """
    Query is split on spaces, so 'abc def' would
    find all users whose names contain 'abc' and 'def',
    case insensitive.
    Returns arguments to substitute and SQL query.
    """
    terms = search.split(' ')
    #INSTR is case-insensitive
    return terms, ' AND '.join(
        ['INSTR(' + SEARCH_NAME + ', %s) > 0'] * len(terms))


def get_users_by_name_query(search):
    """
    Finds users whose names match the given query.
    Max 10 users returned, in alphabetical order.
    """
    query = 'SELECT user_id, full_name FROM members NATURAL JOIN members_full_name WHERE '
    search, name_query = make_name_query(search)
    query += name_query
    query += ' ORDER BY LOWER(full_name) LIMIT 10'
    with flask.g.pymysql_db.cursor() as cursor:
        cursor.execute(query, search)
        return cursor.fetchall()


def get_user_id(username):
    query = 'SELECT user_id FROM users WHERE username = %s'
    with flask.g.pymysql_db.cursor() as cursor:
        cursor.execute(query, [username])
        user = cursor.fetchone()
    if user is None:
        return 0  #will show 'No such user' page
    return user['user_id']


def set_image(user_id, extension, contents):
    delete_query = 'DELETE FROM images WHERE user_id = %s'
    with flask.g.pymysql_db.cursor() as cursor:
        cursor.execute(delete_query, [user_id])
    add_query = 'INSERT INTO images (user_id, extension, image) VALUES (%s, %s, %s);'
    with flask.g.pymysql_db.cursor() as cursor:
        cursor.execute(add_query, [user_id, extension, contents])


def get_image(user_id):
    query = 'SELECT extension, image FROM images WHERE user_id = %s'
    with flask.g.pymysql_db.cursor() as cursor:
        cursor.execute(query, [user_id])
        image = cursor.fetchone()
    if image is None:
        raise Exception('No image found for user')
    return image['extension'], image['image']


def execute_search(**kwargs):
    query = """
        SELECT DISTINCT
            user_id, full_name, graduation_year,
            extension IS NOT NULL as image
        FROM members
            NATURAL JOIN members_full_name
            NATURAL LEFT JOIN group_house_membership AS house
            NATURAL LEFT JOIN member_options
            NATURAL LEFT JOIN buildings
            NATURAL LEFT JOIN users
            NATURAL LEFT JOIN images
    """
    query += ' WHERE INSTR(email, %s) > 0'
    substitution_arguments = [kwargs['email'].lower()]
    if kwargs['username']:
        query += ' AND INSTR(username, %s) > 0'
        substitution_arguments.append(kwargs['username'])
    if kwargs['name']:
        name_search, name_query = make_name_query(kwargs['name'])
        query += ' AND ' + name_query
        substitution_arguments += name_search
    if kwargs['house_id']:
        query += ' AND house.group_id = %s'
        substitution_arguments.append(kwargs['house_id'])
    if kwargs['option_id']:
        query += ' AND option_id = %s'
        substitution_arguments.append(kwargs['option_id'])
    if kwargs['building_id']:
        query += ' AND building_id = %s'
        substitution_arguments.append(kwargs['building_id'])
    if kwargs['grad_year']:
        query += ' AND graduation_year = %s'
        substitution_arguments.append(kwargs['grad_year'])
    if kwargs['state']:
        query += ' AND state = %s'
        substitution_arguments.append(kwargs['state'])
    query += ' ORDER BY LOWER(last_name), LOWER(full_name)'
    with flask.g.pymysql_db.cursor() as cursor:
        cursor.execute(query, substitution_arguments)
        return cursor.fetchall()


def members_unique_values(field):
    query = 'SELECT DISTINCT ' + field + ' FROM members WHERE ' + field + ' IS NOT NULL AND ' + field + '!= "" ORDER BY ' + field
    with flask.g.pymysql_db.cursor() as cursor:
        cursor.execute(query)
        return [member[field] for member in cursor.fetchall()]


def get_houses():
    query = 'SELECT * FROM group_houses ORDER BY group_name'
    with flask.g.pymysql_db.cursor() as cursor:
        cursor.execute(query)
        return cursor.fetchall()


def get_options():
    query = 'SELECT * FROM options ORDER BY option_name'
    with flask.g.pymysql_db.cursor() as cursor:
        cursor.execute(query)
        return cursor.fetchall()


def get_residences():
    query = 'SELECT DISTINCT building_id, building_name FROM members NATURAL JOIN buildings ORDER BY building_name'
    with flask.g.pymysql_db.cursor() as cursor:
        cursor.execute(query)
        return cursor.fetchall()


def get_grad_years():
    return members_unique_values('graduation_year')


def get_states():
    return members_unique_values('state')


def get_preferred_name(user_id):
    query = 'SELECT preferred_name FROM members WHERE user_id = %s'
    with flask.g.pymysql_db.cursor() as cursor:
        cursor.execute(query, [user_id])
        return cursor.fetchone()['preferred_name'] or ''


def set_preferred_name(user_id, name):
    query = 'UPDATE members SET preferred_name = %s WHERE user_id = %s'
    with flask.g.pymysql_db.cursor() as cursor:
        cursor.execute(query, [name, user_id])


def get_gender(user_id):
    query = 'SELECT gender_custom FROM members WHERE user_id = %s'
    with flask.g.pymysql_db.cursor() as cursor:
        cursor.execute(query, [user_id])
        return cursor.fetchone()['gender_custom'] or ''


def set_gender(user_id, gender):
    query = 'UPDATE members SET gender_custom = %s WHERE user_id = %s'
    with flask.g.pymysql_db.cursor() as cursor:
        cursor.execute(query, [gender, user_id])
