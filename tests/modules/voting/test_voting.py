"""
Tests donut/modules/voting
"""
from datetime import date, datetime, timedelta
import json
import re
import flask
import pytest
from donut.testing.fixtures import client
from donut import app
from donut.modules.groups.helpers import get_group_list_data
from donut.modules.voting import helpers, routes, ranked_pairs


# Ranked pairs
def test_ranked_pairs():
    # Example taken from en.wikipedia.org/wiki/Ranked_pairs
    M = 'Memphis'
    N = 'Nashville'
    C = 'Chattanooga'
    K = 'Knoxville'
    responses = (((M, ), (N, ), (C, ), (K, )), ) * 42
    responses += (((N, ), (C, ), (K, ), (M, )), ) * 26
    responses += (((C, ), (K, ), (N, ), (M, )), ) * 15
    responses += (((K, ), (C, ), (N, ), (M, )), ) * 17
    results = ranked_pairs.results(responses)
    assert results.winners == [N, C, K, M]
    assert results.tallies == {
        (C, K): 42 + 26 + 15,
        (C, M): 26 + 15 + 17,
        (C, N): 15 + 17,
        (K, C): 17,
        (K, M): 26 + 15 + 17,
        (K, N): 15 + 17,
        (M, C): 42,
        (M, K): 42,
        (M, N): 42,
        (N, C): 42 + 26,
        (N, K): 42 + 26,
        (N, M): 26 + 15 + 17,
    }

    # Test incomplete lists
    results = ranked_pairs.results([[['A']], [['B']], [['A']]])
    assert results.winners == ['A', 'B']

    # Test ties
    responses = [[['A'], ['B', 'C'], ['D']], [['A', 'C'], ['B', 'D']]]
    assert ranked_pairs.results(responses).winners == ['A', 'C', 'B', 'D']


# Helpers
def test_question_types(client):
    assert helpers.get_question_types() == {
        'Dropdown': 1,
        'Checkboxes': 2,
        'Elected position': 3,
        'Short text': 4,
        'Long text': 5
    }


def test_public_surveys(client):
    ruddock_id = get_group_list_data(
        ['group_id'], {'group_name': 'Ruddock House'})[0]['group_id']
    survey_params = [
        {
            'title': 'Unrestricted',
            'group': '',
            'end_hour': '12'
        },
        {
            'title': 'Ruddock only',
            'group': str(ruddock_id),
            'end_hour': '1'  # ends later
        }
    ]
    yesterday = date.today() + timedelta(days=-1)
    tomorrow = date.today() + timedelta(days=1)
    access_keys = {}
    with client.session_transaction() as sess:
        sess['username'] = 'csander'
    for params in survey_params:
        rv = client.post(
            flask.url_for('voting.make_survey'),
            data=dict(
                description='',
                start_date=yesterday.strftime(helpers.YYYY_MM_DD),
                start_hour='12',
                start_minute='00',
                start_period='P',
                end_date=tomorrow.strftime(helpers.YYYY_MM_DD),
                end_minute='00',
                end_period='P',
                public='on',
                **params),
            follow_redirects=False)
        assert rv.status_code == 302
        access_keys[params['title']] = [
            url_piece for url_piece in rv.location.split('/')
            if len(url_piece) == 64
        ][0]
    unrestricted = {
        'title': 'Unrestricted',
        'description': None,
        'end_time': datetime(tomorrow.year, tomorrow.month, tomorrow.day, 12),
        'access_key': access_keys['Unrestricted'],
        'group_id': None
    }
    assert list(helpers.get_visible_surveys(helpers.get_user_id(
        'dqu'))) == [  # not a Rudd
            unrestricted
        ]
    assert list(
        helpers.get_visible_surveys(helpers.get_user_id('csander'))) == [
            unrestricted, {
                'title':
                'Ruddock only',
                'description':
                None,
                'end_time':
                datetime(tomorrow.year, tomorrow.month, tomorrow.day, 13),
                'access_key':
                access_keys['Ruddock only'],
                'group_id':
                2
            }
        ]


def test_closed_surveys(client):
    yesterday = date.today() + timedelta(days=-1)
    tomorrow = date.today() + timedelta(days=1)
    survey_params = [{
        'title': 'Before',
        'start_date': yesterday.strftime(helpers.YYYY_MM_DD),
        'start_hour': '2',
        'end_date': yesterday.strftime(helpers.YYYY_MM_DD),
        'end_hour': '3'
    }, {
        'title': 'During',
        'start_date': yesterday.strftime(helpers.YYYY_MM_DD),
        'start_hour': '4',
        'end_date': tomorrow.strftime(helpers.YYYY_MM_DD),
        'end_hour': '5'
    }, {
        'title': 'After',
        'start_date': tomorrow.strftime(helpers.YYYY_MM_DD),
        'start_hour': '2',
        'end_date': tomorrow.strftime(helpers.YYYY_MM_DD),
        'end_hour': '3'
    }]
    access_keys = {}
    with client.session_transaction() as sess:
        sess['username'] = 'csander'
    for params in survey_params:
        rv = client.post(
            flask.url_for('voting.make_survey'),
            data=dict(
                description='',
                start_minute='00',
                start_period='P',
                end_minute='00',
                end_period='P',
                public='on',
                group='',
                **params),
            follow_redirects=False)
        assert rv.status_code == 302
        access_keys[params['title']] = [
            url_piece for url_piece in rv.location.split('/')
            if len(url_piece) == 64
        ][0]
    assert helpers.get_closed_surveys(helpers.get_user_id('reng')) == (
    )  # not the creator of 'Before'
    before = [{
        'title':
        'Before',
        'description':
        None,
        'end_time':
        datetime(yesterday.year, yesterday.month, yesterday.day, 15),
        'access_key':
        access_keys['Before'],
        'results_shown':
        0
    }]
    assert helpers.get_closed_surveys(helpers.get_user_id('csander')) == before
    rv = client.get(
        flask.url_for(
            'voting.release_results', access_key=access_keys['Before']))
    assert rv.status_code == 302
    assert rv.location == flask.url_for(
        'voting.show_results', access_key=access_keys['Before'])
    before[0]['results_shown'] = 1
    assert helpers.get_closed_surveys(helpers.get_user_id('reng')) == before
    assert helpers.get_closed_surveys(helpers.get_user_id('csander')) == before
    helpers.delete_survey(3)
    helpers.delete_survey(4)
    helpers.delete_survey(5)


