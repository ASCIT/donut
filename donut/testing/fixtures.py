import pytest

import flask
import sqlalchemy
import donut
from donut import app, init


@pytest.fixture
def client():
    donut.init("test")
    # Need to specify a server, since test_client doesn't do that for us.
    app.config["SERVER_NAME"] = "127.0.0.1"

    # Establish an application context before running the tests.
    ctx = app.app_context()
    ctx.push()
    if 'DB_URI' in app.config:
        engine = sqlalchemy.create_engine(
            app.config['DB_URI'], convert_unicode=True)
        flask.g.db = engine.connect()
        flask.g.tx = flask.g.db.begin()

    yield app.test_client()
    flask.g.tx.rollback()
    flask.g.db.close()
