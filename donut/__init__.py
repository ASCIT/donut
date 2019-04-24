import flask
from flask_bootstrap import Bootstrap
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
from donut.modules import account, auth, marketplace, calendar, core, courses, directory_search, editor, feedback, groups, rooms, uploads, voting

app = flask.Flask(__name__)
Bootstrap(app)  # enable Bootstrap in Flask

# Load blueprint modules
app.register_blueprint(account.blueprint)
app.register_blueprint(auth.blueprint)
app.register_blueprint(marketplace.blueprint)
app.register_blueprint(calendar.blueprint)
app.register_blueprint(core.blueprint)
app.register_blueprint(courses.blueprint)
app.register_blueprint(directory_search.blueprint)
app.register_blueprint(groups.blueprint)
app.register_blueprint(feedback.blueprint)
app.register_blueprint(editor.blueprint)
app.register_blueprint(rooms.blueprint)
app.register_blueprint(uploads.blueprint)
app.register_blueprint(voting.blueprint)


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
    app.config["ENV"] = "production" if environment_name == "prod" \
        else "development"
    # Initialize configuration variables.
    app.config["DB_URI"] = environment.db_uri
    app.config["DEBUG"] = environment.debug
    app.config["SECRET_KEY"] = environment.secret_key
    app.config["RESTRICTED_IPS"] = environment.restricted_ips
    app.config["DB_USER"] = environment.db_user
    app.config["DB_PASSWORD"] = environment.db_password
    app.config["DB_NAME"] = environment.db_name
    app.config["IMGUR_API"] = environment.imgur_api
    app.config["UPLOAD_WEBPAGES"] = 'modules/uploads/uploaded_files/pages'
    app.config["UPLOAD_FOLDER"] = 'modules/uploads/uploaded_files'
    # Maximum file upload size, in bytes.
    app.config["MAX_CONTENT_LENGTH"] = constants.MAX_CONTENT_LENGTH

    # Update jinja global functions
    app.jinja_env.globals.update(
        current_year=lambda: datetime.datetime.now().year)


# Create database engine object.
@app.before_request
def before_request():
    flask.request.start = datetime.datetime.now()
    """Logic executed before request is processed."""
    if ('DB_NAME' in app.config and 'DB_USER' in app.config
            and 'DB_PASSWORD' in app.config):
        flask.g.pymysql_db = pymysql.connect(
            host='localhost',
            database=app.config['DB_NAME'],
            user=app.config['DB_USER'],
            password=app.config['DB_PASSWORD'],
            db='db',
            autocommit=True,
            charset='utf8mb4',
            cursorclass=pymysql.cursors.DictCursor)


@app.after_request
def log_request(response):
    duration = datetime.datetime.now() - flask.request.start
    duration = round(duration / datetime.timedelta(milliseconds=1))
    method = flask.request.method
    path = flask.request.path
    args = dict(flask.request.args.items())
    args = f' {args}' if args else ''
    source = flask.request.remote_addr
    user = flask.session.get('username')
    user = ' by ' + user if user else ''
    app.logger.info(f'{method} {path}{args}{user} in {duration} ms')
    return response


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
