import flask
import json
from flask import jsonify

from donut.modules.directory_search import blueprint, helpers

@blueprint.route("/directory_search")
def directory_search():
    print "hi"
