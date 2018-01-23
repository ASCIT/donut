"""
Tests donut/modules/rooms/
"""
from datetime import datetime
from donut.testing.fixtures import client
from donut import app
from donut.modules.rooms import helpers
from donut.modules.rooms import routes


# Helpers
def test_get_rooms(client):
    assert helpers.get_rooms() == [{
        "id":
        1,
        "name":
        "SAC 23",
        "title":
        "ASCIT Screening Room",
        "desc":
        "A room for watching DVDs and videos"
    }]


def test_is_room(client):
    assert helpers.is_room("1")
    assert not helpers.is_room("2")


def test_add_and_get_reservations(client):
    assert helpers.get_all_reservations([],
                                        datetime(2017, 11, 14),
                                        datetime(2017, 11, 15)) == []
    assert helpers.get_all_reservations([1],
                                        datetime(2017, 11, 14),
                                        datetime(2017, 11, 15)) == []
    helpers.add_reservation(1, "dqu", None,
                            datetime(2017, 11, 14, 18),
                            datetime(2017, 11, 14, 19))
    helpers.add_reservation(1, "reng", "Dank memes",
                            datetime(2017, 11, 15, 12),
                            datetime(2017, 11, 15, 13))
    first_day_reservations = {
        "day":
        datetime(2017, 11, 14).date(),
        "reservations": [{
            "id": 1,
            "room": "SAC 23",
            "start": datetime(2017, 11, 14, 18),
            "end": datetime(2017, 11, 14, 19)
        }]
    }
    assert helpers.get_all_reservations(
        [], datetime(2017, 11, 14), datetime(2017, 11,
                                             14)) == [first_day_reservations]
    second_day_reservations = {
        "day":
        datetime(2017, 11, 15).date(),
        "reservations": [{
            "id": 2,
            "room": "SAC 23",
            "start": datetime(2017, 11, 15, 12),
            "end": datetime(2017, 11, 15, 13)
        }]
    }
    assert helpers.get_all_reservations(
        [], datetime(2017, 11, 15), datetime(2017, 11,
                                             15)) == [second_day_reservations]
    assert helpers.get_all_reservations([1],
                                        datetime(2017, 11, 14),
                                        datetime(2017, 11, 15)) == [
                                            first_day_reservations,
                                            second_day_reservations
                                        ]
