from flask import url_for

from Donut.tests.fixtures import *
from Donut import app

def testHome(client):
  rv = client.get(url_for('example.home'))

  assert rv.status_code == 200
  assert "Example page" in rv.data
