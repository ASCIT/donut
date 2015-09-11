import flask

from Donut.modules.example import blueprint

@blueprint.route('/')
def home():
  """Loads an example page."""
  return flask.render_template('example_index.html')
