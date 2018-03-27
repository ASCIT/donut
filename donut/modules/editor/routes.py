import flask
import json
import os

from donut.modules.editor import blueprint, helpers
from flask import current_app, redirect, url_for


@blueprint.route('/editor')
def editor(input_text='Hello World!!!', title="TITLE", div_id='empty'):
    if input_text == title:
        input_text = read_markdown(input_text, div_id)
    return flask.render_template(
        'editor_page.html', input_text=input_text, title=title)


'''
def read_markdown(name):
    underCommittee = ['BoC', 'ascit_bylaws', 'BoC.bylaws', 'BoC.defendants',
    'BoC.FAQ', 'BoC.reporters', 'BoC.witnesses', 'CRC', 'honor_system_handbook']
    if name in underCommittee:
        with open(new_root + '/template_page') as f:
                template_html += f.read()
            f.close()
'''


@blueprint.route('/redirecting')
def redirecting(title='uploads.aaa'):
    return flask.render_template('redirecting.html', input_text=url_for(title))


@blueprint.route('/_save', methods=['POST'])
def save():
    markdown = flask.request.form['markdown']
    title = flask.request.form['title']

    helpers.write_markdown(markdown, title)

    return redirect(url_for('editor.editor'))
