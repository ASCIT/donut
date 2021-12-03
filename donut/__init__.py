import flask
from flask_bootstrap import Bootstrap
import pymysql.cursors
import http
import datetime
import logging

try:
    from donut import config
except ImportError:
    from donut import default_config as config
from donut import constants
from donut.modules import account, auth, marketplace, calendar, core, courses, directory_search, editor, feedback, groups, newsgroups, rooms, uploads, voting, flights
from donut.donut_SMTP_handler import DonutSMTPHandler
from donut.email_utils import DOMAIN

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
app.register_blueprint(newsgroups.blueprint)
app.register_blueprint(flights.blueprint)


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
    app.config["MAKE_REQUEST_DB"] = environment_name != "test"
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
    app.jinja_env.trim_blocks = True
    app.jinja_env.lstrip_blocks = True

    if environment_name == "prod":
        mail_handler = DonutSMTPHandler(
            mailhost='localhost',
            fromaddr='server-error@' + DOMAIN,
            toaddrs=[],
            subject='Donut Server Error',
            db_instance=make_db())
        mail_handler.setLevel(logging.ERROR)
        mail_handler.setFormatter(
            logging.Formatter(
                '[%(asctime)s] %(levelname)s in %(module)s: %(message)s'))
        app.logger.addHandler(mail_handler)


# Create database engine object.
@app.before_request
def before_request():
    """Logic executed before request is processed."""
    flask.request.start = datetime.datetime.now()
    # When running in a test, the database connection will be created by the test fixture
    if app.config['MAKE_REQUEST_DB']:
        db = make_db()
        if db:
            flask.g.pymysql_db = db


def make_db():
    database = app.config.get('DB_NAME')
    user = app.config.get('DB_USER')
    password = app.config.get('DB_PASSWORD')
    if database is None or user is None or password is None:
        return None

    return pymysql.connect(
        host='localhost',
        database=database,
        user=user,
        password=password,
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
    source = f' from {flask.request.remote_addr}'
    user = flask.session.get('username')
    user = ' by ' + user if user else ''
    app.logger.info(f'{method} {path}{args}{user}{source} in {duration} ms')
    return response


@app.teardown_request
def teardown_request(exception):
    """Logic executed after every request is finished."""
    # When running in a test, the database connection will be closed by the test fixture
    if app.config['MAKE_REQUEST_DB']:
        db = getattr(flask.g, 'pymysql_db', None)
        if db:
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


@app.errorhandler(http.client.REQUEST_ENTITY_TOO_LARGE)
def upload_too_large(error):
    """ Handles a 413 Payload Too Large error. """
    max_size = constants.MAX_CONTENT_LENGTH_STRING
    return flask.render_template("413.html", max_size=max_size), \
        http.client.REQUEST_ENTITY_TOO_LARGE


@app.errorhandler(http.client.INTERNAL_SERVER_ERROR)
def internal_server_error(error):
    """
  Handles a 500 internal server error response.
  """
    return flask.render_template("500.html"), http.client.INTERNAL_SERVER_ERROR


# After initialization, import the routes.
from donut import routes
