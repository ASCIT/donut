from datetime import datetime, timedelta
import flask

from . import blueprint, helpers
from donut.validation_utils import (validate_date, validate_exists,
                                    validate_in, validate_int)

AM_OR_PM = set(["A", "P"])
H_MM = "%-I:%M %p"
YYYY_MM_DD = "%Y-%m-%d"


@blueprint.route("/reserve")
def rooms_home():
    """Displays room reservation homepage"""

    return flask.render_template(
        "reservations.html",
        rooms=helpers.get_rooms(),
        date=None,
        start_hour=None,
        start_minute=None,
        end_hour=None,
        end_minute=None)


@blueprint.route("/1/book-room/", methods=["POST"])
def book():
    """POST /1/book-room/"""

    def book_error(message):
        flask.flash(message)
        #Using form.get() in case values were not POSTed
        room = form.get("room")
        if room is not None and validate_int(room):
            room = int(room)
        return flask.render_template(
            "reservations.html",
            rooms=helpers.get_rooms(),
            room=room,
            date=form.get("date"),
            start_hour=form.get("start_hour"),
            start_minute=form.get("start_minute"),
            start_period=form.get("start_period"),
            end_hour=form.get("end_hour"),
            end_minute=form.get("end_minute"),
            end_period=form.get("end_period"),
            reason=form.get("reason"))

    form = flask.request.form
    validations = [
        validate_exists(form, "room") and validate_int(form["room"])
        and helpers.is_room(form["room"]),
        validate_exists(form, "date") and validate_date(form["date"]),
        validate_exists(form, "start_hour")
        and validate_int(form["start_hour"], 1, 12),
        validate_exists(form, "start_minute")
        and validate_int(form["start_minute"], 0, 59),
        validate_exists(form, "start_period")
        and validate_in(form["start_period"], AM_OR_PM),
        validate_exists(form, "end_hour")
        and validate_int(form["end_hour"], 1, 12),
        validate_exists(form, "end_minute")
        and validate_int(form["end_minute"], 0, 59),
        validate_exists(form, "end_period")
        and validate_in(form["end_period"], AM_OR_PM),
        validate_exists(form, "reason")
    ]
    if not all(validations):
        #Should only happen if a malicious request is sent,
        #so error message is not important
        return book_error("Invalid form data")

    start_hour = int(form["start_hour"]) % 12
    if form["start_period"] == "P":
        start_hour += 12
    start_minute = int(form["start_minute"])
    end_hour = int(form["end_hour"]) % 12
    if form["end_period"] == "P":
        end_hour += 12
    end_minute = int(form["end_minute"])
    invalid_times = start_hour > end_hour or (start_hour == end_hour
                                              and start_minute >= end_minute)
    if invalid_times:
        return book_error("Start time must be before end time")

    room = int(form["room"])
    day = datetime.strptime(form["date"], YYYY_MM_DD)
    start = datetime(day.year, day.month, day.day, start_hour, start_minute)
    end = datetime(day.year, day.month, day.day, end_hour, end_minute)
    reason = form["reason"] or None
    conflicts = helpers.conflicts(room, start, end)
    if conflicts:
        message = "Room already booked for: "
        for conflict in conflicts:
            if conflict is not conflicts[0]:
                message += ", "
            start, end = conflict
            message += start.strftime(H_MM) + " to "
            message += end.strftime(H_MM)
        return book_error(message)

    helpers.add_reservation(room, flask.session["username"], reason, start,
                            end)
    return flask.render_template("reservation_success.html")


@blueprint.route("/my-reservations")
def my_reservations():
    reservations = helpers.get_my_reservations(
        flask.session["username"]) if "username" in flask.session else None

    return flask.render_template("mine-iframe.html", reservations=reservations)


@blueprint.route("/all-reservations")
def all_reservations():
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


@blueprint.route("/reservation/<int:id>", methods=["GET"])
def view_reservation(id):
    return flask.render_template(
        "reservation-view.html",
        reservation=helpers.get_reservation(id),
        now=datetime.now())


@blueprint.route("/reservation/<int:id>", methods=["DELETE"])
def delete_reservation(id):
    helpers.delete_reservation(id, flask.session.get("username"))
    return flask.jsonify({"success": True})
