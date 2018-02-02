import flask
from donut import app


@app.route('/')
def home():
    return flask.render_template('donut.html')


@app.route('/contact')
def contact():
    return flask.render_template('contact.html')

@app.route('/directory')
def directory_search():
    return flask.render_template('directory_search.html')

