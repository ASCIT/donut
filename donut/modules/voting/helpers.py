import json
import flask
from donut.auth_utils import get_user_id
from donut.misc_utils import generate_random_string
from donut.modules.groups.helpers import get_group_list_data

ACCESS_KEY_LENGTH = 64


def get_groups():
    return get_group_list_data(['group_id', 'group_name'])


def get_question_types():
    query = 'SELECT type_id, type_name FROM survey_question_types'
    with flask.g.pymysql_db.cursor() as cursor:
        cursor.execute(query)
        return {
            question_type['type_name']: question_type['type_id']
            for question_type in cursor.fetchall()
        }


def get_public_surveys(user_id):
    query = """
        SELECT DISTINCT title, description, end_time, access_key
        FROM surveys
            NATURAL LEFT JOIN groups
            NATURAL LEFT JOIN (
                SELECT group_id, user_id FROM group_members UNION
                SELECT group_id, user_id FROM position_holders
            ) tmp
        WHERE start_time <= NOW() AND NOW() <= end_time
        AND (group_id IS NULL OR user_id = %s)
        ORDER BY end_time
    """
    with flask.g.pymysql_db.cursor() as cursor:
        cursor.execute(query, [user_id])
        return cursor.fetchall()


def get_survey_data(access_key):
    query = """
        SELECT survey_id, title, description, start_time, end_time, creator
        FROM surveys WHERE access_key = %s
    """
    with flask.g.pymysql_db.cursor() as cursor:
        cursor.execute(query, [access_key])
        survey = cursor.fetchone()
    return survey


def get_questions_json(survey_id):
    questions_query = """
        SELECT question_id, title, description, type_id, choices
        FROM survey_questions NATURAL JOIN survey_question_types
        WHERE survey_id = %s
        ORDER BY list_order
    """
    with flask.g.pymysql_db.cursor() as cursor:
        cursor.execute(questions_query, [survey_id])
        questions = cursor.fetchall()
    for question in questions:
        question['description'] = question['description'] or ''
        if question['choices']:
            choices_query = 'SELECT choice FROM survey_question_choices WHERE question_id = %s ORDER BY choice_id'
            with flask.g.pymysql_db.cursor() as cursor:
                cursor.execute(choices_query, [question['question_id']])
                question['choices'] = [
                    choice['choice'] for choice in cursor.fetchall()
                ]
        else:
            del question['choices']
        del question['question_id']
    return json.dumps(questions)


def make_survey(**params):
    access_key = generate_random_string(ACCESS_KEY_LENGTH)
    creator = get_user_id(params['username'])
    query = """
        INSERT INTO surveys (title, description, start_time, end_time,
            access_key, group_id, auth, public, creator)
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
    """
    with flask.g.pymysql_db.cursor() as cursor:
        cursor.execute(query, [
            params['title'], params['description'], params['start'],
            params['end'], access_key, params['group_id'], params['auth'],
            params['public'], creator
        ])
    return access_key


def get_survey_params(survey_id):
    query = """
        SELECT title, description, start_time, end_time,
            group_id, auth, public
        FROM surveys
        WHERE survey_id = %s
    """
    with flask.g.pymysql_db.cursor() as cursor:
        cursor.execute(query, [survey_id])
        return cursor.fetchone()
