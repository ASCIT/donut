import flask
from flask_bootstrap import Bootstrap
import sqlalchemy
import pymysql.cursors
import os
import pdb
import traceback
import http
import datetime

try:
    from donut import config
except ImportError:
    from donut import default_config as config
from donut import constants
from donut.modules import account
from donut.modules import auth
from donut.modules import marketplace
from donut.modules import core
from donut.modules import groups

app = flask.Flask(__name__)
Bootstrap(app)  # enable Bootstrap in Flask

# Load blueprint modules
app.register_blueprint(account.blueprint)
app.register_blueprint(auth.blueprint)
app.register_blueprint(marketplace.blueprint)
app.register_blueprint(core.blueprint)
app.register_blueprint(groups.blueprint)


def init(environment_name):
    """Initializes the application with configuration variables and routes.

  This function MUST be called before the server can be run.

  Args:
    environment_name: this must be either "prod", "dev", or "test".

  Returns:
    None
  """
    if environment_name == "prod" and hasattr(config, "PROD"):
        environment = config.PROD
    elif environment_name == "dev" and hasattr(config, "DEV"):
        environment = config.DEV
    elif environment_name == "test" and hasattr(config, "TEST"):
        environment = config.TEST
    else:
        raise ValueError("Illegal environment name.")
    # Initialize configuration variables.
    app.config["DB_URI"] = environment.db_uri
    app.config["DEBUG"] = environment.debug
    app.config["SECRET_KEY"] = environment.secret_key
    app.config["DB_USER"] = environment.db_user
    app.config["DB_PASSWORD"] = environment.db_password
    app.config["DB_NAME"] = environment.db_name

    # Maximum file upload size, in bytes.
    app.config["MAX_CONTENT_LENGTH"] = constants.MAX_CONTENT_LENGTH

    # Update jinja global functions
    app.jinja_env.globals.update(
        current_year=lambda: datetime.datetime.now().year)


# Create database engine object.
@app.before_request
def before_request():
    if 'DB_URI' in app.config:
        engine = sqlalchemy.create_engine(
            app.config['DB_URI'], convert_unicode=True)
        flask.g.db = engine.connect()
    """Logic executed before request is processed."""
    if ('DB_NAME' in app.config and 'DB_USER' in app.config
            and 'DB_PASSWORD' in app.config):
        connection = pymysql.connect(
            host='localhost',
            database=app.config['DB_NAME'],
            user=app.config['DB_USER'],
            password=app.config['DB_PASSWORD'],
            db='db',
            charset='utf8mb4',
            cursorclass=pymysql.cursors.DictCursor)
        flask.g.pymysql_db = connection


@app.teardown_request
def teardown_request(exception):
    """Logic executed after every request is finished."""
    db = getattr(flask.g, 'db', None)
    if db is not None:
        db.close()


# Error handlers
@app.errorhandler(http.client.NOT_FOUND)
def page_not_found(error):
    """ Handles a 404 page not found error. """
    return flask.render_template("404.html"), http.client.NOT_FOUND


@app.errorhandler(http.client.FORBIDDEN)
def access_forbidden(error):
    """ Handles a 403 access forbidden error. """
    return flask.render_template("403.html"), http.client.FORBIDDEN


@app.errorhandler(http.client.INTERNAL_SERVER_ERROR)
def internal_server_error(error):
    """
  Handles a 500 internal server error response.
  """
    return flask.render_template("500.html"), http.client.INTERNAL_SERVER_ERROR


# After initialization, import the routes.
from donut import routes
