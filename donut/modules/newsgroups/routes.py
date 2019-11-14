import flask 
from flask import jsonify
from donut.modules.groups import helpers as groups
from donut import auth_utils

from . import blueprint, helpers

@blueprint.route('/newsgroups')
def newsgroups_home():
    return flask.render_template(
            'newsgroups.html',
            groups=helpers.get_newsgroups())

@blueprint.route('/newsgroups/post')
@blueprint.route('/newsgroups/post/<group_id>')
def post(group_id=None):
    user_id = auth_utils.get_user_id(flask.session['username'])
    return flask.render_template(
            'post.html',
            groups=helpers.get_can_send_groups(user_id),
            group_selected=group_id)

@blueprint.route('/newsgroups/postmessage', methods=['POST'])
def post_message():
    user_id = auth_utils.get_user_id(flask.session['username'])
    fields = ['group', 'subject', 'msg']
    data = {}
    for field in fields:
        data[field] = flask.request.form.get(field)
    data['group_name'] = groups.get_group_data(data['group'], ['group_name'])['group_name']
    if helpers.send_email(data):
        flask.flash('Email sent')
        helpers.insert_email(user_id, data)
    else:
        flask.flash('Email failed to send')
    return flask.redirect(flask.url_for('newsgroups.post'))

@blueprint.route('/newsgroups/viewgroup/<group_id>')
def view_group(group_id):
    user_id = auth_utils.get_user_id(flask.session['username'])
    pos_actions = helpers.get_user_actions(user_id, group_id)
    fields = ['group_id', 'group_name', 'group_desc', 'anyone_can_send',
            'members_can_send', 'visible', 'admin_control_members']
    group_info = groups.get_group_data(group_id, fields)
    
    return flask.render_template(
            'group.html',
            group=group_info,
            member=groups.is_user_in_group(user_id, group_id),
            actions=pos_actions,
            messages=helpers.get_past_messages(group_id),
            owners=['TODO'])

@blueprint.route('/newsgroups/viewgroup/apply/<group_id>', methods=['POST'])
def apply_subscription(group_id):
    helpers.apply_subscription(flask.session['username'], group_id)
    flask.flash('Successfully applied for subscription')
    return flask.redirect(flask.url_for('newsgroups.view_group', group_id=group_id))

@blueprint.route('/newsgroups/viewgroup/unsub/<group_id>', methods=['POST'])
def unsubscribe(group_id):
    helpers.unsubscribe(flask.session['username'], group_id)
    flask.flash('Successfully unsubscribed')
    return flask.redirect(flask.url_for('newsgroups.view_group', group_id=group_id))

@blueprint.route('/newsgroups/mygroups')
def mygroups():
    user_id = auth_utils.get_user_id(flask.session['username'])
    return flask.render_template(
            'newsgroups.html',
            groups=helpers.get_my_newsgroups(user_id))
