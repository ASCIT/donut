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
        helpers.change_lock_status(
            "Some really really really interesting title", False)

    rv = client.get(
        flask.url_for(
            'editor.editor',
            title="Some really really really interesting title"))
    assert rv.status_code == 200
    assert b'Some really really really interesting title' in rv.data


def test_path_related_funciton(client):
    helpers.remove_link("TEST TITLE")
    helpers.remove_link("ANOTHER Title")
    links = helpers.get_links()
    titles = [title for title, _ in links.items()]
    assert "TEST TITLE" not in ' '.join(titles)
    assert "ANOTHER Title" not in ' '.join(titles)

    helpers.write_markdown("BLAHBLAH", "TEST TITLE")
    root = os.path.join(flask.current_app.root_path,
                        flask.current_app.config["UPLOAD_WEBPAGES"])
    assert helpers.get_links() != []

    assert helpers.check_duplicate("TEST TITLE")
    assert not helpers.check_duplicate("doesnt exist")

    links = helpers.get_links()
    titles = [title for title, _ in links.items()]
    assert "TEST TITLE" in ' '.join(titles)
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
    assert "TEST TITLE" not in ' '.join(titles)
    assert "ANOTHER Title" in ' '.join(titles)

    client.get(flask.url_for('uploads.display',
                             url="ANOTHER Title")).status_code == 200
    assert "BLAHBLAH" == helpers.read_markdown('ANOTHER_Title')
    helpers.remove_link("ANOTHER_Title")