def test_survey_data(client):
    access_key = list(helpers.get_visible_surveys(1))[0]['access_key']
    yesterday = date.today() + timedelta(days=-1)
    tomorrow = date.today() + timedelta(days=1)
    assert helpers.get_survey_data(access_key) == {
        'survey_id':
        1,
        'title':
        'Unrestricted',
        'description':
        None,
        'group_id':
        None,
        'start_time':
        datetime(yesterday.year, yesterday.month, yesterday.day, 12),
        'end_time':
        datetime(tomorrow.year, tomorrow.month, tomorrow.day, 12),
        'creator':
        3,
        'results_shown':
        0
    }


def test_question_json(client):
    question_types = helpers.get_question_types()
    helpers.set_questions(1, [{
        'title': 'A',
        'description': '',
        'type': question_types['Dropdown'],
        'choices': ['1', '2', '3']
    }, {
        'title': 'B',
        'description': 'bbb',
        'type': question_types['Short text']
    }, {
        'title': 'C',
        'description': 'ccc',
        'type': question_types['Checkboxes'],
        'choices': ['a', 'b', 'c']
    }, {
        'title': 'D',
        'description': '',
        'type': question_types['Long text']
    }, {
        'title': 'E',
        'description': '',
        'type': question_types['Elected position'],
        'choices': ['do', 're', 'me']
    }])
    assert helpers.get_questions_json(
        1, False
    ) == '[{"title":"A","description":"","type":1,"choices":["1","2","3"]},{"title":"B","description":"bbb","type":4},{"title":"C","description":"ccc","type":2,"choices":["a","b","c"]},{"title":"D","description":"","type":5},{"title":"E","description":"","type":3,"choices":["do","re","me"]}]'
    assert helpers.get_questions_json(
        1, True
    ) == '[{"question_id":1,"title":"A","description":"","type":1,"choices":[{"id":1,"choice":"1"},{"id":2,"choice":"2"},{"id":3,"choice":"3"}]},{"question_id":2,"title":"B","description":"bbb","type":4},{"question_id":3,"title":"C","description":"ccc","type":2,"choices":[{"id":4,"choice":"a"},{"id":5,"choice":"b"},{"id":6,"choice":"c"}]},{"question_id":4,"title":"D","description":"","type":5},{"question_id":5,"title":"E","description":"","type":3,"choices":[{"id":7,"choice":"do"},{"id":8,"choice":"re"},{"id":9,"choice":"me"}]}]'


def test_question_ids(client):
    assert helpers.get_question_ids(1) == [1, 2, 3, 4, 5]
    assert helpers.get_question_ids(2) == []


def test_question_type(client):
    assert list(map(helpers.get_question_type, range(1, 6))) == [1, 4, 2, 5, 3]


def test_get_choice(client):
    assert [
        helpers.invalid_choice_id(5, choice)
        for choice in ['abc', 7, 8, 9, 10]
    ] == [True, False, False, False, True]


def test_process_params_error(client):
    default_params = dict(
        title='New survey',
        description='',
        start_date='2018-05-08',
        start_hour='12',
        start_minute='00',
        start_period='P',
        end_date='2018-05-10',
        end_hour='12',
        end_minute='00',
        end_period='P',
        public='on',
        group='')

    def assert_message(message, params):
        rv = client.post(
            flask.url_for('voting.make_survey'),
            data=params,
            follow_redirects=False)
        assert rv.status_code == 200
        assert message in rv.data

    rv = client.post(
        flask.url_for('voting.make_survey'), follow_redirects=False)
    assert rv.status_code == 403
    with client.session_transaction() as sess:
        sess['username'] = 'csander'
    for delete_param in default_params:
        if delete_param == 'public': continue  # this param is optional
        params = default_params.copy()
        del params[delete_param]
        assert_message(b'Invalid form data', params)
    for date_field in ['start_date', 'end_date']:
        assert_message(b'Invalid form data', {
            **default_params, date_field: '123'
        })
    for hour_field in ['start_hour', 'end_hour']:
        assert_message(b'Invalid form data', {
            **default_params, hour_field: 'abc'
        })
        assert_message(b'Invalid form data', {
            **default_params, hour_field: '0'
        })
        assert_message(b'Invalid form data', {
            **default_params, hour_field: '13'
        })
    for minute_field in ['start_minute', 'end_minute']:
        assert_message(b'Invalid form data', {
            **default_params, minute_field: 'abc'
        })
        assert_message(b'Invalid form data', {
            **default_params, minute_field: '-1'
        })
        assert_message(b'Invalid form data', {
            **default_params, minute_field: '60'
        })
    for period_field in ['start_period', 'end_period']:
        assert_message(b'Invalid form data', {
            **default_params, period_field: 'a'
        })
        assert_message(b'Invalid form data', {
            **default_params, period_field: ''
        })
    assert_message(b'Invalid form data', {**default_params, 'group': 'a'})
    assert_message(b'Start must be before end', {
        **default_params, 'start_date': '2018-05-09',
        'end_date': '2018-05-08'
    })
    rv = client.post(
        flask.url_for('voting.make_survey'),
        data=default_params,
        follow_redirects=False)
    assert rv.status_code == 302  # successful
    helpers.delete_survey(6)


