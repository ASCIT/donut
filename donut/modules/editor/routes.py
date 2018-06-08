import flask
import json
import os

import glob
from donut.modules.editor import blueprint, helpers
from flask import current_app, redirect, url_for
from donut.resources import Permissions
from donut.auth_utils import check_permission


@blueprint.route('/editor', methods=['GET', 'POST'])
def editor(input_text='Hello World!!!', title="TITLE"):
    '''
    Returns the editor page where users can create and edit
    existing pages
    '''
    input = flask.request.args.get('input_text')

    if input != None:
        input_text = helpers.read_markdown(input)
        title = flask.request.args.get('title')

    return flask.render_template(
        'editor_page.html', input_text=input_text, title=title)


@blueprint.route('/_change_title', methods=['POST'])
def change_title():
    '''
    Actually saves the data from the forms as markdown
    '''
    title = flask.request.form['title']


@blueprint.route('/_save', methods=['POST'])
def save():
    '''
    Actually saves the data from the forms as markdown
    '''
    markdown = flask.request.form['markdown']
    title = flask.request.form['title']
    if title == 'BoC':
        return flask.jsonify({'url': url_for('committee_sites.boc')})
    elif title == 'ASCIT_Bylaws':
        return flask.jsonify({'url': url_for('committee_sites.ascit_bylaws')})
    elif title == 'BoC_Bylaws':
        return flask.jsonify({'url': url_for('committee_sites.bylaws')})
    elif title == 'BoC_Defendants':
        return flask.jsonify({'url': url_for('committee_sites.defendants')})
    elif title == 'BoC_FAQ':
        return flask.jsonify({'url': url_for('committee_sites.FAQ')})
    elif title == 'BoC_Reporters':
        return flask.jsonify({'url': url_for('committee_sites.reporters')})
    elif title == 'BoC_Witness':
        return flask.jsonify({'url': url_for('committee_sites.winesses')})
    elif title == 'CRC':
        return flask.jsonify({'url': url_for('committee_sites.CRC')})
    if (helpers.write_markdown(markdown, title) == 0):
        return flask.jsonify({'url': url_for('uploads.display', url=title)})
    else:
        return flask.jsonify({'url': url_for('uploads.display', url=title)})


@blueprint.route('/created_list')
def created_list(filename='default'):
    '''
    Returns a list of all created pages
    '''
    filename = flask.request.form.get('filename')
    if filename != None:
        helper.remove_link(filename)

    links = helpers.get_links()

    return flask.render_template('created_list.html', links=links)
