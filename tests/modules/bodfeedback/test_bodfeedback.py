import flask
from donut.modules.bodfeedback import helpers
from donut.testing.fixtures import client
from datetime import datetime


def test_get_link(client):
    assert helpers.get_link(
        1) == flask.url_for('home') + 'bodfeedback/view/sample_uuid'
    assert helpers.get_link(500) is None
    return


def test_get_id(client):
    assert helpers.get_id('sample_uuid') == 1
    assert helpers.get_id('nonsense') == False
    return


def test_get_messages(client):
    messages = helpers.get_messages(1)
    assert messages[0]['time'] == datetime(2018, 1, 1, 0, 0)
    assert messages[1]['time'] == datetime(2018, 1, 2, 0, 0)
    assert messages[0]['message'] == 'Sample Message'
    assert messages[1]['message'] == 'Sample Message 2'
    assert messages[0]['poster'] == 'Davis'
    assert messages[1]['poster'] == 'Davis'
    assert helpers.get_messages(500) is None


def test_get_summary(client):
    summary = helpers.get_summary(1)
    assert summary['subject'] == 'Sub1'
    assert summary['status'] == 'new_msg'
    summary = helpers.get_summary(2)
    assert summary['subject'] == 'Sub2'
    assert summary['status'] == 'read'
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
    assert fields['emails'] == ['test@example.com', 'test2@example.com']
    assert fields['messages'][0]['message'] == 'Sample Message'
    assert fields['subject'] == 'Sub1'
    assert fields['status'] == 'new_msg'
    assert helpers.get_all_fields(500) is None


def test_get_new_posts(client):
    posts = helpers.get_new_posts()
    assert len(posts) == 1
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
    complaint_id = helpers.register_complaint(data)
    res = helpers.get_all_fields(complaint_id)
    assert res['emails'] == ['joe@example.com', 'joey@example.com']
    assert res['messages'][0]['message'] == 'Sample Message 3'
    assert res['messages'][0]['poster'] == 'Joe Schmo'
    assert res['subject'] == 'Sub1'
    assert res['status'] == 'new_msg'
    assert helpers.register_complaint(None) == False


def test_add_email(client):
    helpers.add_email(1, 'sample_text@example.com', True)
    assert helpers.get_emails(1) == [
        'test@example.com', 'test2@example.com', 'sample_text@example.com'
    ]
    assert helpers.add_email(500, 'text', True) == False


def test_add_msg(client):
    helpers.add_msg(2, 'Test message', 'Test user')
    messages = helpers.get_messages(2)
    assert len(messages) == 2
    assert messages[0]['message'] == 'This course is fun'
    assert messages[0]['poster'] == 'Davis'
    assert messages[1]['message'] == 'Test message'
    assert messages[1]['poster'] == 'Test user'
    helpers.add_msg(2, 'Anonymous message', '')
    messages = helpers.get_messages(2)
    assert len(messages) == 3
    assert messages[2]['poster'] == '(anonymous)'
    assert helpers.get_status(2) == 'new_msg'
    assert helpers.add_msg(500, '', '') == False