def test_survey_params(client):
    yesterday = date.today() + timedelta(days=-1)
    tomorrow = date.today() + timedelta(days=1)
    assert helpers.get_survey_params(1) == {
        'title':
        'Unrestricted',
        'description':
        None,
        'start_time':
        datetime(yesterday.year, yesterday.month, yesterday.day, 12),
        'end_time':
        datetime(tomorrow.year, tomorrow.month, tomorrow.day, 12),
        'group_id':
        None,
        'public':
        1
    }
    helpers.update_survey_params(1, {'title': 'ABC', 'group_id': 2})
    assert helpers.get_survey_params(1) == {
        'title':
        'ABC',
        'description':
        None,
        'start_time':
        datetime(yesterday.year, yesterday.month, yesterday.day, 12),
        'end_time':
        datetime(tomorrow.year, tomorrow.month, tomorrow.day, 12),
        'group_id':
        2,
        'public':
        1
    }


def test_my_surveys(client):
    yesterday = date.today() + timedelta(days=-1)
    tomorrow = date.today() + timedelta(days=1)
    assert helpers.get_my_surveys(helpers.get_user_id('dqu')) == ()
    csander = helpers.get_user_id('csander')
    assert helpers.get_my_surveys(csander) == [{
        'title':
        'ABC',
        'description':
        None,
        'access_key':
        list(helpers.get_visible_surveys(csander))[0]['access_key'],
        'start_time':
        datetime(yesterday.year, yesterday.month, yesterday.day, 12),
        'unopened':
        0,
        'closed':
        0,
        'end_time':
        datetime(tomorrow.year, tomorrow.month, tomorrow.day, 12)
    }, {
        'title':
        'Ruddock only',
        'description':
        None,
        'access_key':
        list(helpers.get_visible_surveys(csander))[1]['access_key'],
        'start_time':
        datetime(yesterday.year, yesterday.month, yesterday.day, 12),
        'unopened':
        0,
        'closed':
        0,
        'end_time':
        datetime(tomorrow.year, tomorrow.month, tomorrow.day, 13)
    }]


def test_respond(client):
    assert not helpers.some_responses_for_survey(1)
    with app.test_request_context():
        flask.session['username'] = 'csander'
        helpers.set_responses([1, 2, 3, 4, 5], [
            '2', '"asdf"', '[4, 6]', '"Lorem ipsum dolor sit amet"',
            '[[7], [-1], [9], [-2], [null]]'
        ])
    assert helpers.some_responses_for_survey(1)
    results = helpers.get_results(1)
    election_result = results.pop()
    assert results == [{
        'question_id': 1,
        'title': 'A',
        'description': None,
        'type': 1,
        'list_order': 0,
        'choices': {
            1: '1',
            2: '2',
            3: '3'
        },
        'responses': [2],
        'results': [(2, 1)]
    }, {
        'question_id': 2,
        'title': 'B',
        'description': 'bbb',
        'type': 4,
        'list_order': 1,
        'choices': 0,
        'responses': ['asdf'],
        'results': [('asdf', 1)]
    }, {
        'question_id': 3,
        'title': 'C',
        'description': 'ccc',
        'type': 2,
        'list_order': 2,
        'choices': {
            4: 'a',
            5: 'b',
            6: 'c'
        },
        'responses': [[4, 6]],
        'results': [(4, 1), (6, 1)]
    }, {
        'question_id': 4,
        'title': 'D',
        'description': None,
        'type': 5,
        'list_order': 3,
        'choices': 0,
        'responses': ['Lorem ipsum dolor sit amet'],
        'results': [('Lorem ipsum dolor sit amet', 1)]
    }]
    results = election_result.pop('results')
    assert election_result == {
        'question_id': 5,
        'title': 'E',
        'description': None,
        'type': 3,
        'list_order': 4,
        'choices': {
            7: 'do',
            8: 're',
            9: 'me'
        },
        'responses': [[['do'], ['David Qu'], ['me'], ['Robert Eng'], ['NO']]]
    }
    assert results.winners == ['do', 'David Qu', 'me', 'Robert Eng', 'NO']
    with app.test_request_context():
        flask.session['username'] = 'dqu'
        # Invalid elected position response
        helpers.set_responses([5], ['[["abc"]]'])
    with pytest.raises(Exception) as e:
        helpers.get_results(1)
    assert e.value.args == ('Unrecognized elected position vote', )


