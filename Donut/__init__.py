import flask
import sqlalchemy
import os
import pdb
import traceback
import httplib
import datetime

from Donut import constants
from Donut.modules import scheduler 

app = flask.Flask(__name__)
app.debug = False

# Get app config, if we're not testing on travis.
if 'TRAVIS' not in os.environ:
  app.config.from_object('Donut.config')

# Maximum file upload size, in bytes.
app.config['MAX_CONTENT_LENGTH'] = constants.MAX_CONTENT_LENGTH
app.secret_key = app.config['SECRET_KEY']

# Load blueprint modules

app.register_blueprint(scheduler.blueprint, url_prefix='/scheduler')

# Create database engine object.
# TODO ##DatabaseWork: We currently don't have a database set up, so we can't
# reference sqlalchemy yet. However, it serves as a good example implementation.
# engine = sqlalchemy.create_engine(app.config['DB_URI'], convert_unicode=True)

@app.before_request
def before_request():
  """Logic executed before request is processed."""
  if 'DB_URI' in app.config:
    engine = sqlalchemy.create_engine(app.config['DB_URI'], convert_unicode=True)
    flask.g.db = engine.connect()

@app.teardown_request
def teardown_request(exception):
  """Logic executed after every request is finished."""
  db = getattr(flask.g, 'db', None)
  if db is not None:
   db.close()

# Error handlers
@app.errorhandler(httplib.NOT_FOUND)
def page_not_found(error):
  """ Handles a 404 page not found error. """
  return flask.render_template("404.html"), httplib.NOT_FOUND

@app.errorhandler(httplib.FORBIDDEN)
def access_forbidden(error):
  """ Handles a 403 access forbidden error. """
  return flask.render_template("403.html"), httplib.FORBIDDEN

@app.errorhandler(httplib.INTERNAL_SERVER_ERROR)
def internal_server_error(error):
  """
  Handles a 500 internal server error response. 
  """
  return flask.render_template("500.html"), httplib.INTERNAL_SERVER_ERROR

# After initialization, import the routes.
from Donut import routes
