from datetime import datetime, timedelta
import flask

from . import blueprint, helpers
from donut.validation_utils import (validate_date, validate_exists,
                                    validate_in, validate_int)

AM_OR_PM = set(["A", "P"])
H_MM = "%-I:%M %p"
YYYY_MM_DD = "%Y-%m-%d"


@blueprint.route("/newsgroups")
def rooms_home():
    """
        GET /reserve
        Displays room reservation homepage
    """

    return flask.render_template("post.html")


@blueprint.route("/1/send/", methods=["POST"])
def send():
    """POST /1/send/"""

    helpers.send(room, flask.session["username"], reason, start, end)
    return flask.render_template("reservation_success.html")


@blueprint.route("/my-reservations")
def my_reservations():
    """GET /my-reservations"""

    reservations = helpers.get_my_reservations(
        flask.session["username"]) if "username" in flask.session else None

    return flask.render_template("mine-iframe.html", reservations=reservations)


@blueprint.route("/all-reservations")
def all_reservations():
    """GET /all-reservations"""

    now = datetime.now()
    next_week = now + timedelta(days=7)

    args = flask.request.args
    rooms = args.getlist("rooms")
    validations = [
        all(map(validate_int, rooms)), "start" not in args
        or validate_date(args["start"]), "end" not in args
        or validate_date(args["end"])
    ]
    if all(validations):
        start = datetime.strptime(
            args.get("start", now.strftime(YYYY_MM_DD)), YYYY_MM_DD).date()
        end = datetime.strptime(
            args.get("end", next_week.strftime(YYYY_MM_DD)),
            YYYY_MM_DD).date()
        reservations = helpers.get_all_reservations(
            list(map(int, rooms)), start, end)
    else:
        reservations = helpers.get_all_reservations([], now, next_week)
    return flask.render_template(
        "all-iframe.html",
        rooms=helpers.get_rooms(),
        start=start,
        end=end,
        reservations=reservations)


@blueprint.route("/1/reservation/<int:id>", methods=["GET"])
def view_groups(id):
    """GET /1/groups/1"""

    return flask.render_template(
        "groups-view.html",
        reservation=helpers.get_reservation(id),
        now=datetime.now())
