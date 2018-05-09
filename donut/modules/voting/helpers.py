from collections import Counter
from datetime import datetime
from itertools import chain, groupby
import json
import flask
from donut.auth_utils import get_user_id
from donut.misc_utils import generate_random_string
from donut.modules.groups.helpers import get_group_list_data, is_user_in_group
from donut.validation_utils import (validate_date, validate_exists,
                                    validate_in, validate_int)
from .ranked_pairs import winners

ACCESS_KEY_LENGTH = 64
AM_OR_PM = set(['A', 'P'])
YYYY_MM_DD = '%Y-%m-%d'
NO = 'NO'


def get_groups():
    return get_group_list_data(['group_id', 'group_name'])


question_types = None


def get_question_types():
    global question_types
    if not question_types:
        query = 'SELECT type_id, type_name FROM survey_question_types'
        with flask.g.pymysql_db.cursor() as cursor:
            cursor.execute(query)
            question_types = {
                question_type['type_name']: question_type['type_id']
                for question_type in cursor.fetchall()
            }
    return question_types


def allowed_to_take(user_id):
    return lambda survey: survey['group_id'] is None or is_user_in_group(user_id, survey['group_id'])


def get_public_surveys(user_id):
    query = """
        SELECT DISTINCT title, description, end_time, access_key, group_id
        FROM surveys
        WHERE start_time <= NOW() AND NOW() <= end_time
        AND public
        ORDER BY end_time
    """
    with flask.g.pymysql_db.cursor() as cursor:
        cursor.execute(query)
        return filter(allowed_to_take(user_id), cursor.fetchall())


def get_closed_surveys(user_id):
    query = """
        SELECT title, description, end_time, access_key, results_shown
        FROM surveys
        WHERE end_time <= NOW()
        AND (creator = %s OR (public AND results_shown))
        ORDER BY end_time DESC
    """
    with flask.g.pymysql_db.cursor() as cursor:
        cursor.execute(query, [user_id])
        return cursor.fetchall()


def get_survey_data(access_key):
    query = """
        SELECT survey_id, title, description, group_id,
        start_time, end_time, creator, auth, results_shown
        FROM surveys WHERE access_key = %s
    """
    with flask.g.pymysql_db.cursor() as cursor:
        cursor.execute(query, [access_key])
        return cursor.fetchone()


def get_questions_json(survey_id, include_id):
    questions_query = """
        SELECT question_id, title, description, type_id AS type, choices
        FROM survey_questions NATURAL JOIN survey_question_types
        WHERE survey_id = %s
        ORDER BY list_order
    """
    choices_query = 'SELECT choice FROM survey_question_choices WHERE question_id = %s ORDER BY choice_id'
    with flask.g.pymysql_db.cursor() as cursor:
        cursor.execute(questions_query, [survey_id])
        questions = cursor.fetchall()
        for question in questions:
            question['description'] = question['description'] or ''
            if question['choices']:
                cursor.execute(choices_query, [question['question_id']])
                question['choices'] = [
                    choice['choice'] for choice in cursor.fetchall()
                ]
            else:
                del question['choices']
            if not include_id: del question['question_id']
    return json.dumps(questions)


def get_question_ids(survey_id):
    query = 'SELECT question_id FROM survey_questions WHERE survey_id = %s ORDER BY list_order'
    with flask.g.pymysql_db.cursor() as cursor:
        cursor.execute(query, [survey_id])
        return [question['question_id'] for question in cursor.fetchall()]


def get_question_type(question_id):
    query = 'SELECT type_id FROM survey_questions WHERE question_id = %s'
    with flask.g.pymysql_db.cursor() as cursor:
        cursor.execute(query, [question_id])
        return cursor.fetchone()['type_id']


def get_choice(question_id, value):
    query = 'SELECT choice_id FROM survey_question_choices WHERE question_id = %s AND choice = %s'
    with flask.g.pymysql_db.cursor() as cursor:
        cursor.execute(query, [question_id, value])
        return cursor.fetchone()


