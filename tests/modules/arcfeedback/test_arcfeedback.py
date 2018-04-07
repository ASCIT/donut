import flask
from donut.modules.arcfeedback import helpers
from donut.testing.fixtures import client

def test_get_link(client):
    assert(helpers.get_link(1) == flask.url_for('home') + 'arcfeedback/view/sample_uuid')    
    assert(helpers.get_link(500) is None)
    return
        
def test_get_id(client):
    assert(helpers.get_id('sample_uuid') == 1)
    assert(helpers.get_id('nonsense') == False)
    return

'''def test_get_messages(client):
    

def test_get_summary(client):


def test_get_course(client):


def test_get_status(client):


def test_get_emails(client):


def test_get_all_fields(client):


def get_new_posts(client):


def test_register_complaint(client):


def test_add_email(client):


def test_add_message(client):
    

def test_api_add_message(client):


def test_api_view_complaint(client):

'''
