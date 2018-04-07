from datetime import datetime, timedelta
from itertools import groupby
import flask
import pymysql.cursors

from donut.auth_utils import get_user_id


def get_rooms():
    """Gets a list of rooms in the form {id, name, title, desc}"""

    query = 'SELECT room_id, location, title, description FROM rooms'
    with flask.g.pymysql_db.cursor() as cursor:
        cursor.execute(query)
        return cursor.fetchall()


def is_room(room_id_string):
    query = "SELECT room_id FROM rooms WHERE room_id = %s"
    with flask.g.pymysql_db.cursor() as cursor:
        cursor.execute(query, [room_id_string])
        return cursor.fetchone() is not None


def add_reservation(room, username, reason, start, end):
    insertion = """
        INSERT INTO room_reservations
        (room_id, user_id, reason, start_time, end_time)
        VALUES (%s, %s, %s, %s, %s)
    """
    with flask.g.pymysql_db.cursor() as cursor:
        cursor.execute(insertion,
                       [room, get_user_id(username), reason, start, end])


def get_all_reservations(rooms, start, end):
    if not rooms:
        rooms = [room["room_id"] for room in get_rooms()]
    query = """
        SELECT reservation_id, location, start_time, end_time
        FROM room_reservations NATURAL JOIN rooms AS room
        WHERE %s <= end_time AND start_time <= %s
        AND room.room_id IN (""" + ",".join(["%s"] * len(rooms)) + """)
        ORDER BY start_time
    """
    with flask.g.pymysql_db.cursor() as cursor:
        values = [start, end + timedelta(days=1)]
        values.extend(rooms)
        cursor.execute(query, values)
        reservations = cursor.fetchall()

    return [
        {
            "day": day,
            "reservations": list(day_rooms)
        }
        for day, day_rooms in groupby(
            reservations, lambda reservation: reservation["start_time"].date())
    ]


def split(lst, pred):
    switch_index = len(lst)
    for index, item in enumerate(lst):
        if not pred(item):
            switch_index = index
            break
    return [lst[:switch_index], lst[switch_index:]]


def get_my_reservations(username):
    query = """
        SELECT reservation_id, location, start_time, end_time
        FROM room_reservations AS reservation
            LEFT OUTER JOIN users AS user
            ON reservation.user_id = user.user_id
            LEFT OUTER JOIN rooms AS room
            ON reservation.room_id = room.room_id
        WHERE user.username = %s
        ORDER BY start_time
    """
    with flask.g.pymysql_db.cursor() as cursor:
        cursor.execute(query, [username])
        reservations = cursor.fetchall()
    now = datetime.now()
    past, upcoming = split(reservations, lambda res: res["start_time"] < now)
    return {
        "past": past[::-1],  #show most recent past first
        "upcoming": upcoming
    }


def get_reservation(id):
    query = """
        SELECT location, title, full_name, start_time, end_time, reason, username
        FROM room_reservations AS reservation
            LEFT OUTER JOIN members_full_name as member
            ON reservation.user_id = member.user_id
            LEFT OUTER JOIN users as user
            ON reservation.user_id = user.user_id
            LEFT OUTER JOIN rooms AS room
            ON reservation.room_id = room.room_id
        WHERE reservation_id = %s
    """
    with flask.g.pymysql_db.cursor() as cursor:
        cursor.execute(query, [id])
        return cursor.fetchone()


def delete_reservation(id, username):
    if username is None:
        raise "Not logged in"

    query = """
        DELETE FROM room_reservations
        WHERE reservation_id = %s
        AND user_id IN (
            SELECT user_id FROM users WHERE username = %s
        )
    """
    with flask.g.pymysql_db.cursor() as cursor:
        cursor.execute(query, [id, username])


def conflicts(room, start, end):
    """Returns a list of overlapping [start_time, end_time] tuples"""
    query = """
        SELECT start_time, end_time FROM room_reservations
        WHERE room_id = %s AND %s < end_time AND start_time < %s
        ORDER BY start_time
    """
    with flask.g.pymysql_db.cursor() as cursor:
        cursor.execute(query, [room, start, end])
        results = cursor.fetchall()
    return [(r['start_time'], r['end_time']) for r in results]
