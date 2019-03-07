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
from werkzeug.datastructures import FileStorage


def test_routes(client):
    assert client.get(flask.url_for('uploads.uploads')).status_code == 403
    assert client.get(
        flask.url_for('uploads.uploaded_list')).status_code == 200


def test_get_links(client):

    helpers.remove_link("SOME_TITLE")
    links = helpers.get_links()
    titles = []
    titles = [title for title, _ in links.items()]
    assert "SOME_TITLE" not in ''.join(titles)

    path = os.path.join(flask.current_app.root_path,
                        flask.current_app.config["UPLOAD_FOLDER"],
                        "SOME.title.jpg")

    f = open(path, "w+")
    f.close()
    links = helpers.get_links()
    titles = [title for title, _ in links.items()]
    assert "SOME.title" in ''.join(titles)

    editor_helpers.write_markdown("BLEH", "ANOTHER_TITLE")
    assert "BLEH" == helpers.read_page("ANOTHER_TITLE")
    assert None == helpers.read_page("This no exist")

    editor_helpers.remove_link("ANOTHER TITLE")
    helpers.remove_link("SOME.title.jpg")
    links = helpers.get_links()
    titles = []
    titles = [title for title, _ in links.items()]
    assert "SOME.title" not in ''.join(titles)


def test_allowed_file(client):

    # Generate a random file that's 11 mb
    file_name_max = 'max_test_file.txt'
    file_size_max = 1024 * 1024 * 11  # size in bytes
    f = open(file_name_max, "wb")
    f.write("0".encode() * file_size_max)
    f.seek(0)
    test_file_max = FileStorage(f)
    assert helpers.check_valid_file(
        test_file_max) == "File size larger than 10 mb"
    # Otherwise file.seek doesn't work
    f.close()

    # Clean up test files.
    os.remove(file_name_max)

    # Generate a random file that should be fine
    file_name_min = 'min_test_file.txt'
    file_size_min = 1

    uploads = os.path.join(flask.current_app.root_path,
                           flask.current_app.config['UPLOAD_FOLDER'])
    f = open(file_name_min, "wb")
    f.write("0".encode() * file_size_min)
    f.seek(0)
    test_file_min = FileStorage(f)

    # Since we create the file inside the test directory, this
    # should return "" because there are no duplicates
    assert helpers.check_valid_file(test_file_min) == ""
    f.close()

    # This time, we create and save a test file at where it would have
    # been saved in production. Calling check_valid_file
    # should now return "Duplicate title".
    f = open(os.path.join(uploads, file_name_min), 'w')
    f.write('why is file seek at the end???')
    f.seek(0)
    test_dup = FileStorage(f)
    assert helpers.check_valid_file(test_dup) == "Duplicate title"
    f.close()

    # Clean up created files
    os.remove(os.path.join(uploads, file_name_min))
    os.remove(file_name_min)

    assert not helpers.allowed_file("bleh.bleh")
    assert helpers.allowed_file("bleh.JPg")
    assert helpers.allowed_file("bleh.GiF")
    assert helpers.allowed_file("bleh.PDF")
