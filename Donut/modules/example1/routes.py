import flask

from Donut.modules.example1 import blueprint

@blueprint.route('/')
def home1():
  """Loads an example page."""
  return flask.render_template('donut.html')
