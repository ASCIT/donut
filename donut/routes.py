import flask
from donut import app


@app.route('/')
def home():
    return flask.render_template('donut.html')


@app.route('/contact')
def contact():
    return flask.render_template('contact.html')


@app.route('/arcfeedback')
def arcfeedback():
    return flask.render_template('arcfeedback.html')
