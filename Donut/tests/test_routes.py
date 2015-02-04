import flask

from Donut.tests.fixtures import *
from Donut import app

def testHome(client):
  rv = client.get(flask.url_for('home'))

  assert rv.status_code == 200
  assert "Hello world!" in rv.data
