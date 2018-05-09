"""
Tests donut/modules/rooms/
"""
from datetime import date, datetime, timedelta
import flask
import pytest
from donut.testing.fixtures import client
from donut import app
from donut.modules.groups.helpers import get_group_list_data
from donut.modules.voting import helpers, routes, ranked_pairs


# Ranked pairs
def test_ranked_pairs():
    # Example taken from en.wikipedia.org/wiki/Ranked_pairs
    MEMPHIS = 'Memphis'
    NASHVILLE = 'Nashville'
    CHATTANOOGA = 'Chattanooga'
    KNOXVILLE = 'Knoxville'
    responses = [[MEMPHIS, NASHVILLE, CHATTANOOGA, KNOXVILLE]] * 42
    responses += [[NASHVILLE, CHATTANOOGA, KNOXVILLE, MEMPHIS]] * 26
    responses += [[CHATTANOOGA, KNOXVILLE, NASHVILLE, MEMPHIS]] * 15
    responses += [[KNOXVILLE, CHATTANOOGA, NASHVILLE, MEMPHIS]] * 17
    correct_winners = [NASHVILLE, CHATTANOOGA, KNOXVILLE, MEMPHIS]
    correct_winners = correct_winners[:ranked_pairs.WINNERS_TO_LIST]
    assert ranked_pairs.winners(responses) == correct_winners


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
    assert list(helpers.get_public_surveys(helpers.get_user_id(
        'dqu'))) == [  # not a Rudd
            unrestricted
        ]
    assert list(
        helpers.get_public_surveys(helpers.get_user_id('csander'))) == [
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
    access_key = list(helpers.get_public_surveys(1))[0]['access_key']
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
        'auth':
        0,
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
    ) == '[{"question_id":1,"title":"A","description":"","type":1,"choices":["1","2","3"]},{"question_id":2,"title":"B","description":"bbb","type":4},{"question_id":3,"title":"C","description":"ccc","type":2,"choices":["a","b","c"]},{"question_id":4,"title":"D","description":"","type":5},{"question_id":5,"title":"E","description":"","type":3,"choices":["do","re","me"]}]'


def test_question_ids(client):
    assert helpers.get_question_ids(1) == [1, 2, 3, 4, 5]
    assert helpers.get_question_ids(2) == []


def test_question_type(client):
    assert list(map(helpers.get_question_type, range(1, 6))) == [1, 4, 2, 5, 3]


def test_get_choice(client):
    assert [
        helpers.get_choice(5, choice) for choice in ['do', 're', 'me', 'z']
    ] == [{
        'choice_id': 7
    }, {
        'choice_id': 8
    }, {
        'choice_id': 9
    }, None]


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
        auth='on',
        public='on',
        group='')

    def assert_message(message, params):
        rv = client.post(
            flask.url_for('voting.make_survey'),
            data=params,
            follow_redirects=False)
        assert rv.status_code == 200
        assert message in rv.data

    assert_message(b'Not logged in', default_params)
    with client.session_transaction() as sess:
        sess['username'] = 'csander'
    for delete_param in default_params:
        if delete_param in ['auth', 'public']: continue  # these are optional
        params = default_params.copy()
        del params[delete_param]
        assert_message(b'Invalid form data', params)
    for date_field in ['start_date', 'end_date']:
        assert_message(b'Invalid form data', {**default_params, date_field: '123'})
    for hour_field in ['start_hour', 'end_hour']:
        assert_message(b'Invalid form data', {**default_params, hour_field: 'abc'})
        assert_message(b'Invalid form data', {**default_params, hour_field: '0'})
        assert_message(b'Invalid form data', {**default_params, hour_field: '13'})
    for minute_field in ['start_minute', 'end_minute']:
        assert_message(b'Invalid form data', {**default_params, minute_field: 'abc'})
        assert_message(b'Invalid form data', {**default_params, minute_field: '-1'})
        assert_message(b'Invalid form data', {**default_params, minute_field: '60'})
    for period_field in ['start_period', 'end_period']:
        assert_message(b'Invalid form data', {**default_params, period_field: 'a'})
        assert_message(b'Invalid form data', {**default_params, period_field: ''})
    assert_message(b'Invalid form data', {**default_params, 'group': 'a'})
    assert_message(b'Start must be before end', {**default_params, 'start_date': '2018-05-09', 'end_date': '2018-05-08'})
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
        'auth':
        0,
        'public':
        1
    }
    helpers.update_survey_params(1,
                                 {'title': 'ABC',
                                  'group_id': 2,
                                  'auth': True})
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
        'auth':
        1,
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
        list(helpers.get_public_surveys(csander))[0]['access_key'],
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
        list(helpers.get_public_surveys(csander))[1]['access_key'],
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
            '[7, -1, 9, -2, null]'
        ])
    assert helpers.some_responses_for_survey(1)
    assert helpers.get_results(1) == [{
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
        'question_id':
        4,
        'title':
        'D',
        'description':
        None,
        'type':
        5,
        'list_order':
        3,
        'responses': ['Lorem ipsum dolor sit amet'],
        'results': [('Lorem ipsum dolor sit amet', 1)]
    }, {
        'question_id':
        5,
        'title':
        'E',
        'description':
        None,
        'type':
        3,
        'list_order':
        4,
        'choices': {
            7: 'do',
            8: 're',
            9: 'me'
        },
        'responses': [[7, -1, 9, -2, None]],
        'results': ['do', 'David Qu', 'me'],
        'filled_responses': [['do', 'David Qu', 'me', 'Robert Eng', 'NO']]
    }]
    with app.test_request_context():
        flask.session['username'] = 'dqu'
        # Invalid elected position response
        helpers.set_responses([5], ['["abc"]'])
    with pytest.raises(
            Exception, message='Unrecognized elected position vote'):
        helpers.get_results(1)


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
