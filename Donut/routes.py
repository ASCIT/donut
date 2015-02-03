import flask

from Donut import app

@app.route('/')
def home():
  """An example route that does nothing."""
  return flask.render_template('index.html')

