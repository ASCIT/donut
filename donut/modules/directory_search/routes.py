import flask
import json
from flask import jsonify

from donut.modules.directory_search import blueprint, helpers


@blueprint.route("/directory")
def directory_search():
    return flask.render_template("directory_search.html")


@blueprint.route('/1/users/<int:user_id>')
def view_user(user_id):
    return flask.render_template(
        'view_user.html', user=helpers.get_user(user_id))


@blueprint.route('/1/users/search/<name_query>')
def search_by_name(name_query):
    return jsonify(helpers.get_users_by_name_query(name_query))