def test_restrict_access(client):
    assert helpers.restrict_take_access(None) == 'Invalid access key'
    yesterday = datetime.now() + timedelta(days=-1)
    tomorrow = datetime.now() + timedelta(days=1)
    assert helpers.restrict_take_access({
        'start_time': yesterday,
        'end_time': yesterday
    }) == 'Survey is not currently accepting responses'
    assert helpers.restrict_take_access({
        'start_time': tomorrow,
        'end_time': tomorrow
    }) == 'Survey is not currently accepting responses'
    with app.test_request_context():
        assert helpers.restrict_take_access({
            'start_time': yesterday,
            'end_time': tomorrow
        }) == 'Must be logged in to take survey'
    with app.test_request_context():
        flask.session['username'] = 'dqu'
        assert helpers.restrict_take_access({
            'start_time': yesterday,
            'end_time': tomorrow,
            'group_id': 2
        }) == 'You do not belong to the group this survey is for'
    with app.test_request_context():
        flask.session['username'] = 'csander'
        assert helpers.restrict_take_access({
            'survey_id': 1,
            'start_time': yesterday,
            'end_time': tomorrow,
            'group_id': 2
        }) == 'Already completed'
    with app.test_request_context():
        flask.session['username'] = 'reng'
        assert helpers.restrict_take_access({
            'survey_id': 1,
            'start_time': yesterday,
            'end_time': tomorrow,
            'group_id': 2
        }) is None


# Routes


def test_home(client):
    rv = client.get(flask.url_for('voting.list_surveys'))
    assert rv.status_code == 200
    assert b'Ruddock only' not in rv.data
    with client.session_transaction() as sess:
        sess['username'] = 'csander'
    rv = client.get(flask.url_for('voting.list_surveys'))
    assert rv.status_code == 200
    assert b'Ruddock only' in rv.data


def test_take(client):
    access_key = list(
        helpers.get_visible_surveys(helpers.get_user_id('csander')))[1][
            'access_key']
    rv = client.get(flask.url_for('voting.take_survey', access_key=access_key))
    assert rv.status_code == 200
    assert b'Must be logged in to take survey' in rv.data
    with client.session_transaction() as sess:
        sess['username'] = 'csander'
    helpers.set_questions(2, [{
        'title': 'Question 1',
        'description': '',
        'type': helpers.get_question_types()['Long text']
    }])
    rv = client.get(flask.url_for('voting.take_survey', access_key=access_key))
    assert rv.status_code == 200
    assert b'Edit' in rv.data
    assert b'Question 1' in rv.data
    with client.session_transaction() as sess:
        sess['username'] = 'reng'
    rv = client.get(flask.url_for('voting.take_survey', access_key=access_key))
    assert rv.status_code == 200
    assert b'Edit' not in rv.data
    assert b'Question 1' in rv.data


def test_make_form(client):
    with client.session_transaction() as sess:
        sess['username'] = 'ruddock_pres'
    rv = client.get(flask.url_for('voting.make_survey_form'))
    assert rv.status_code == 403
    with client.session_transaction() as sess:
        sess['username'] = 'csander'
    rv = client.get(flask.url_for('voting.make_survey_form'))
    assert rv.status_code == 200
    assert b'Making new survey' in rv.data


def test_manage(client):
    rv = client.get(flask.url_for('voting.my_surveys'))
    assert rv.status_code == 200
    assert b'Please log in to manage your surveys' in rv.data
    with client.session_transaction() as sess:
        sess['username'] = 'ruddock_pres'
    rv = client.get(flask.url_for('voting.my_surveys'))
    assert rv.status_code == 403
    with client.session_transaction() as sess:
        sess['username'] = 'csander'
    rv = client.get(flask.url_for('voting.my_surveys'))
    assert rv.status_code == 200
    assert b'ABC' in rv.data and b'Ruddock only' in rv.data


def test_edit_questions(client):
    # Test all restrictions
    rv = client.get(
        flask.url_for(
            'voting.edit_questions', access_key='invalid-access-key'))
    assert rv.status_code == 403
    with client.session_transaction() as sess:
        sess['username'] = 'csander'
    rv = client.get(
        flask.url_for(
            'voting.edit_questions', access_key='invalid-access-key'))
    assert rv.status_code == 200
    assert b'Invalid access key' in rv.data
    assert b'Editing survey questions' not in rv.data
    with client.session_transaction() as sess:
        sess['username'] = 'reng'
    access_key = list(
        helpers.get_visible_surveys(helpers.get_user_id('csander')))[0][
            'access_key']
    rv = client.get(
        flask.url_for('voting.edit_questions', access_key=access_key))
    assert rv.status_code == 200
    assert b'You are not the creator of this survey' in rv.data
    assert b'Editing survey questions' not in rv.data
    with client.session_transaction() as sess:
        sess['username'] = 'csander'
    client.post(
        flask.url_for('voting.make_survey'),
        data=dict(
            title='Already closed',
            description='',
            start_date='2018-05-01',
            start_hour='12',
            start_minute='00',
            start_period='P',
            end_date='2018-05-03',
            end_hour='12',
            end_minute='00',
            end_period='P',
            group=''),
        follow_redirects=False)
    closed_access_key = helpers.get_closed_surveys(
        helpers.get_user_id('csander'))[0]['access_key']
    rv = client.get(
        flask.url_for('voting.edit_questions', access_key=closed_access_key))
    assert rv.status_code == 200
    assert b'Cannot modify a survey after it has closed' in rv.data
    assert b'Editing survey questions' not in rv.data
    # Test success cases
    rv = client.get(
        flask.url_for('voting.edit_questions', access_key=access_key))
    assert rv.status_code == 200
    assert b'Editing survey questions' in rv.data
    assert b'someResponses = true' in rv.data
    access_key2 = list(
        helpers.get_visible_surveys(helpers.get_user_id('csander')))[1][
            'access_key']
    rv = client.get(
        flask.url_for('voting.edit_questions', access_key=access_key2))
    assert rv.status_code == 200
    assert b'Editing survey questions' in rv.data
    assert b'someResponses = false' in rv.data
    # Test saving questions
    rv = client.post(
        flask.url_for('voting.save_questions', access_key=closed_access_key),
        data='[]')
    assert rv.status_code == 200
    assert b'Cannot modify a survey after it has closed' in rv.data
    rv = client.post(
        flask.url_for('voting.save_questions', access_key=access_key2),
        data=
        '[{"title":"Added question","description":"","type":1,"choices":["choice A","choice B"]}]'
    )
    assert rv.status_code == 200
    assert json.loads(rv.data) == {'success': True}
    rv = client.get(
        flask.url_for('voting.edit_questions', access_key=access_key2))
    assert rv.status_code == 200
    assert b'Editing survey questions' in rv.data
    assert b'Added question' in rv.data and b'choice A' in rv.data and b'choice B' in rv.data


