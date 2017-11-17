import flask
import sqlalchemy

def get_rooms():
    """Gets a list of rooms in the form {id, name}"""

    query = sqlalchemy.text("SELECT id, location FROM rooms")
    rooms = flask.g.db.execute(query).fetchall()

    return [{"id": id, "name": location} for id, location in rooms]
