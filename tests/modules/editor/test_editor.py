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
import os


def test_plain_editor_page(client):
    assert client.get(flask.url_for('editor.editor')).status_code == 403
    assert client.get(flask.url_for('editor.page_list')).status_code == 200
    # Since dude has admin privileges, he should be able to access the editor
    # page.
    with client.session_transaction() as sess:
        sess['username'] = 'dqu'
    assert client.get(flask.url_for('editor.editor')).status_code == 200


def test_text_editor_page(client):
    with client.session_transaction() as sess:
        sess['username'] = 'dqu'
    with app.test_request_context():
        flask.session['username'] = 'dqu'
        helpers.create_page_in_database(
            "Some really really really interesting title",
            "nothing to see here")
        helpers.change_lock_status(
            "Some really really really interesting title", False)
        assert not helpers.is_locked(
            "Some really really really interesting title")
        helpers.create_page_in_database("Some less interesting title",
                                        "or is there")
        helpers.change_lock_status("Some less interesting title", True)
        assert helpers.is_locked("Some less interesting title")
        helpers.change_lock_status("default", True, default=True)
        assert not helpers.is_locked("default")

    rv = client.get(
        flask.url_for(
            'editor.editor',
            title="Some really really really interesting title"))
    assert rv.status_code == 200
    assert b'Some really really really interesting title' in rv.data


def test_path_related_funciton(client):

    helpers.create_page_in_database("TEST_TITLE", "BLAHBLAH")
    assert helpers.get_links() != []

    assert helpers.check_duplicate("TEST TITLE")
    assert not helpers.check_duplicate("doesnt exist")

    links = helpers.get_links()
    titles = [title for title, _ in links.items()]
    assert "TEST_TITLE" in ' '.join(titles)
    with app.test_request_context():
        flask.session['username'] = 'dqu'
        helpers.change_lock_status("TEST TITLE", True)
        assert helpers.is_locked("TEST TITLE")

        helpers.change_lock_status("TEST TITLE", False)
        assert not helpers.is_locked("TEST TITLE")
    client.get(
        flask.url_for('uploads.display', url="TEST_TITLE")).status_code == 200
    helpers.rename_title('TEST_TITLE', 'ANOTHER_Title')

    links = helpers.get_links()
    titles = [title for title, _ in links.items()]
    assert "TEST_TITLE" not in ' '.join(titles)
    assert "ANOTHER_Title" in ' '.join(titles)

    client.get(flask.url_for('uploads.display',
                             url="ANOTHER Title")).status_code == 200
    assert "BLAHBLAH" == helpers.read_markdown('ANOTHER_Title')
    helpers.remove_file_from_db("ANOTHER_Title")
