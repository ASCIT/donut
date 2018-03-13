import flask
import json
import os

from donut.modules.editor import blueprint, helpers
from flask import current_app, redirect, url_for


@blueprint.route('/editor')
def editor(input_text='Hello World!!!'):
    return flask.render_template('editor_page.html', input_text=input_text)


@blueprint.route('/redirecting')
def redirecting(title='uploads.aaa'):
    return flask.render_template('redirecting.html', input_text=url_for(title))


@blueprint.route('/_save', methods=['POST'])
def save():
    if flask.request.method == 'POST':
        html = flask.request.form['html']
        title = flask.request.form['html']
    root = current_app.config["UPLOAD_FOLDER"]
    root += "/templates"

    title = title.replace('</p>', '')
    title = title.replace('<p>', '')
    path = os.path.join(root, title + ".html")
    f = open(path, "w+")
    f.write(html)
    f.close()

    f = open(current_app.config["UPLOAD_FOLDER"] + "/routes.py", "a")
    f.write("@blueprint.route('/" + title + "')\n")
    f.write("def " + title + "():\n")
    f.write("\treturn flask.render_template('" + title + ".html')\n\n")
    f.close()
    return redirect(url_for('editor.redirecting', title=title))
