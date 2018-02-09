import flask
import json
from flask import jsonify

from donut.modules.directory_search import blueprint, helpers

@blueprint.route("/directory")
def directory_search():
    return flask.render_template("directory_search.html")

