from flask import Blueprint
blueprint = Blueprint('example1', __name__, template_folder='templates')

import Donut.modules.example1.routes
