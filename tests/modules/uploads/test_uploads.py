"""
Tests donut/modules/editor/
"""
from datetime import date
import flask
import pytest
from donut.testing.fixtures import client
from donut import app
import donut.modules.core.helpers as core_helpers
from donut.modules.uploads import helpers
from donut.modules.uploads import routes
from donut.modules.editor import helpers as editor_helpers
import os


def test_routes(client):
    assert client.get(flask.url_for('uploads.uploads')).status_code == 403
    assert client.get(
        flask.url_for('uploads.uploaded_list')).status_code == 200


def test_get_links(client):

    helpers.remove_link("SOME_TITLE")
    links = helpers.get_links()
    titles = []
    for (discard, title) in links:
        titles.append(title)
    assert "SOME_TITLE" not in ''.join(titles)

    path = os.path.join(flask.current_app.root_path,
                        flask.current_app.config["UPLOAD_FOLDER"],
                        "SOME.TITLE" + ".jpg")

    f = open(path, "w+")
    f.close()
    links = helpers.get_links()
    titles = [title for _, title in links]
    assert "SOME.TITLE" in ''.join(titles)

    editor_helpers.write_markdown("BLEH", "ANOTHER_TITLE")
    assert "BLEH" == helpers.read_page("ANOTHER_TITLE")

    helpers.remove_link("SOME.TITLE")
    links = helpers.get_links()
    titles = []
    for (discard, title) in links:
        titles.append(title)
    assert "SOME.TITLE" not in ''.join(titles)


def test_allowed_file(client):
    assert not helpers.allowed_file("bleh.bleh")
    assert helpers.allowed_file("bleh.JPg")
    assert helpers.allowed_file("bleh.GiF")
    assert helpers.allowed_file("bleh.PDF")
