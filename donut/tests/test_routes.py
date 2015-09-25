import flask

from donut.tests.fixtures import client
from donut import app

def testHome(client):
  rv = client.get(flask.url_for('home'))

  assert rv.status_code == 200
