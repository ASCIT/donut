import flask
import json
import os
import re

from donut.modules.editor import blueprint, helpers
from flask import current_app, redirect, url_for
from donut.resources import Permissions
from donut.auth_utils import check_permission


@blueprint.route('/editor', methods=['GET', 'POST'])
def editor():
    '''
    Returns the editor page where users can create and edit
    existing pages
    '''
    input_text = "Hello world"
    title = "TITLE"
    inputt = flask.request.args.get('input_text')

    if inputt != None:
        input_text = helpers.read_markdown(inputt)
        title = flask.request.args.get('title')

    if check_permission(Permissions.ADMIN) and 'username' in flask.session:
        return flask.render_template(
            'editor_page.html', input_text=input_text, title=title)
    else:
        return flask.abort(403)


@blueprint.route('/_change_title', methods=['POST'])
def change_title():
    '''
    Allows one to change a file/page title.
    '''
    title = flask.request.form['title']
    old_title = flask.request.form['old_title']
    input_text = flask.request.form['input_text']
    title_res = re.match("^[0-9a-zA-Z.\/_\- ]*$", title)
    if title_res != None and check_permission(Permissions.ADMIN) and 'username' in flask.session:
        helpers.rename_title(old_title, title)
        return flask.render_template('editor_page.html', input_text=input_text, title=title)
    return flask.abort(403)

@blueprint.route('/pages/_save', methods=['POST'])
def save():
    '''
    Actually saves the data from the forms as markdown
    '''
    markdown = flask.request.form['markdown']
    title = flask.request.form['title']
    title_res = re.match("^[0-9a-zA-Z.\/_\- ]*$", title)
    if title_res != None and len(title) <= 30 and check_permission(
            Permissions.ADMIN) and 'username' in flask.session:
        helpers.write_markdown(markdown, title)
        return flask.jsonify({'url': url_for('uploads.display', url=title)})

    else:
        flask.abort(403)


@blueprint.route('/pages/_check_override', methods=['POST'])
def check_duplicate():
    title = flask.request.form['title']
    return flask.jsonify({'error': helpers.check_duplicate(title)})


@blueprint.route('/created_list')
def created_list():
    '''
    Returns a list of all created pages
    '''

    filename = flask.request.args.get('filename')
    if filename != None and check_permission(
            Permissions.ADMIN) and 'username' in flask.session:
        helpers.remove_link(filename)

    links = helpers.get_links()

    return flask.render_template(
        'created_list.html',
        links=links,
        permissions=check_permission(Permissions.ADMIN))