def test_edit_params(client):
    # Test that (some) restrictions are applied
    rv = client.get(
        flask.url_for('voting.edit_params', access_key='invalid-access-key'))
    assert rv.status_code == 403
    with client.session_transaction() as sess:
        sess['username'] = 'csander'
    rv = client.get(
        flask.url_for('voting.edit_params', access_key='invalid-access-key'))
    assert rv.status_code == 200
    assert b'Invalid access key' in rv.data
    assert b'Editing survey' not in rv.data
    # Test successful case
    access_key = list(
        helpers.get_visible_surveys(helpers.get_user_id('csander')))[0][
            'access_key']
    rv = client.get(flask.url_for('voting.edit_params', access_key=access_key))
    assert rv.status_code == 200
    assert b'Editing survey' in rv.data
    assert b"value='ABC'" in rv.data
    assert b'New description' not in rv.data
    yesterday = date.today() + timedelta(days=-1)
    tomorrow = date.today() + timedelta(days=1)
    rv = client.post(
        flask.url_for('voting.save_params', access_key=access_key),
        data=dict(
            title='ABC',
            description='New description',
            start_date=yesterday.strftime(helpers.YYYY_MM_DD),
            start_hour='12',
            start_minute='00',
            start_period='P',
            end_date=tomorrow.strftime(helpers.YYYY_MM_DD),
            end_hour='12',
            end_minute='00',
            end_period='P',
            group=''),
        follow_redirects=False)
    assert rv.status_code == 302
    assert rv.location == flask.url_for(
        'voting.edit_questions', access_key=access_key)
    rv = client.get(flask.url_for('voting.edit_params', access_key=access_key))
    assert rv.status_code == 200
    assert b'New description' in rv.data  # assert that description has changed
    # Error cases for saving params
    with client.session_transaction() as sess:
        sess['username'] = 'reng'
    rv = client.post(
        flask.url_for('voting.save_params', access_key=access_key),
        follow_redirects=False)
    assert rv.status_code == 200
    assert b'You are not the creator of this survey' in rv.data
    with client.session_transaction() as sess:
        del sess['username']
    rv = client.post(
        flask.url_for('voting.save_params', access_key=access_key),
        follow_redirects=False)
    assert rv.status_code == 403


def test_close(client):
    with client.session_transaction() as sess:
        sess['username'] = 'csander'

    def make_survey(start_date):
        rv = client.post(
            flask.url_for('voting.make_survey'),
            data=dict(
                title='ABC',
                description='',
                start_date=start_date.strftime(helpers.YYYY_MM_DD),
                start_hour='12',
                start_minute='00',
                start_period='P',
                end_date=(start_date + timedelta(
                    days=2)).strftime(helpers.YYYY_MM_DD),
                end_hour='12',
                end_minute='00',
                end_period='P',
                public='on',
                group=''),
            follow_redirects=False)
        assert rv.status_code == 302
        return re.search(r'[A-Za-z0-9]{64}', rv.location)[0]

    past = make_survey(date.today() + timedelta(days=-3))
    present = make_survey(date.today() + timedelta(days=-1))
    future = make_survey(date.today() + timedelta(days=1))
    # Test error cases
    rv = client.get(flask.url_for('voting.close_survey', access_key=past))
    assert rv.status_code == 200
    assert json.loads(rv.data) == {
        'success': False,
        'message': 'Cannot modify a survey after it has closed'
    }
    rv = client.get(flask.url_for('voting.close_survey', access_key=future))
    assert rv.status_code == 200
    assert json.loads(rv.data) == {
        'success': False,
        'message': 'Survey has not opened yet'
    }
    # Test successful case
    rv = client.get(flask.url_for('voting.close_survey', access_key=present))
    assert rv.status_code == 200
    assert json.loads(rv.data) == {'success': True}
    rv = client.get(flask.url_for('voting.close_survey', access_key=present))
    assert rv.status_code == 200
    assert json.loads(rv.data) == {
        'success': False,
        'message': 'Cannot modify a survey after it has closed'
    }


