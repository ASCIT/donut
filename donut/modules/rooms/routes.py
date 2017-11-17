import flask

from . import blueprint, helpers


@blueprint.route("/reserve")
def rooms_home():
    """Displays room reservation homepage"""

    return flask.render_template("reservations.html", rooms=helpers.get_rooms())

@blueprint.route("/1/book-room/", methods=["POST"])
def book():
    """POST /1/book-room/"""

    return flask.render_template("reservations.html", rooms=helpers.get_rooms())
