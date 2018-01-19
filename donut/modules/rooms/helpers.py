from datetime import timedelta
from itertools import groupby
import flask
import sqlalchemy

from donut.auth_utils import get_user_id


def get_rooms():
    """Gets a list of rooms in the form {id, name, title, desc}"""

    query = sqlalchemy.text(
        "SELECT id, location, title, description FROM rooms")
    rooms = flask.g.db.execute(query).fetchall()

    return [{
        "id": id,
        "name": location,
        "title": title,
        "desc": description
    } for id, location, title, description in rooms]


def is_room(room_id_string):
    query = sqlalchemy.text("SELECT id FROM rooms WHERE id = :room_id")
    room = flask.g.db.execute(query, room_id=int(room_id_string))
    return room is not None


def add_reservation(room, username, reason, start, end):
    # TODO: Check that there are no overlapping reservations
    insertion = sqlalchemy.text("""
        INSERT INTO room_reservations
        (room_id, user_id, reason, start_time, end_time)
        VALUES (:room, :user, :reason, :start, :end)
    """)
    flask.g.db.execute(
        insertion,
        room=room,
        user=get_user_id(username),
        reason=reason,
        start=start,
        end=end)


def render_reservations(rooms, start, end):
    if not rooms:
        rooms = [room["id"] for room in get_rooms()]
    query = sqlalchemy.text("""
        SELECT reservation.id, location, start_time, end_time
        FROM room_reservations AS reservation LEFT OUTER JOIN rooms AS room
        ON reservation.room_id = room.id
        WHERE :start <= end_time AND start_time <= :end
        AND room.id IN (""" + ",".join(map(str, rooms)) + """)
        ORDER BY start_time
    """)
    reservations = flask.g.db.execute(
        query,
        start=start,
        end=end + timedelta(days=1),  # until start of following day
        rooms=rooms)
    reservations = [{
        "id": id,
        "room": room,
        "start": start,
        "end": end
    } for id, room, start, end in reservations]
    day_reservations = [
        {
            "day": day,
            "reservations": list(day_rooms)
        }
        for day, day_rooms in groupby(
            reservations, lambda reservation: reservation["start"].date())
    ]
    return flask.render_template(
        "all-iframe.html",
        rooms=get_rooms(),
        start=start,
        end=end,
        reservations=day_reservations)


def get_reservation(id):
    query = sqlalchemy.text("""
        SELECT location, title, full_name, start_time, end_time, reason
        FROM room_reservations AS reservation
            LEFT OUTER JOIN members_full_name as member
            ON reservation.user_id = member.user_id
            LEFT OUTER JOIN rooms AS room
            ON reservation.room_id = room_id
        WHERE reservation.id = :id
    """)
    location, title, name, start, end, reason = flask.g.db.execute(
        query, id=id).fetchone()
    return {
        "location": location,
        "title": title,
        "name": name,
        "start": start,
        "end": end,
        "reason": reason
    }
