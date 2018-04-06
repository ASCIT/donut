import flask
import json
import os

from donut.modules.editor import blueprint, helpers
from flask import current_app, redirect, url_for


@blueprint.route('/editor', methods=['GET', 'POST'])
def editor(input_text='Hello World!!!', title="TITLE", div_id='empty'):
    #markdown = flask.request.form['markdown']
    #title = flask.request.form['title']
    #if title == '':
    #    title = 'SAMPLE_TITLE'
    #    markdown = 'Hello World!'
    #if input_text == title:
    #    input_text = read_markdown(input_text, div_id)
    return flask.render_template(
        'editor_page.html', input_text=input_text, title=title)


@blueprint.route('/redirecting')
def redirecting(title='uploads.aaa'):
    return flask.render_template('redirecting.html', input_text=url_for(title))


@blueprint.route('/_save', methods=['GET', 'POST'])
def save():
    markdown = flask.request.form['markdown']
    title = flask.request.form['title']

    if (helpers.write_markdown(markdown, title) == 0):
        return redirect(url_for('uploads.display', url=title))
    else:
        return redirect(
            url_for(
                'editor.editor',
                input_text=helpers.read_markdown(title, 0),
                title=title))
