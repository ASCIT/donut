import flask

from donut.testing.fixtures import client
from donut import app


def test_home(client):
    rv = client.get(flask.url_for('home'))

    assert rv.status_code == 200
