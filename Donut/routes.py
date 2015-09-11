import flask

from Donut import app

@app.route('/')
def home():
  return flask.render_template('donut.html')

@app.route('/contact')
def contact():
    return flask.render_template('contact.html')
