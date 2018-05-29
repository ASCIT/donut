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


def test_routes(client):
    assert client.get(flask.url_for('uploads.uploads')).status_code == 200
    assert client.get(flask.url_for('uploads.uploaded_list')).status_code == 200

def test_get_links(client):
    assert helpers.get_links == []

def test_allowed_file(client):
    assert helpers.allowed_file("bleh.bleh") == ""
    assert helpers.allowed_file("bleh.JPg") == "bleh.jpg"
    assert helpers.allowed_file("bleh.GiF") == "bleh.gif"
    assert helpers.allowed_file("bleh.PDF") == "bleh.pdf"