def test_delete(client):
    # Test error cases
    rv = client.delete(
        flask.url_for('voting.delete_survey', access_key='invalid-access-key'))
    assert rv.status_code == 403
    with client.session_transaction() as sess:
        sess['username'] = 'reng'
    rv = client.delete(
        flask.url_for('voting.delete_survey', access_key='invalid-access-key'))
    assert rv.status_code == 200
    assert json.loads(rv.data) == {
        'success': False,
        'message': 'Invalid access key'
    }
    access_key = helpers.get_closed_surveys(
        helpers.get_user_id('csander'))[0]['access_key']
    rv = client.delete(
        flask.url_for('voting.delete_survey', access_key=access_key))
    assert rv.status_code == 200
    assert json.loads(rv.data) == {
        'success': False,
        'message': 'You are not the creator of this survey'
    }
    with client.session_transaction() as sess:
        sess['username'] = 'csander'
    # Test successful case
    rv = client.delete(
        flask.url_for('voting.delete_survey', access_key=access_key))
    assert rv.status_code == 200
    assert json.loads(rv.data) == {'success': True}
    # Test that it was deleted
    rv = client.delete(
        flask.url_for('voting.delete_survey', access_key=access_key))
    assert rv.status_code == 200
    assert json.loads(rv.data) == {
        'success': False,
        'message': 'Invalid access key'
    }


