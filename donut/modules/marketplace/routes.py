import flask

from donut.modules.marketplace import blueprint, helpers

@blueprint.route('/marketplace')
def login():
  """Display login page."""
  return flask.render_template('marketplace.html')