def process_params_request(survey_id=None, access_key=None):
    form = flask.request.form

    def creation_error(message):
        flask.flash(message)
        return flask.render_template(
            'survey_params.html',
            groups=get_groups(),
            title=form.get('title'),
            description=form.get('description'),
            start_date=form.get('start_date'),
            start_hour=form.get('start_hour'),
            start_minute=form.get('start_minute'),
            start_period=form.get('start_period'),
            end_date=form.get('end_date'),
            end_hour=form.get('end_hour'),
            end_minute=form.get('end_minute'),
            end_period=form.get('end_period'),
            auth='auth' in form,
            public='public' in form,
            group_id=form.get('group'))

    if 'username' not in flask.session:
        return creation_error('Not logged in')

    validations = [
        validate_exists(form, 'title'),
        validate_exists(form, 'description'),
        validate_exists(form, 'start_date')
        and validate_date(form['start_date']),
        validate_exists(form, 'start_hour')
        and validate_int(form['start_hour'], 1, 12),
        validate_exists(form, 'start_minute')
        and validate_int(form['start_minute'], 0, 59),
        validate_exists(form, 'start_period')
        and validate_in(form['start_period'], AM_OR_PM),
        validate_exists(form, 'end_date') and validate_date(form['end_date']),
        validate_exists(form, 'end_hour')
        and validate_int(form['end_hour'], 1, 12),
        validate_exists(form, 'end_minute')
        and validate_int(form['end_minute'], 0, 59),
        validate_exists(form, 'end_period')
        and validate_in(form['end_period'], AM_OR_PM),
        validate_exists(form, 'group')
        and (not form['group'] or validate_int(form['group']))
    ]
    if not all(validations):
        #Should only happen if a malicious request is sent,
        #so error message is not important
        return creation_error('Invalid form data')

    start_day = datetime.strptime(form['start_date'], YYYY_MM_DD)
    start_hour = int(form['start_hour']) % 12
    if form['start_period'] == 'P': start_hour += 12
    start_minute = int(form['start_minute'])
    start = datetime(start_day.year, start_day.month, start_day.day,
                     start_hour, start_minute)
    end_day = datetime.strptime(form['end_date'], YYYY_MM_DD)
    end_hour = int(form['end_hour']) % 12
    if form['end_period'] == 'P': end_hour += 12
    end_minute = int(form['end_minute'])
    end = datetime(end_day.year, end_day.month, end_day.day, end_hour,
                   end_minute)
    if start >= end:
        return creation_error('Start must be before end')

    group = form['group']
    group = int(group) if group else None

    params = {
        'title': form['title'].strip(),
        'description': form['description'].strip() or None,
        'start_time': start,
        'end_time': end,
        'auth': 'auth' in form,
        'public': 'public' in form,
        'group_id': group
    }
    if survey_id:
        update_survey_params(survey_id, params)
    else:
        access_key = generate_random_string(ACCESS_KEY_LENGTH)
        params['access_key'] = access_key
        params['creator'] = get_user_id(flask.session['username'])
        query = 'INSERT INTO surveys (' + ', '.join(
            params) + ') VALUES (' + ', '.join(['%s'] * len(params)) + ')'
        with flask.g.pymysql_db.cursor() as cursor:
            cursor.execute(query, list(params.values()))
    return flask.redirect(
        flask.url_for('voting.edit_questions', access_key=access_key))


def get_survey_params(survey_id):
    query = """
        SELECT title, description, start_time, end_time, group_id, auth, public
        FROM surveys WHERE survey_id = %s
    """
    with flask.g.pymysql_db.cursor() as cursor:
        cursor.execute(query, [survey_id])
        return cursor.fetchone()


def update_survey_params(survey_id, params):
    query = 'UPDATE surveys SET ' + ', '.join(
        key + ' = %s' for key in params) + ' WHERE survey_id = %s'
    with flask.g.pymysql_db.cursor() as cursor:
        cursor.execute(query, [*params.values(), survey_id])


def set_questions(survey_id, questions):
    delete_query = 'DELETE FROM survey_questions WHERE survey_id = %s'
    insert_question_query = """
        INSERT INTO survey_questions (survey_id, title, description, list_order, type_id)
        VALUES (%s, %s, %s, %s, %s)
    """
    insert_choice_query = """
        INSERT INTO survey_question_choices (question_id, choice)
        VALUES (%s, %s)
    """
    with flask.g.pymysql_db.cursor() as cursor:
        cursor.execute(delete_query, [survey_id])
        for order, question in enumerate(questions):
            cursor.execute(insert_question_query, [
                survey_id, question['title'], question['description'].strip()
                or None, order, question['type']
            ])
            question_id = cursor.lastrowid
            for choice in question.get('choices', []):
                cursor.execute(insert_choice_query, [question_id, choice])


