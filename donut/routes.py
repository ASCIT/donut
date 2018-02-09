import flask
from flask import jsonify
from donut import app
from donut.auth_utils import get_user_id
from donut.modules.core import helpers
from donut.modules import groups

@app.route('/')
def home():
    return flask.render_template('donut.html')


@app.route('/contact')
def contact():
    return flask.render_template('contact.html')

@app.route('/campus_positions')
def campus_positions():
    user_id = get_user_id(flask.session['username'])
    result = helpers.get_group_list_of_member(user_id) 
    approved_group_ids = []
    approved_group_names = []
    for res in result:
        if res["control"] == 1:
            approved_group_ids.append(res["group_id"])
            approved_group_names.append(res["group_name"])
    all_positions = groups.helpers.get_position_data();
    for pos in all_positions:
        pos['start_date'] = str(pos['start_date'])    
        pos['end_date'] = str(pos['end_date'])
    if 'username' in flask.session:
        return flask.render_template('campus_positions.html',
            approved_group_ids=approved_group_ids, 
            approved_group_names=approved_group_names,
            all_positions=all_positions)
    else:
        return flask.render_template('campus_positions.html',
            all_positions=all_positions)
