"""
Tests donut/modules/courses
"""
import flask
import pytest
from donut.testing.fixtures import client
from donut import app
from donut.modules.courses import helpers, routes

# Helpers

# Routes


def test_planner(client):
    rv = client.get(flask.url_for('courses.planner'))
    assert rv.status_code == 200


def test_scheduler(client):
    rv = client.get(flask.url_for('courses.scheduler'))
    assert rv.status_code == 200
