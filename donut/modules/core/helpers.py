import flask

import pymysql.cursors


def get_member_data(user_id, fields=None):
    """
    Queries the database and returns member data for the specified user_id
    or list of user_id's.

    Arguments:
        user_id: The member (or list of members) to look up
        fields:  The fields to return. If None specified, then default_fields
                 are used.
    Returns:
        result: The fields and corresponding values of member with user_id. In
                the form of a dict with key:value of columnname:columnvalue.
                For lists of user_id's result will be a list of dicts.
    """
    all_returnable_fields = [
        "user_id", "uid", "last_name", "first_name", "middle_name",
        "preferred_name", "email", "phone", "gender", "gender_custom",
        "birthday", "entry_year", "graduation_year", "msc", "building",
        "room_num", "address", "city", "state", "zip", "country"
    ]
    default_fields = [
        "user_id", "first_name", "last_name", "email", "uid", "entry_year",
        "graduation_year"
    ]
    if fields == None:
        fields = default_fields
    else:
        if any(f not in all_returnable_fields for f in fields):
            return "Invalid field"

    if not isinstance(user_id, list):
        user_id = [user_id]

    # edge case: user_id is empty list
    if len(user_id) == 0:
        return {}

    query = "SELECT " + ', '.join(fields) + " FROM members WHERE "
    query += ' OR '.join(["user_id=%s" for _ in user_id])

    # Execute the query
    with flask.g.pymysql_db.cursor() as cursor:
        cursor.execute(query, user_id)
        result = cursor.fetchall()

    if len(result) == 0:
        return {}
    elif len(result) == 1:
        return result[0]
    return result


def get_member_list_data(fields=None, attrs={}):
    """
    Queries the database and returns list of member data constrained by the
    specified attributes.

    Arguments:
        fields: The fields to return. If None specified, then default_fields
                are used.
        attrs:  The attributes of the members to filter for.
    Returns:
        result: The fields and corresponding values of members with desired
                attributes. In the form of a list of dicts with key:value of
                columnname:columnvalue.
    """
    all_returnable_fields = [
        "user_id", "uid", "last_name", "first_name", "middle_name", "email",
        "phone", "gender", "gender_custom", "birthday", "entry_year",
        "graduation_year", "msc", "building", "room_num", "address", "city",
        "state", "zip", "country"
    ]
    default_fields = [
        "user_id", "first_name", "last_name", "email", "uid", "entry_year",
        "graduation_year"
    ]
    if fields == None:
        fields = default_fields
    else:
        if any(f not in all_returnable_fields for f in fields):
            return "Invalid field"

    query = "SELECT " + ', '.join(fields) + " FROM members"

    if attrs:
        query += " WHERE "
        query += ' AND '.join([key + "= %s" for key, value in attrs.items()])
    values = [value for key, value in attrs.items()]

    # Execute the query
    with flask.g.pymysql_db.cursor() as cursor:
        cursor.execute(query, values)
        return cursor.fetchall()


def get_name_and_email(user_id):
    """
    Queries the database and returns the full_name and email corresponding to the
    user_id.

    Arguments:
        user_id:            The user_id to match.
    Returns:
        {'full_name', 'email'}: The full_name and email of the user with the given id.
    """

    query = """
        SELECT full_name, email
        FROM members NATURAL LEFT JOIN members_full_name
        WHERE user_id = %s
    """
    with flask.g.pymysql_db.cursor() as cursor:
        cursor.execute(query, user_id)
        return cursor.fetchone()


def get_group_list_of_member(user_id):
    """
    Queries the database and returns list of groups and admin status
    for a given id
    Arguments:
        user_id: The user_id for query.
    Returns:
        result: All the groups that an user_id is a part of
    """
    query = """
        SELECT DISTINCT group_id, group_name, control
        FROM groups NATURAL JOIN positions NATURAL JOIN current_position_holders
        WHERE user_id = %s
    """

    with flask.g.pymysql_db.cursor() as cursor:
        cursor.execute(query, [user_id])
        return list(cursor.fetchall())


def set_image(user_id, extension, contents):
    delete_query = 'DELETE FROM images WHERE user_id = %s'
    with flask.g.pymysql_db.cursor() as cursor:
        cursor.execute(delete_query, [user_id])
    add_query = 'INSERT INTO images (user_id, extension, image) VALUES (%s, %s, %s)'
    with flask.g.pymysql_db.cursor() as cursor:
        cursor.execute(add_query, [user_id, extension, contents])


def get_preferred_name(user_id):
    return get_member_data(user_id, ['preferred_name'])['preferred_name'] or ''


def get_gender(user_id):
    return get_member_data(user_id, ['gender_custom'])['gender_custom'] or ''


def set_member_field(user_id, field, value):
    query = 'UPDATE members SET `' + field + '` = %s WHERE user_id = %s'
    with flask.g.pymysql_db.cursor() as cursor:
        cursor.execute(query, [value, user_id])


def get_news():
    query = 'SELECT * FROM news ORDER BY news_id DESC'
    with flask.g.pymysql_db.cursor() as cursor:
        cursor.execute(query)
        return cursor.fetchall()


def add_news(news):
    query = 'INSERT INTO news(news_text) VALUES (%s)'
    with flask.g.pymysql_db.cursor() as cursor:
        cursor.execute(query, news)


def delete_news(news_id):
    query = 'DELETE FROM news WHERE news_id = %s'
    with flask.g.pymysql_db.cursor() as cursor:
        cursor.execute(query, news_id)
