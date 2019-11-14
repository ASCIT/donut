import flask 
from flask import jsonify

from . import blueprint, helpers

@blueprint.route('/newsgroups')
def newsgroups_home():
    """
        GET /newsgroups
        Displays newsgroups homepage
    """

    return flask.render_template('newsgroups.html')

@blueprint.route('/newsgroups/view')
def view():
    return flask.render_template(
            'view-iframe.html',
            groups=helpers.get_newsgroups())

@blueprint.route('/newsgroups/post')
def post():
    username = flask.session['username'] if 'username' in flask.session else None
    return flask.render_template(
            'post-iframe.html',
            group_selected=False,
            groups=helpers.get_can_send_groups(username))

@blueprint.route('/newsgroups/postmessage', methods=['POST'])
def post_message():
    fields = ['group', 'subject', 'msg']
    data = {}
    for field in fields:
        data[field] = flask.request.form.get(field)
    # TODO: send email
    return flask.redirect(url_for('newsgroups.post'))


@blueprint.route('/newsgroups/viewgroup/<group_id>')
def view_group(group_id):
    group_info = helpers.get_newsgroup_info(group_id)
    username = flask.session['username'] if 'username' in flask.session else None
    pos_actions = helpers.get_user_actions(username, group_id)
    pos_held = helpers.positions_held(username, group_id)
    return flask.render_template(
            'group-iframe.html',
            name=group_info['group_name'],
            desc=group_info['group_desc'],
            group_id=group_id,
            member=(pos_held !=  ()),
            actions=pos_actions,
            recent_messages=helpers.get_past_messages(group_id),
            owners=['TODO'])

@blueprint.route('/newsgroups/viewgroup/apply/<group_id>', methods=['POST'])
def apply_subscription(group_id):
    helpers.apply_subscription(flask.session['username'], group_id)
    # TODO: fix flashes in home page
    flask.flash('Successfully applied for subscription')
    return flask.redirect(flask.url_for('newsgroups.view_group', group_id=group_id))

@blueprint.route('/newsgroups/mygroups')
def mygroups():
    username = flask.session['username'] if 'username' in flask.session else None
    return flask.render_template(
            'view-iframe.html',
            groups=helpers.get_my_newsgroups(username))