def test_submit(client):
    with client.session_transaction() as sess:
        sess['username'] = 'csander'
    yesterday = date.today() + timedelta(days=-1)
    tomorrow = date.today() + timedelta(days=1)
    rv = client.post(
        flask.url_for('voting.make_survey'),
        data=dict(
            title='Response test',
            description='',
            start_date=yesterday.strftime(helpers.YYYY_MM_DD),
            start_hour='12',
            start_minute='00',
            start_period='P',
            end_date=tomorrow.strftime(helpers.YYYY_MM_DD),
            end_hour='12',
            end_minute='00',
            end_period='P',
            public='on',
            group=''),
        follow_redirects=False)
    access_key = [
        survey
        for survey in helpers.get_visible_surveys(
            helpers.get_user_id('csander'))
        if survey['title'] == 'Response test'
    ][0]['access_key']
    assert rv.status_code == 302
    assert rv.location == flask.url_for(
        'voting.edit_questions', access_key=access_key)
    with client.session_transaction() as sess:
        del sess['username']
    survey_id = helpers.get_survey_data(access_key)['survey_id']
    question_types = helpers.get_question_types()
    helpers.set_questions(survey_id, [{ # question id 8
        'title': 'Question A',
        'description': '',
        'type': question_types['Dropdown'],
        'choices': ['1', '2', '3'] # choices 12, 13, 14
    }, {  # question id 9
        'title': 'Question B',
        'description': 'bbb',
        'type': question_types['Short text']
    }, { # question id 10
        'title': 'Question C',
        'description': 'ccc',
        'type': question_types['Checkboxes'],
        'choices': ['a', 'b', 'c'] # choices 15, 16, 17
    }, { # question id 11
        'title': 'Question D',
        'description': '',
        'type': question_types['Long text']
    }, { # question id 12
        'title': 'Question E',
        'description': '',
        'type': question_types['Elected position'],
        'choices': ['do', 're', 'me'] # choices 18, 19, 20
    }])
    # Test (some) restriction
    rv = client.post(
        flask.url_for('voting.submit', access_key=access_key), data='')
    assert rv.status_code == 200
    assert json.loads(rv.data) == {
        'success': False,
        'message': 'Must be logged in to take survey'
    }
    with client.session_transaction() as sess:
        sess['username'] = 'csander'
    # Test questions match
    rv = client.post(
        flask.url_for('voting.submit', access_key=access_key),
        data='{"responses":[{"question":1}]}')
    assert rv.status_code == 200
    assert json.loads(rv.data) == {
        'success': False,
        'message': 'Survey questions have changed'
    }
    # Test response value errors
    rv = client.post(
        flask.url_for('voting.submit', access_key=access_key),
        data="""
            {
                "responses":[
                    {"question":8,"response":"4"},
                    {"question":9},
                    {"question":10},
                    {"question":11},
                    {"question":12}
                ]
            }
        """)
    assert rv.status_code == 200
    assert json.loads(rv.data) == {
        'success': False,
        'message': 'Invalid response to dropdown'
    }
    rv = client.post(
        flask.url_for('voting.submit', access_key=access_key),
        data="""
            {
                "responses":[
                    {"question":8,"response":15},
                    {"question":9},
                    {"question":10},
                    {"question":11},
                    {"question":12}
                ]
            }
        """)
    assert rv.status_code == 200
    assert json.loads(rv.data) == {
        'success': False,
        'message': 'Invalid choice for dropdown'
    }
    rv = client.post(
        flask.url_for('voting.submit', access_key=access_key),
        data="""
            {
                "responses":[
                    {"question":8,"response":13},
                    {"question":9,"response":10},
                    {"question":10},
                    {"question":11},
                    {"question":12}
                ]
            }
        """)
    assert rv.status_code == 200
    assert json.loads(rv.data) == {
        'success': False,
        'message': 'Invalid text response'
    }
    rv = client.post(
        flask.url_for('voting.submit', access_key=access_key),
        data="""
            {
                "responses":[
                    {"question":8,"response":13},
                    {"question":9,"response":"shorty"},
                    {"question":10,"response":10},
                    {"question":11},
                    {"question":12}
                ]
            }
        """)
    assert rv.status_code == 200
    assert json.loads(rv.data) == {
        'success': False,
        'message': 'Invalid response to checkboxes'
    }
    rv = client.post(
        flask.url_for('voting.submit', access_key=access_key),
        data="""
            {
                "responses":[
                    {"question":8,"response":13},
                    {"question":9,"response":"shorty"},
                    {"question":10,"response":["3"]},
                    {"question":11},
                    {"question":12}
                ]
            }
        """)
    assert rv.status_code == 200
    assert json.loads(rv.data) == {
        'success': False,
        'message': 'Invalid response to checkboxes'
    }
    rv = client.post(
        flask.url_for('voting.submit', access_key=access_key),
        data="""
            {
                "responses":[
                    {"question":8,"response":13},
                    {"question":9,"response":"shorty"},
                    {"question":10,"response":[14]},
                    {"question":11},
                    {"question":12}
                ]
            }
        """)
    assert rv.status_code == 200
    assert json.loads(rv.data) == {
        'success': False,
        'message': 'Invalid choice for checkboxes'
    }
    rv = client.post(
        flask.url_for('voting.submit', access_key=access_key),
        data="""
            {
                "responses":[
                    {"question":8,"response":13},
                    {"question":9,"response":"shorty"},
                    {"question":10,"response":[15,17]},
                    {"question":11,"response":100},
                    {"question":12}
                ]
            }
        """)
    assert rv.status_code == 200
    assert json.loads(rv.data) == {
        'success': False,
        'message': 'Invalid text response'
    }
    for position_response in ('NO', [True], [[1]]):
        rv = client.post(
            flask.url_for('voting.submit', access_key=access_key),
            data=json.dumps({
                'responses': [{
                    'question': 8,
                    'response': 13
                }, {
                    'question': 9,
                    'response': 'shorty'
                }, {
                    'question': 10,
                    'response': [15, 17]
                }, {
                    'question': 11,
                    'response': 'looooooooong'
                }, {
                    'question': 12,
                    'response': position_response
                }]
            }))
        assert rv.status_code == 200
        assert json.loads(rv.data) == {
            'success': False,
            'message': 'Invalid response to elected position'
        }
    for position_choice in ({'choice_id': 2}, {'user_id': -100}):
        rv = client.post(
            flask.url_for('voting.submit', access_key=access_key),
            data=json.dumps({
                'responses': [{
                    'question': 8,
                    'response': 13
                }, {
                    'question': 9,
                    'response': 'shorty'
                }, {
                    'question': 10,
                    'response': [15, 17]
                }, {
                    'question': 11,
                    'response': 'looooooooong'
                }, {
                    'question': 12,
                    'response': [[position_choice]]
                }]
            }))
        assert rv.status_code == 200
        assert json.loads(rv.data) == {
            'success': False,
            'message': 'Invalid choice for elected position'
        }
    duplicate_responses = ([[{'choice_id': 19}, {'choice_id': 19}]], )
    duplicate_responses += ([[None], [{'user_id': 3}], [None]], )
    for position_response in duplicate_responses:
        rv = client.post(
            flask.url_for('voting.submit', access_key=access_key),
            data=json.dumps({
                'responses': [{
                    'question': 8,
                    'response': 13
                }, {
                    'question': 9,
                    'response': 'shorty'
                }, {
                    'question': 10,
                    'response': [15, 17]
                }, {
                    'question': 11,
                    'response': 'looooooooong'
                }, {
                    'question': 12,
                    'response': position_response
                }]
            }))
        assert rv.status_code == 200
        assert json.loads(rv.data) == {
            'success': False,
            'message': 'Candidate ranked twice for elected position'
        }
    rv = client.post(
        flask.url_for('voting.submit', access_key=access_key),
        data="""
            {
                "responses":[
                    {"question":8,"response":13},
                    {"question":9,"response":"shorty"},
                    {"question":10,"response":[15,17]},
                    {"question":11,"response":"looooooooong"},
                    {"question":12,"response":[[{"user_id":3}],[{"choice_id":19},{"user_id":2}],[null]]}
                ]
            }
        """)
    assert rv.status_code == 200
    assert json.loads(rv.data) == {'success': True}
    assert helpers.get_responses(
        survey_id, helpers.get_user_id('csander')) == [{
            'question_id': 8,
            'title': 'Question A',
            'description': None,
            'type': 1,
            'list_order': 0,
            'choices': {
                12: '1',
                13: '2',
                14: '3'
            },
            'responses': [13]
        }, {
            'question_id': 9,
            'title': 'Question B',
            'description': 'bbb',
            'type': 4,
            'list_order': 1,
            'choices': 0,
            'responses': ['shorty']
        }, {
            'question_id': 10,
            'title': 'Question C',
            'description': 'ccc',
            'type': 2,
            'list_order': 2,
            'choices': {
                15: 'a',
                16: 'b',
                17: 'c'
            },
            'responses': [[15, 17]]
        }, {
            'question_id':
            11,
            'title':
            'Question D',
            'description':
            None,
            'type':
            5,
            'list_order':
            3,
            'choices':
            0,
            'responses': ['looooooooong']
        }, {
            'question_id':
            12,
            'title':
            'Question E',
            'description':
            None,
            'type':
            3,
            'list_order':
            4,
            'choices': {
                18: 'do',
                19: 're',
                20: 'me'
            },
            'responses': [[['Belac Sander'], ['re', 'Robert Eng'], ['NO']]]
        }]

    rv = client.get(flask.url_for('voting.take_survey', access_key=access_key))
    assert rv.status_code == 302
    assert rv.location == flask.url_for(
        'voting.show_my_response', access_key=access_key)


