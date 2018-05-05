import flask
import json
import os

from donut.modules.editor import blueprint, helpers
from flask import current_app, redirect, url_for

@blueprint.route('/editor', methods=['GET', 'POST'])
def editor(input_text='Hello World!!!', title="TITLE"):
    input = flask.request.args.get('input_text')
    print(input)
    if input != None:
        input_text = helpers.read_markdown(input)
        title = flask.request.args.get('title')
    return flask.render_template(
        'editor_page.html', input_text=input_text, title=title)


@blueprint.route('/redirecting')
def redirecting(title='uploads.aaa'):
    return flask.render_template('redirecting.html', input_text=url_for(title))


@blueprint.route('/_save', methods=['POST'])
def save():
    markdown = flask.request.form['markdown']
    title = flask.request.form['title']

    if (helpers.write_markdown(markdown, title) == 0):
        return flask.jsonify({'url' : url_for('uploads.display', url=title)})
    else:
        return flask.jsonify({'url' : url_for( 'uploads.display', url = title)})

@blueprint.route('/created_list')
def created_list():
    root = os.path.join(current_app.root_path, current_app.config["UPLOAD_FOLDER"])
    links = glob.glob(root+'/*')
    for i in range(len(links)):
        links[i] = (flask.url_for('uploads.display', url=links[i][22:]), links[i][22:])
    return flask.render_template('uploaded_list.html', links=links)
