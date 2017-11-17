"""
Tests donut/modules/core/
"""
from donut.testing.fixtures import client
from donut import app
from donut.modules.core.helpers import (
    get_member_data,
    get_member_list_data,
    get_name_and_email, )
from donut.modules.core.routes import get_members


# Helpers
def test_get_member_data(client):
    assert get_member_data(1)["user_id"] == 1
    # check functionality for lists of user id's
    members = get_member_data([1, 2])
    assert isinstance(members, list)
    assert members[1]["user_id"] == 2
    # try an invalid field
    assert get_member_data(1, "spaghetti") == "Invalid field"
    # try a list of user id's with no valid id's
    assert get_member_data([-1]) == {}
    assert get_member_data([]) == {}


def test_get_member_list_data(client):
    members = get_member_list_data(attrs={"uid": "1957540"})
    assert members[0]["uid"] == "1957540"
    # try an invalid field
    assert get_member_list_data("spaghetti") == "Invalid field"


def test_get_name_and_email(client):
    name, email = get_name_and_email(1)
    assert name == "David Qu"
    assert email == "davidqu12345@gmail.com"


# Test Routes
def test_get_members(client):
    assert get_members(1) is not None
