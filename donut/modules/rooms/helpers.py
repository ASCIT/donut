from datetime import datetime, timedelta
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
    room = flask.g.db.execute(query, room_id=int(room_id_string)).fetchone()
    return room is not None


def add_reservation(room, username, reason, start, end):
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


def get_all_reservations(rooms, start, end):
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
    return [{
        "day": day,
        "reservations": list(day_rooms)
    }
            for day, day_rooms in groupby(
                reservations, lambda reservation: reservation["start"].date())]


def split(lst, pred):
    switch_index = len(lst)
    for index, item in enumerate(lst):
        if not pred(item):
            switch_index = index
            break
    return [lst[:switch_index], lst[switch_index:]]


def get_my_reservations(username):
    query = sqlalchemy.text("""
        SELECT reservation.id, location, start_time, end_time
        FROM room_reservations AS reservation
            LEFT OUTER JOIN users AS user
            ON reservation.user_id = user.user_id
            LEFT OUTER JOIN rooms AS room
            ON reservation.room_id = room.id
        WHERE user.username = :username
        ORDER BY start_time
    """)
    reservations = flask.g.db.execute(query, username=username)
    reservations = [{
        "id": id,
        "room": room,
        "start": start,
        "end": end
    } for id, room, start, end in reservations]
    now = datetime.now()
    past, upcoming = split(reservations, lambda res: res["start"] < now)
    return {
        "past": past[::-1],  #show most recent past first
        "upcoming": upcoming
    }


def get_reservation(id):
    query = sqlalchemy.text("""
        SELECT location, title, full_name, start_time, end_time, reason, username
        FROM room_reservations AS reservation
            LEFT OUTER JOIN members_full_name as member
            ON reservation.user_id = member.user_id
            LEFT OUTER JOIN users as user
            ON reservation.user_id = user.user_id
            LEFT OUTER JOIN rooms AS room
            ON reservation.room_id = room_id
        WHERE reservation.id = :id
    """)
    location, title, name, start, end, reason, username = flask.g.db.execute(
        query, id=id).fetchone()
    return {
        "location": location,
        "title": title,
        "name": name,
        "start": start,
        "end": end,
        "reason": reason,
        "username": username
    }


def delete_reservation(id, username):
    if username is None:
        raise "Not logged in"

    query = sqlalchemy.text("""
        DELETE FROM room_reservations
        WHERE id = :id
        AND user_id IN (
            SELECT user_id FROM users WHERE username = :username
        )
    """)
    flask.g.db.execute(query, id=id, username=username)


def conflicts(room, start, end):
    """Returns a list of overlapping [start_time, end_time] tuples"""
    query = sqlalchemy.text("""
        SELECT start_time, end_time FROM room_reservations
        WHERE room_id = :room AND :start < end_time AND start_time < :end
        ORDER BY start_time
    """)
    return list(flask.g.db.execute(query, room=room, start=start, end=end))
