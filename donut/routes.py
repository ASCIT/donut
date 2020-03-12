import flask
from flask import jsonify
from donut import app
from donut.auth_utils import get_user_id, is_admin
from donut.constants import CONTACTS
from donut.modules.core import helpers
from donut.modules import groups


@app.route('/')
def home():
    news = helpers.get_news()
    return flask.render_template('donut.html', news=news, is_admin=is_admin())


@app.route('/contact')
def contact():
    return flask.render_template('contact.html', contacts=CONTACTS)


@app.route('/campus_positions')
def campus_positions():
    '''Renders the campus positions template. We collect a list of
    groups that the currently loged in user is the admin of. We
    also collect the total list of positions and pass it in'''
    approved_group_ids = []
    approved_group_names = []
    username = flask.session.get('username')
    if username:
        user_id = get_user_id(username)
        for group in helpers.get_group_list_of_member(user_id):
            if group["control"]:
                approved_group_ids.append(group["group_id"])
                approved_group_names.append(group["group_name"])
    all_positions = groups.helpers.get_position_data(
        include_house_and_ug=False, order_by=("group_name", "pos_name"))
    return flask.render_template(
        'campus_positions.html',
        approved_group_ids=approved_group_ids,
        approved_group_names=approved_group_names,
        all_positions=all_positions)


@app.route('/news', methods=('POST', ))
def add_news():
    if not is_admin():
        flask.abort(403)

    news = flask.request.form.get('news')
    if news:
        helpers.add_news(news)
    return flask.redirect(flask.url_for('.home'))


@app.route('/news/<int:news_id>/delete', methods=('POST', ))
def delete_news(news_id):
    if not is_admin():
        flask.abort(403)

    helpers.delete_news(news_id)
    return flask.redirect(flask.url_for('.home'))
