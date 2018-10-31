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
    assert client.get(flask.url_for('editor.created_list')).status_code == 200


def test_text_editor_page(client):
    assert client.get(
        flask.url_for(
            'editor.editor', input_text='TESTING TESTING',
            title="TEST")).status_code == 403


def test_path_related_funciton(client):
    helpers.remove_link("TEST_TITLE")
    helpers.remove_link("ANOTHER_TITLE")
    links = helpers.get_links()
    titles = []
    for (discard, title) in links:
        titles.append(title)
    assert "TEST TITLE" not in ' '.join(titles)
    assert "ANOTHER TITLE" not in ' '.join(titles)

    helpers.write_markdown("BLAHBLAH", "TEST TITLE")
    root = os.path.join(flask.current_app.root_path,
                        flask.current_app.config["UPLOAD_WEBPAGES"])
    assert helpers.get_links() != []

    links = helpers.get_links()
    titles = [title for _, title in links]
    assert "TEST TITLE" in ' '.join(titles)

    client.get(
        flask.url_for('uploads.display', url="TEST TITLE")).status_code == 403
    helpers.rename_title('TEST_TITLE', 'ANOTHER_TITLE')

    links = helpers.get_links()
    titles = []
    for (discard, title) in links:
        titles.append(title)
    assert "TEST TITLE" not in ' '.join(titles)
    assert "ANOTHER TITLE" in ' '.join(titles)

    client.get(flask.url_for('uploads.display',
                             url="ANOTHER TITLE")).status_code == 403
    assert "BLAHBLAH" == helpers.read_markdown('ANOTHER_TITLE')