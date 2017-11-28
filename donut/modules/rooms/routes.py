from datetime import datetime
import flask

from . import blueprint, helpers
from donut.validation_utils import (validate_date, validate_exists, validate_in, validate_int)

AM_OR_PM = set(["A", "P"])

@blueprint.route("/reserve")
def rooms_home():
    """Displays room reservation homepage"""

    return flask.render_template("reservations.html", rooms=helpers.get_rooms())

@blueprint.route("/1/book-room/", methods=["POST"])
def book():
    """POST /1/book-room/"""

    form = flask.request.form
    validations = [
        validate_exists(form, "room") and validate_int(form["room"]) and helpers.is_room(form["room"]),
        validate_exists(form, "date") and validate_date(form["date"]),
        validate_exists(form, "start_hour") and validate_int(form["start_hour"], 1, 12),
        validate_exists(form, "start_minute") and validate_int(form["start_minute"], 0, 59),
        validate_exists(form, "start_period") and validate_in(form["start_period"], AM_OR_PM),
        validate_exists(form, "end_hour") and validate_int(form["end_hour"], 1, 12),
        validate_exists(form, "end_minute") and validate_int(form["end_minute"], 0, 59),
        validate_exists(form, "end_period") and validate_in(form["end_period"], AM_OR_PM),
        validate_exists(form, "reason")
    ]

    if not all(validations):
        # TODO: Should include old parameters in form here
        return flask.render_template("reservations.html", rooms=helpers.get_rooms())

    start_hour = int(form["start_hour"]) % 12
    if form["start_period"] == "P":
        start_hour += 12
    start_minute = int(form["start_minute"])
    end_hour = int(form["end_hour"]) % 12
    if form["end_period"] == "P":
        end_hour += 12
    end_minute = int(form["end_minute"])
    if start_hour > end_hour or (start_hour == end_hour and start_minute >= end_minute):
        flask.flash("Start time must be before end time")
        # TODO: Should include old parameters in form here
        return flask.render_template("reservations.html", rooms=helpers.get_rooms())

    room = int(form["room"])
    day = datetime.strptime(form["date"], '%Y-%m-%d')
    start = datetime(day.year, day.month, day.day, start_hour, start_minute)
    end = datetime(day.year, day.month, day.day, end_hour, end_minute)
    reason = form["reason"] or None

    helpers.add_reservation(room, flask.session["username"], reason, start, end)

    return flask.render_template("reservation_success.html")