def test_my_response(client):
    access_key = [
        survey
        for survey in helpers.get_visible_surveys(
            helpers.get_user_id('csander'))
        if survey['title'] == 'Response test'
    ][0]['access_key']
    rv = client.get(
        flask.url_for('voting.show_my_response', access_key=access_key))
    assert rv.status_code == 200
    assert b'Must be logged in to see response' in rv.data
    with client.session_transaction() as sess:
        sess['username'] = 'csander'
    rv = client.get(
        flask.url_for('voting.show_my_response', access_key='not-a-real-key'))
    assert rv.status_code == 200
    assert b'Invalid access key' in rv.data
    unresponded_access_key = [
        survey
        for survey in helpers.get_visible_surveys(
            helpers.get_user_id('csander'))
        if survey['title'] != 'Response test'
    ][0]['access_key']
    rv = client.get(
        flask.url_for(
            'voting.show_my_response', access_key=unresponded_access_key))
    assert rv.status_code == 200
    assert b'You have not responded to this survey' in rv.data
    rv = client.get(
        flask.url_for('voting.show_my_response', access_key=access_key))
    assert rv.status_code == 200
    assert b'My responses for Response test' in rv.data


def test_results(client):
    rv = client.get(
        flask.url_for('voting.show_results', access_key='invalid-access-key'))
    assert rv.status_code == 200
    assert b'Invalid access key' in rv.data
    access_key = [
        survey
        for survey in helpers.get_visible_surveys(
            helpers.get_user_id('csander'))
        if survey['title'] == 'Response test'
    ][0]['access_key']
    with client.session_transaction() as sess:
        sess['username'] = 'csander'
    # Test viewing before close
    rv = client.get(
        flask.url_for('voting.show_results', access_key=access_key))
    assert rv.status_code == 200
    assert b'You are not permitted to see the results at this time' in rv.data
    # Test releasing before close
    rv = client.get(
        flask.url_for('voting.release_results', access_key=access_key))
    assert rv.status_code == 200
    assert b'Survey has not yet finished' in rv.data
    # Test after close
    yesterday = date.today() + timedelta(days=-1)
    rv = client.post(
        flask.url_for('voting.save_params', access_key=access_key),
        data=dict(
            title='Response test',
            description='',
            start_date=yesterday.strftime(helpers.YYYY_MM_DD),
            start_hour='12',
            start_minute='00',
            start_period='P',
            end_date=yesterday.strftime(helpers.YYYY_MM_DD),
            end_hour='1',
            end_minute='00',
            end_period='P',
            public='on',
            group=''),
        follow_redirects=False)
    assert rv.status_code == 302
    assert rv.location == flask.url_for(
        'voting.edit_questions', access_key=access_key)
    rv = client.get(
        flask.url_for('voting.show_results', access_key=access_key))
    assert rv.status_code == 200
    assert b'You are not permitted to see the results at this time' not in rv.data
    assert b'Responses:' in rv.data
    assert b'Question A' in rv.data
    assert b'Question B' in rv.data
    assert b'Question C' in rv.data
    assert b'Question D' in rv.data
    assert b'Question E' in rv.data
    assert b'Allow others to see results' in rv.data
    # Test if not creator after close
    with client.session_transaction() as sess:
        del sess['username']
    rv = client.get(
        flask.url_for('voting.show_results', access_key=access_key))
    assert rv.status_code == 200
    assert b'You are not permitted to see the results at this time' in rv.data
    # Test releasing error conditions
    rv = client.get(
        flask.url_for(
            'voting.release_results', access_key='invalid-access-key'),
        follow_redirects=False)
    assert rv.status_code == 403
    with client.session_transaction() as sess:
        sess['username'] = 'reng'
    rv = client.get(
        flask.url_for(
            'voting.release_results', access_key='invalid-access-key'),
        follow_redirects=False)
    assert rv.status_code == 200
    assert b'Invalid access key' in rv.data
    rv = client.get(
        flask.url_for('voting.release_results', access_key=access_key),
        follow_redirects=False)
    assert rv.status_code == 200
    assert b'You are not the creator of this survey' in rv.data
    # Test successful release
    with client.session_transaction() as sess:
        sess['username'] = 'csander'
    rv = client.get(
        flask.url_for('voting.release_results', access_key=access_key),
        follow_redirects=False)
    assert rv.status_code == 302
    assert rv.location == flask.url_for(
        'voting.show_results', access_key=access_key)
    # Test if not creator, but results released
    with client.session_transaction() as sess:
        del sess['username']
    rv = client.get(
        flask.url_for('voting.show_results', access_key=access_key))
    assert rv.status_code == 200
    assert b'You are not permitted to see the results at this time' not in rv.data
    assert b'Responses:' in rv.data
    assert b'Question A' in rv.data
    assert b'Question B' in rv.data
    assert b'Question C' in rv.data
    assert b'Question D' in rv.data
    assert b'Question E' in rv.data
    assert b'Allow others to see results' not in rv.data
