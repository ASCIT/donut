import json
import flask


def get_survey_id(access_key):
    query = 'SELECT survey_id FROM surveys WHERE access_key = %s AND start_time <= NOW() AND NOW() <= end_time'
    with flask.g.pymysql_db.cursor() as cursor:
        cursor.execute(query, [access_key])
        survey = cursor.fetchone()
    return survey and survey['survey_id']


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
