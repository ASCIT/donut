import flask

from Donut.modules.scheduler import blueprint

@blueprint.route('/')
def home():
  """Loads an example page."""
  return flask.render_template('scheduler.html')
