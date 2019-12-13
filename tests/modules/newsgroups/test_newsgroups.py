import flask
from donut.modules.newsgroups import helpers
from donut.testing.fixtures import client
from datetime import datetime

def test_get_newsgroups(client):
    assert helpers.get_newsgroups() == [{
        'group_name': 'Donut Devteam',
        'group_id': 1
    }, {
        'group_name': 'IHC',
        'group_id': 3
    }]

def test_get_my_newsgroups(client):
    assert helpers.get_my_newsgroups(1) == [{
        'group_name': 'Donut Devteam',
        'group_id': 1
    }]

def test_get_can_send_groups(client):
    assert helpers.get_can_send_groups(1) == [{
        'group_name': 'Donut Devteam',
        'group_id': 1
    }, {
        'group_name': 'BoD',
        'group_id': 4
    }]
    
    assert helpers.get_can_send_groups(100) == [{
        'group_name': 'BoD',
        'group_id': 4
    }]

def test_get_my_positions(client):
    assert helpers.get_my_positions(1, 1) == [{
        'pos_name': 'Head',
        'pos_id': 1
    }]
    assert helpers.get_my_positions(3, 1) is None
    
def test_email_newsgroup(client):
    data = {
        'group': 1, 
        'subject': 'Subj',
        'msg': 'msg to donut',
        'poster': 'Head'
    }
    helpers.insert_email(1, data)
    res = helpers.get_past_messages(1, 1)[0]
    expected = {
        'subject': 'Subj',
        'message': 'msg to donut',
        'user_id': 1,
        'post_as': 'Head'
    }
    for key in expected:
        assert expected[key] == res[key]
