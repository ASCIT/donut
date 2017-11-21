import flask
from donut import app


@app.route('/')
def home():
    return flask.render_template('donut.html')


@app.route('/contact')
def contact():
    return flask.render_template('contact.html')

@app.route('/campus_positions')
def campus_positions():
    return flask.render_template('campus_positions.html')
