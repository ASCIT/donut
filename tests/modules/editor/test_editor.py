"""
Tests donut/modules/editor/
"""
from datetime import date
import flask
import pytest
from donut.testing.fixtures import client
from donut import app
import donut.modules.core.helpers as core_helpers
from donut.modules.editor import helpers
from donut.modules.editor import routes


def test_plain_editor_page(client):
    assert client.get(flask.url_for('editor.editor')).status_code == 200

def test_text_editor_page(client):
    assert client.get(flask.url_for('editor.editor', input_text='TESTING TESTING', title="TEST")).status_code == 200
    print(client.get(flask.url_for('editor.editor', input_text='TESTING TESTING', title="TEST")))
    print(client.post(flask.url_for('editor.save')))
    #assert flask.request.args['input_text'] == 'TESTING TESTING'
    #assert flask.request.args['title'] == 'TEST'
    #assert client.get(flask.url_for('uploads.display', url="TEST")).status_code == 200


def test_create_list(client):
    assert client.get(flask.url_for('editor.created_list')).status_code == 200
