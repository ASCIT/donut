import flask
import sqlalchemy

from donut.auth_utils import get_user_id


def get_rooms():
    """Gets a list of rooms in the form {id, name}"""

    query = sqlalchemy.text("SELECT id, location FROM rooms")
    rooms = flask.g.db.execute(query).fetchall()

    return [{"id": id, "name": location} for id, location in rooms]


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
    query = sqlalchemy.text("""
        SELECT room_reservations.id, location, start_time, end_time
        FROM room_reservations LEFT OUTER JOIN rooms
        WHERE room_reservations.room_id = rooms.id
        AND end_time >= :start AND start_time >= :end
    """)
    reservations = flask.g.db.execute(query, start=start, end=end)
    print(reservations)
    return flask.render_template("all-iframe.html", rooms=get_rooms(), start=start, end=end)