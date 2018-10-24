import flask
from donut.modules.bodfeedback import helpers
from donut.testing.fixtures import client
from datetime import datetime


def test_get_link(client):
    assert helpers.get_link(
        1) == flask.url_for('home') + 'bodfeedback/view/sample_uuid'
    assert helpers.get_link(500) is None


def test_get_id(client):
    assert helpers.get_id('sample_uuid') == 1
    assert helpers.get_id('nonsense') == False


def test_get_messages(client):
    messages = helpers.get_messages(1)
    assert messages == [{
        'time': datetime(2018, 1, 1, 0, 0),
        'poster': 'Davis',
        'message': 'Sample Message',
        'message_id': 1
    }, {
        'time': datetime(2018, 1, 2, 0, 0),
        'message': 'Sample Message 2',
        'poster': 'Davis',
        'message_id': 2
    }]
    assert helpers.get_messages(500) is None


def test_get_summary(client):
    summary = helpers.get_summary(1)
    assert summary == {'subject': 'Sub1', 'status': 'new_msg'}
    summary = helpers.get_summary(2)
    assert summary == {'subject': 'Sub2', 'status': 'read'}
    assert helpers.get_summary(500) is None


def test_get_subject(client):
    assert helpers.get_subject(1) == 'Sub1'
    assert helpers.get_subject(2) == 'Sub2'
    assert helpers.get_subject(500) is None


def test_get_status(client):
    assert helpers.get_status(1) == 'new_msg'
    assert helpers.get_status(2) == 'read'
    assert helpers.get_status(500) is None


def test_mark_read(client):
    helpers.mark_read(1)
    assert helpers.get_status(1) == 'read'
    helpers.mark_unread(1)
    assert helpers.get_status(1) == 'new_msg'
    assert helpers.mark_read(500) == False
    assert helpers.mark_unread(500) == False


def test_get_emails(client):
    assert helpers.get_emails(1) == ['test@example.com', 'test2@example.com']
    assert helpers.get_emails(2) == []
    assert helpers.get_emails(500) == []


def test_get_all_fields(client):
    fields = helpers.get_all_fields(1)
    expected = {
        'emails': ['test@example.com', 'test2@example.com'],
        'messages': [{
            'message': 'Sample Message',
            'message_id': 1,
            'poster': 'Davis',
            'time': datetime(2018, 1, 1, 0, 0)
        }, {
            'message': 'Sample Message 2',
            'message_id': 2,
            'poster': 'Davis',
            'time': datetime(2018, 1, 2, 0, 0)
        }],
        'subject':
        'Sub1',
        'status':
        'new_msg'
    }
    assert fields == expected
    assert helpers.get_all_fields(500) is None


def test_get_new_posts(client):
    posts = helpers.get_new_posts()
    assert posts == [{
        'complaint_id': 1,
        'subject': 'Sub1',
        'status': 'new_msg',
        'uuid': 'sample_uuid',
        'message': 'Sample Message 2',
        'poster': 'Davis',
        'time': datetime(2018, 1, 2)
    }]


def test_register_complaint(client):
    data = {
        'subject': 'Sub1',
        'msg': 'Sample Message 3',
        'name': 'Joe Schmo',
        'email': 'joe@example.com, joey@example.com'
    }
    complaint_id = helpers.register_complaint(data, False)
    res = helpers.get_all_fields(complaint_id)
    expected_without_messages = {
        'subject': 'Sub1',
        'status': 'new_msg',
        'emails': ['joe@example.com', 'joey@example.com']
    }
    expected_messages = [{
        'message': 'Sample Message 3',
        'poster': 'Joe Schmo',
        'message_id': 4
    }]
    res_without_messages = {k: v for k, v in res.items() if k != 'messages'}
    res_messages = [{k: v
                     for (k, v) in r.items() if k != 'time'}
                    for r in res['messages']]
    assert res_without_messages == expected_without_messages
    assert res_messages == expected_messages
    assert helpers.register_complaint(None) == False


def test_add_email(client):
    helpers.add_email(1, 'sample_text@example.com', False)
    assert helpers.get_emails(1) == [
        'test@example.com', 'test2@example.com', 'sample_text@example.com'
    ]
    assert helpers.add_email(500, 'text', False) == False


def test_add_msg(client):
    helpers.add_msg(2, 'Test message', 'Test user', False)
    messages = helpers.get_messages(2)
    messages_without = [{
        k: v
        for (k, v) in message.items() if k == 'message' or k == 'poster'
    } for message in messages]
    expected_messages = [{
        'message': 'This course is fun',
        'poster': 'Davis',
    }, {
        'message': 'Test message',
        'poster': 'Test user',
    }]
    assert messages_without == expected_messages
    helpers.add_msg(2, 'Anonymous message', '', False)
    messages = helpers.get_messages(2)
    messages_without = [{
        k: v
        for (k, v) in message.items() if k == 'message' or k == 'poster'
    } for message in messages]
    assert len(messages) == 3
    assert messages_without == expected_messages + [{
        'message':
        'Anonymous message',
        'poster':
        '(anonymous)'
    }]
    assert helpers.get_status(2) == 'new_msg'
    assert helpers.add_msg(500, '', '') == False
