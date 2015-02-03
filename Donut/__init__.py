import flask
import sqlalchemy

from Donut import config, constants
from Donut.modules import example

app = flask.Flask(__name__)
app.debug = False
app.secret_key = config.SECRET_KEY

# Maximum file upload size, in bytes.
app.config['MAX_CONTENT_LENGTH'] = constants.MAX_CONTENT_LENGTH

# Load blueprint modules
app.register_blueprint(example.blueprint, url_prefix='/example')

# Create database engine object.
# TODO##DatabaseWork: We currently don't have a database set up, so we can't
# reference sqlalchemy yet. However, it serves as a good example implementation.
# engine = sqlalchemy.create_engine(config.DB_URI, convert_unicode=True)

@app.before_request
def before_request():
  """Logic executed before request is processed."""
  # TODO#DatabaseWork uncomment this line
  # flask.g.db = engine.connect()

@app.teardown_request
def teardown_request(exception):
  """Logic executed after every request is finished."""
  # TODO#DatabaseWork uncomment these lines
  # if flask.g.db != None:
  #  flask.g.db.close()

# After initialization, import the routes.
from Donut import routes
