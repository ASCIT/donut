from flask import render_template

from Donut import app

@app.route('/')
def home():
  """An example route that does nothing."""
  return render_template('index.html')

