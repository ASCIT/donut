from flask import url_for

from fixtures import *
from Donut import app

def testHome(client):
  rv = client.get(url_for('home'))

  assert rv.status_code == 200
  assert "Hello world!" in rv.data
