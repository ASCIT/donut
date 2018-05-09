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
    responses =  [[MEMPHIS, NASHVILLE, CHATTANOOGA, KNOXVILLE]] * 42
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
    ruddock_id = get_group_list_data(['group_id'], {'group_name': 'Ruddock House'})[0]['group_id']
    survey_params = [
        {'title': 'Unrestricted', 'group': '', 'end_hour': '12'},
        {'title': 'Ruddock only', 'group': str(ruddock_id), 'end_hour': '1'} # end later
    ]
    yesterday = date.today() + timedelta(days=-1)
    tomorrow = date.today() + timedelta(days=1)
    access_keys = {}
    with client.session_transaction() as sess:
        sess['username'] = 'csander'
    for params in survey_params:
        rv = client.post(flask.url_for('voting.make_survey'), data=dict(
            description='',
            start_date=yesterday.strftime(helpers.YYYY_MM_DD),
            start_hour='12',
            start_minute='00',
            start_period='P',
            end_date=tomorrow.strftime(helpers.YYYY_MM_DD),
            end_minute='00',
            end_period='P',
            public='on',
            **params
        ), follow_redirects=False)
        assert rv.status_code == 302
        access_keys[params['title']] = [url_piece for url_piece in rv.location.split('/') if len(url_piece) == 64][0]
    unrestricted = {
        'title': 'Unrestricted',
        'description': None,
        'end_time': datetime(tomorrow.year, tomorrow.month, tomorrow.day, 12),
        'access_key': access_keys['Unrestricted'],
        'group_id': None
    }
    assert list(helpers.get_public_surveys(helpers.get_user_id('dqu'))) == [ # not a Rudd
        unrestricted
    ]
    assert list(helpers.get_public_surveys(helpers.get_user_id('csander'))) == [
        unrestricted,
        {
            'title': 'Ruddock only',
            'description': None,
            'end_time': datetime(tomorrow.year, tomorrow.month, tomorrow.day, 13),
            'access_key': access_keys['Ruddock only'],
            'group_id': 2
        }
    ]

def test_closed_surveys(client):
    yesterday = date.today() + timedelta(days=-1)
    tomorrow = date.today() + timedelta(days=1)
    survey_params = [
        {
            'title': 'Before',
            'start_date': yesterday.strftime(helpers.YYYY_MM_DD),
            'start_hour': '2',
            'end_date': yesterday.strftime(helpers.YYYY_MM_DD),
            'end_hour': '3'
        },
        {
            'title': 'During',
            'start_date': yesterday.strftime(helpers.YYYY_MM_DD),
            'start_hour': '4',
            'end_date': tomorrow.strftime(helpers.YYYY_MM_DD),
            'end_hour': '5'
        },
        {
            'title': 'After',
            'start_date': tomorrow.strftime(helpers.YYYY_MM_DD),
            'start_hour': '2',
            'end_date': tomorrow.strftime(helpers.YYYY_MM_DD),
            'end_hour': '3'
        }
    ]
    access_keys = {}
    with client.session_transaction() as sess:
        sess['username'] = 'csander'
    for params in survey_params:
        rv = client.post(flask.url_for('voting.make_survey'), data=dict(
            description='',
            start_minute='00',
            start_period='P',
            end_minute='00',
            end_period='P',
            public='on',
            group='',
            **params
        ), follow_redirects=False)
        assert rv.status_code == 302
        access_keys[params['title']] = [url_piece for url_piece in rv.location.split('/') if len(url_piece) == 64][0]
    assert helpers.get_closed_surveys(helpers.get_user_id('reng')) == () # not the creator of 'Before'
    before = [{
        'title': 'Before',
        'description': None,
        'end_time': datetime(yesterday.year, yesterday.month, yesterday.day, 15),
        'access_key': access_keys['Before'],
        'results_shown': 0
    }]
    assert helpers.get_closed_surveys(helpers.get_user_id('csander')) == before
    rv = client.get(flask.url_for('voting.release_results', access_key=access_keys['Before']))
    assert rv.status_code == 302
    assert rv.location == flask.url_for('voting.show_results', access_key=access_keys['Before'])
    before[0]['results_shown'] = 1
    assert helpers.get_closed_surveys(helpers.get_user_id('reng')) == before
    assert helpers.get_closed_surveys(helpers.get_user_id('csander')) == before

def test_survey_data(client):
    access_key = list(helpers.get_public_surveys(1))[0]['access_key']
    yesterday = date.today() + timedelta(days=-1)
    tomorrow = date.today() + timedelta(days=1)
    assert helpers.get_survey_data(access_key) == {
        'survey_id': 1,
        'title': 'Unrestricted',
        'description': None,
        'group_id': None,
        'start_time': datetime(yesterday.year, yesterday.month, yesterday.day, 12),
        'end_time': datetime(tomorrow.year, tomorrow.month, tomorrow.day, 12),
        'creator': 3,
        'auth': 0,
        'results_shown': 0
    }

def test_question_json(client):
    question_types = helpers.get_question_types()
    helpers.set_questions(1, [
        {
            'title': 'A',
            'description': '',
            'type': question_types['Dropdown'],
            'choices': ['1', '2', '3']
        },
        {
            'title': 'B',
            'description': 'bbb',
            'type': question_types['Short text']
        },
        {
            'title': 'C',
            'description': 'ccc',
            'type': question_types['Checkboxes'],
            'choices': ['a', 'b', 'c']
        },
        {
            'title': 'D',
            'description': '',
            'type': question_types['Long text']
        },
        {
            'title': 'E',
            'description': '',
            'type': question_types['Elected position'],
            'choices': ['do', 're', 'me']
        }
    ])
    assert helpers.get_questions_json(1, False) == '[{"title":"A","description":"","type":1,"choices":["1","2","3"]},{"title":"B","description":"bbb","type":4},{"title":"C","description":"ccc","type":2,"choices":["a","b","c"]},{"title":"D","description":"","type":5},{"title":"E","description":"","type":3,"choices":["do","re","me"]}]'
    assert helpers.get_questions_json(1, True) == '[{"question_id":1,"title":"A","description":"","type":1,"choices":["1","2","3"]},{"question_id":2,"title":"B","description":"bbb","type":4},{"question_id":3,"title":"C","description":"ccc","type":2,"choices":["a","b","c"]},{"question_id":4,"title":"D","description":"","type":5},{"question_id":5,"title":"E","description":"","type":3,"choices":["do","re","me"]}]'

# Routes