from flask import render_template

from Donut.modules.example import blueprint

@blueprint.route('/')
def home():
  """Loads an example page."""
  return render_template('example_index.html')