def get_my_surveys(user_id):
    query = """
        SELECT title, description, access_key,
        start_time, start_time >= NOW() AS unopened,
        end_time <= NOW() as closed, end_time
        FROM surveys WHERE creator = %s
    """
    with flask.g.pymysql_db.cursor() as cursor:
        cursor.execute(query, [user_id])
        return cursor.fetchall()


def delete_survey(survey_id):
    query = 'DELETE FROM surveys WHERE survey_id = %s'
    with flask.g.pymysql_db.cursor() as cursor:
        cursor.execute(query, [survey_id])


def restrict_take_access(survey):
    if not survey:
        return 'Invalid access key'
    now = datetime.now()
    if not (survey['start_time'] <= now <= survey['end_time']):
        return 'Survey is not currently accepting responses'
    username = flask.session.get('username')
    if not username:
        return 'Must be logged in to take survey'
    if not allowed_to_take(get_user_id(username))(survey):
        return 'You do not belong to the group this survey is for'
    responses_query = """
        SELECT question_id
        FROM survey_questions NATURAL JOIN survey_responses NATURAL JOIN users
        WHERE survey_id = %s AND username = %s
    """
    with flask.g.pymysql_db.cursor() as cursor:
        cursor.execute(responses_query,
                       [survey['survey_id'], flask.session['username']])
        if cursor.fetchone(): return 'Already completed'


def set_responses(question_ids, responses):
    user_id = get_user_id(flask.session['username'])
    query = """
        INSERT INTO survey_responses(question_id, user_id, response)
        VALUES (%s, %s, %s)
    """
    with flask.g.pymysql_db.cursor() as cursor:
        for question_id, response in zip(question_ids, responses):
            cursor.execute(query, [question_id, user_id, response])


def some_responses_for_survey(survey_id):
    query = """
        SELECT user_id
        FROM survey_responses NATURAL JOIN survey_questions
        WHERE survey_id = %s
        LIMIT 1
    """
    with flask.g.pymysql_db.cursor() as cursor:
        cursor.execute(query, [survey_id])
        return cursor.fetchone() is not None


def get_results(survey_id):
    questions_query = """
        SELECT question_id, title, description, type_id AS type, list_order, choices
        FROM survey_questions NATURAL JOIN survey_question_types
        WHERE survey_id = %s
        ORDER BY list_order
    """
    choices_query = """
        SELECT choice_id, choice
        FROM survey_question_choices
        WHERE question_id = %s
        ORDER BY choice_id
    """
    responses_query = """
        SELECT response
        FROM survey_questions NATURAL JOIN survey_responses
        WHERE question_id = %s
    """
    name_query = 'SELECT full_name FROM members_full_name WHERE user_id = %s'
    question_types = get_question_types()
    count_types = set([
        question_types['Dropdown'], question_types['Short text'],
        question_types['Long text']
    ])
    with flask.g.pymysql_db.cursor() as cursor:
        cursor.execute(questions_query, [survey_id])
        questions = cursor.fetchall()
        for question in questions:
            if question['choices']:
                cursor.execute(choices_query, [question['question_id']])
                question['choices'] = {
                    choice['choice_id']: choice['choice']
                    for choice in cursor.fetchall()
                }
            else:
                del question['choices']

            def resolve_name(vote):
                if vote is None: return NO
                if type(vote) is int:
                    if vote < 0:  # user_id
                        cursor.execute(name_query, [-vote])
                        return cursor.fetchone()['full_name']
                    else:
                        return question['choices'][vote]
                raise Exception('Unrecognized elected position vote')

            cursor.execute(responses_query, question['question_id'])
            responses = [
                json.loads(res['response']) for res in cursor.fetchall()
            ]
            question['responses'] = responses
            question_type = question['type']
            if question_type in count_types:
                question['results'] = Counter(responses).most_common()
            elif question_type == question_types['Checkboxes']:
                question['results'] = Counter(chain(*responses)).most_common()
            elif question_type == question_types['Elected position']:
                non_abstaining = [[resolve_name(vote) for vote in res]
                                  for res in responses if res]
                question['results'] = winners(non_abstaining)
                question['filled_responses'] = non_abstaining
    return questions


def release_results(survey_id):
    query = 'UPDATE surveys SET results_shown = TRUE WHERE survey_id = %s'
    with flask.g.pymysql_db.cursor() as cursor:
        cursor.execute(query, [survey_id])
