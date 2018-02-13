import flask
import sqlalchemy

import pymysql.cursors

from donut.constants import MALE, FEMALE


def get_user_list(field=None):
    print("HI")


def get_user(user_id):
    query = """
        SELECT uid, first_name, middle_name, last_name, preferred_name,
            email, phone, gender, birthday, entry_year, graduation_year,
            msc, building, room_num, address, city, state, zip, country
        FROM members
        WHERE user_id = %s
    """
    with flask.g.pymysql_db.cursor() as cursor:
        cursor.execute(query, [user_id])
        user = cursor.fetchone()
    if user is not None:
        if user['gender'] == MALE:
            user['gender_string'] = 'Male'
        elif user['gender'] == FEMALE:
            user['gender_string'] = 'Female'
        phone = user['phone']
        if phone:
            if len(phone) == 10 and all(map(lambda d: '0' <= d <= '9', phone)):
                user[
                    'phone_string'] = '(' + phone[:
                                                  3] + ') ' + phone[3:
                                                                    6] + '-' + phone[6:]
            else:
                user[
                    'phone_string'] = phone  #what sort of phone number is that
        state = user['state']
        if state:
            city = user['city']
            country = user['country']
            user['hometown_string'] = (city + ', ' if city else
                                       '') + state + (', ' + country
                                                      if country else '')
    return user


def get_users_by_name_query(search):
    """
    Finds users whose names match the given query.
    Query is split on spaces, so 'abc def ghi' would
    find all users whose names contain 'abc', 'def', and 'ghi',
    case insensitive. Max 10 users returned, in alphabetical order.
    """
    search = search.lower().split(' ')
    query = 'SELECT * FROM members_full_name'
    for i, fragment in enumerate(search):
        if i:
            query += ' AND'
        else:
            query += ' WHERE'
        query += ' INSTR(LOWER(full_name), %s) > 0'
    query += ' ORDER BY LOWER(full_name) LIMIT 10'
    with flask.g.pymysql_db.cursor() as cursor:
        cursor.execute(query, search)
        return cursor.fetchall()
