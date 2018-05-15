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
    app.config["JSONIFY_PRETTYPRINT_REGULAR"] = False

    # Establish an application context before running the tests.
    ctx = app.app_context()
    ctx.push()
    #if 'DB_URI' in app.config:
    #    engine = sqlalchemy.create_engine(
    #        app.config['DB_URI'], convert_unicode=True)
    #    flask.g.db = engine.connect()
    #    flask.g.tx = flask.g.db.begin()
    if ('DB_NAME' in app.config and 'DB_USER' in app.config
            and 'DB_PASSWORD' in app.config):
        connection = pymysql.connect(
            host='localhost',
            database=app.config['DB_NAME'],
            user=app.config['DB_USER'],
            password=app.config['DB_PASSWORD'],
            db='db',
            autocommit=True,
            charset='utf8mb4',
            cursorclass=pymysql.cursors.DictCursor)
        flask.g.pymysql_db = connection

    yield app.test_client()
    # Teardown logic (happens after each test function)
    flask.g.tx.rollback()
    flask.g.db.close()
