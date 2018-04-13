"""
Tests donut/modules/rooms/
"""
from datetime import datetime, timedelta
import pytest
from donut.testing.fixtures import client
from donut import app
from donut.modules.rooms import helpers
from donut.modules.rooms import routes


# Helpers
def test_get_rooms(client):
    assert helpers.get_rooms() == [{
        "room_id":
        1,
        "location":
        "SAC 23",
        "title":
        "ASCIT Screening Room",
        "description":
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
            "reservation_id": 1,
            "location": "SAC 23",
            "start_time": datetime(2017, 11, 14, 18),
            "end_time": datetime(2017, 11, 14, 19)
        }]
    }
    assert helpers.get_all_reservations(
        [], datetime(2017, 11, 14), datetime(2017, 11,
                                             14)) == [first_day_reservations]
    second_day_reservations = {
        "day":
        datetime(2017, 11, 15).date(),
        "reservations": [{
            "reservation_id": 2,
            "location": "SAC 23",
            "start_time": datetime(2017, 11, 15, 12),
            "end_time": datetime(2017, 11, 15, 13)
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
    assert helpers.get_all_reservations([2],
                                        datetime(2017, 11, 14),
                                        datetime(2017, 11, 15)) == []
    assert helpers.get_reservation(2) == {
        "location": "SAC 23",
        "title": "ASCIT Screening Room",
        "full_name": "Robert Eng",
        "start_time": datetime(2017, 11, 15, 12),
        "end_time": datetime(2017, 11, 15, 13),
        "reason": "Dank memes",
        "username": "reng"
    }
    with pytest.raises(Exception):
        helpers.delete_reservation(2, None)
    helpers.delete_reservation(2, "wrong-user")
    assert helpers.get_all_reservations(
        [], datetime(2017, 11, 15), datetime(2017, 11,
                                             15)) == [second_day_reservations]
    helpers.delete_reservation(2, "reng")
    assert helpers.get_all_reservations([],
                                        datetime(2017, 11, 15),
                                        datetime(2017, 11, 15)) == []


def test_get_my_reservations(client):
    now = datetime.now()
    helpers.add_reservation(
        1,
        "reng",
        "Upcoming",
        datetime(now.year, now.month, now.day, 12) + timedelta(days=1),
        datetime(now.year, now.month, now.day, 13) + timedelta(days=1))
    helpers.add_reservation(
        1,
        "reng",
        "Past older",
        datetime(now.year, now.month, now.day, 12) + timedelta(days=-2),
        datetime(now.year, now.month, now.day, 13) + timedelta(days=-2))
    helpers.add_reservation(
        1,
        "reng",
        "Past newer",
        datetime(now.year, now.month, now.day, 12) + timedelta(days=-1),
        datetime(now.year, now.month, now.day, 13) + timedelta(days=-1))
    helpers.add_reservation(
        1,
        "dqu",
        "Not mine",
        datetime(now.year, now.month, now.day, 14) + timedelta(days=1),
        datetime(now.year, now.month, now.day, 15) + timedelta(days=1))
    assert helpers.get_my_reservations("reng") == {
        "past": [{
            "reservation_id":
            5,
            "location":
            "SAC 23",
            "start_time":
            datetime(now.year, now.month, now.day, 12) + timedelta(days=-1),
            "end_time":
            datetime(now.year, now.month, now.day, 13) + timedelta(days=-1)
        }, {
            "reservation_id":
            4,
            "location":
            "SAC 23",
            "start_time":
            datetime(now.year, now.month, now.day, 12) + timedelta(days=-2),
            "end_time":
            datetime(now.year, now.month, now.day, 13) + timedelta(days=-2)
        }],
        "upcoming": [{
            "reservation_id":
            3,
            "location":
            "SAC 23",
            "start_time":
            datetime(now.year, now.month, now.day, 12) + timedelta(days=1),
            "end_time":
            datetime(now.year, now.month, now.day, 13) + timedelta(days=1)
        }]
    }


def test_conflicts(client):
    start, end = datetime(2017, 10, 31, 12, 30), datetime(2017, 10, 31, 14, 30)
    helpers.add_reservation(1, "reng", None, start, end)
    conflict = [(start, end)]
    assert helpers.conflicts(1, datetime(2017, 10, 31, 11, 30),
                             start) == []  #entirely before
    assert helpers.conflicts(
        1, datetime(2017, 10, 31, 12, 00), datetime(
            2017, 10, 31, 15, 00)) == conflict  #before, during, and after
    assert helpers.conflicts(
        1, datetime(2017, 10, 31, 12, 00), datetime(
            2017, 10, 31, 13, 00)) == conflict  #before and during
    assert helpers.conflicts(
        1, datetime(2017, 10, 31, 13, 00), datetime(2017, 10, 31, 14,
                                                    00)) == conflict  #during
    assert helpers.conflicts(
        1, datetime(2017, 10, 31, 14, 00), datetime(
            2017, 10, 31, 15, 00)) == conflict  #during and after
    assert helpers.conflicts(1, end, datetime(2017, 10, 31, 15,
                                              30)) == []  #entirely after


# Avoiding testing routes because it entirely relies on sessions and arguments
