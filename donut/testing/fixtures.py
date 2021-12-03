import pytest

import flask
import pymysql.cursors
import donut
from donut import app


@pytest.fixture
def client():
    donut.init("test")
    # Need to specify a server, since test_client doesn't do that for us.
    app.config["SERVER_NAME"] = "127.0.0.1"
    app.config["SESSION_COOKIE_DOMAIN"] = False  # suppress Flask warning
    app.config["JSONIFY_PRETTYPRINT_REGULAR"] = False

    # Establish an application context before running the tests.
    with app.app_context():
        flask.g.pymysql_db = donut.make_db()
        assert flask.g.pymysql_db

        yield app.test_client()

        flask.g.pymysql_db.close()
