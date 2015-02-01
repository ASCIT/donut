from flask import Flask, g
from sqlalchemy import create_engine

from Donut import config, constants
from Donut.modules import example

app = Flask(__name__)
app.debug = False
app.secret_key = config.SECRET_KEY

# Maximum file upload size, in bytes.
app.config['MAX_CONTENT_LENGTH'] = constants.MAX_CONTENT_LENGTH

# Load blueprint modules
app.register_blueprint(example.blueprint, url_prefix='/example')

# Create database engine object.
# TODO: Fix after set up database.
# engine = create_engine(config.DB_URI, convert_unicode=True)

@app.before_request
def before_request():
  """Logic executed before request is processed."""
  # g.db = engine.connect()

@app.teardown_request
def teardown_request(exception):
  """Logic executed after every request is finished."""
  # if g.db != None:
  #  g.db.close()

# After initialization, import the routes.
from Donut import routes
