import flask

from donut.modules.marketplace import blueprint, helpers

@blueprint.route('/marketplace')
def marketplace():
  """Display marketplace page."""
  return flask.render_template('marketplace.html')



