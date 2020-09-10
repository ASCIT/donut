import flask
from donut.modules.newsgroups import helpers
from donut.testing.fixtures import client
from datetime import datetime
from donut.default_permissions import Permissions


def test_get_newsgroups(client):
    assert helpers.get_newsgroups() == [{
        'group_name': 'Donut Devteam',
        'group_id': 1
    }, {
        'group_name': 'IHC',
        'group_id': 3
    }]


def test_get_my_newsgroups(client):
    assert helpers.get_my_newsgroups(5) == [{
        'group_name': 'IHC',
        'group_id': 3
    }]


def test_get_can_send_groups(client):
    expected_groups = [{
        'group_name': 'IHC',
        'group_id': 3
    }, {
        'group_name': 'Donut Devteam',
        'group_id': 1
    }]
    groups = helpers.get_my_newsgroups(5, True)
    assert len(groups) == len(expected_groups)
    assert [group for group in groups if group not in expected_groups] == []
    # anyone can send
    assert helpers.get_my_newsgroups(100, True) == groups[1:]
    # admin can send to any group
    groups = helpers.get_my_newsgroups(1, True)
    assert len(groups) == len(expected_groups)
    assert [group for group in groups if group not in expected_groups] == []


def test_get_my_positions(client):
    assert helpers.get_posting_positions(3, 5) == [{
        'pos_name': 'IHC Member',
        'pos_id': 5
    }]
    assert helpers.get_posting_positions(1, 5) == []

    # Admin can post to any group
    assert helpers.get_posting_positions(9, 1) == [{
        'pos_name':
        'Donut Devteam Head',
        'pos_id':
        1
    }]


def test_get_user_actions(client):
    assert helpers.get_user_actions(5, 3) == {
        'send': 1,
        'control': 0,
        'receive': 1
    }

    # user is not part of group but is admin
    assert helpers.get_user_actions(1, 5) == {
        'send': 1,
        'control': 1,
        'receive': 0
    }


def test_email_newsgroup(client):
    data = {
        'group': 1,
        'subject': 'Subj',
        'plain': 'msg to donut',
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
        assert res[key] == expected[key]
    expected['group_name'] = 'Donut Devteam'
    expected['group_id'] = 1
    res = helpers.get_post(1)
    for key in expected:
        assert res[key] == expected[key]


def test_subscriptions(client):
    helpers.apply_subscription(5, 1)
    assert helpers.get_applications(1) == [{
        'user_id': 5,
        'group_id': 1,
        'name': 'Rachel Lin',
        'email': 'rlin@caltech.edu'
    }]
    helpers.remove_application(5, 1)
    assert helpers.get_applications(1) == ()


def test_get_owners(client):
    res = helpers.get_owners(2)
    res = sorted(res, key=lambda owner: owner['user_id'])
    assert res == [{
        'user_id': 2,
        'pos_name': 'President',
        'full_name': 'Robert Eng'
    }, {
        'user_id': 4,
        'pos_name': 'President',
        'full_name': 'Sean Yu'
    }]
