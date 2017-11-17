import flask

from donut.modules.rooms import blueprint, helpers


@blueprint.route("/reserve")
def rooms_home():
    """Displays room reservation homepage"""

    return flask.render_template("reservations.html")
