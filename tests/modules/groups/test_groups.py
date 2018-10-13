"""
Tests donut/modules/groups/
"""
from donut.testing.fixtures import client
from donut import app
from donut.modules.groups import helpers
from donut.modules.groups import routes
import datetime

group = {
    "group_id": 1,
    "group_name": "Donut Devteam",
    "group_desc": None,
    "type": ""
}


# Helpers
def test_get_group_list_data(client):
    assert helpers.get_group_list_data(["not_a_real_field"]) == "Invalid field"
    assert helpers.get_group_list_data(["group_name"]) == [{
        "group_name":
        "Donut Devteam"
    }, {
        "group_name": "IHC"
    }, {
        "group_name":
        "Ruddock House"
    }]
    assert helpers.get_group_list_data()[0] == group
    assert helpers.get_group_list_data(None, {"group_id": 1})[0] == group
    assert helpers.get_group_list_data(None, {"group_id": 4}) == []


def test_get_members_by_group(client):
    assert helpers.get_members_by_group(1)[0]["user_id"] == 1
    assert helpers.get_members_by_group(1)[1]["user_id"] == 2
    assert len(helpers.get_members_by_group(1)) == 2
    assert len(helpers.get_members_by_group(2)) == 3
    assert len(helpers.get_members_by_group(3)) == 2


def test_get_group_positions_data(client):
    assert helpers.get_group_positions(1) == [{
        "pos_id": 1,
        "pos_name": "Head"
    }, {
        "pos_id": 2,
        "pos_name": "Secretary"
    }]
    assert helpers.get_group_positions(4) == []


def test_get_position_holders(client):
    res = helpers.get_position_holders(5)
    assert len(res) == 2
    assert res[0]["first_name"] == "Sean"
    assert res[1]["first_name"] == "Robert"
    res = helpers.get_position_holders(1)
    assert len(res) == 2
    assert res[0]["first_name"] == "David"
    assert res[1]["first_name"] == "Robert"
    res = helpers.get_position_holders([1, 5])
    assert len(res) == 3
    assert res[0]["first_name"] == "David"
    assert res[1]["first_name"] == "Robert"
    assert res[2]["first_name"] == "Sean"


def test_get_position_data(client):
    res = helpers.get_position_data()
    assert res[0]["first_name"] == "David"
    assert res[0]["last_name"] == "Qu"
    assert res[0]["group_name"] == "Donut Devteam"
    assert res[0]["user_id"] == 1
    assert res[0]["pos_name"] == "Head"
    assert res[0]["group_id"] == 1
    assert res[0]["pos_id"] == 1
    assert {
        "first_name": "Robert",
        "last_name": "Eng",
        "group_name": "IHC",
        "user_id": 2,
        "pos_name": "Member",
        "group_id": 3,
        "pos_id": 5,
        "start_date": None,
        "end_date": None
    } in res
    assert len(res) == 7


def test_delete_position(client):
    assert helpers.get_group_positions(1) == [{
        "pos_id": 1,
        "pos_name": "Head"
    }, {
        "pos_id": 2,
        "pos_name": "Secretary"
    }]
    helpers.delete_position(1)
    assert helpers.get_group_positions(1) == [{
        "pos_id": 2,
        "pos_name": "Secretary"
    }]


def test_get_group_data(client):
    assert helpers.get_group_data(4) == {}
    assert helpers.get_group_data(1, ["not_a_real_field"]) == "Invalid field"
    assert helpers.get_group_data(1) == group
    assert helpers.get_group_data(1, ["group_name"]) == {
        "group_name": "Donut Devteam"
    }


def test_create_pos_holders(client):
    helpers.create_position_holder(3, 3, "2018-02-22", "2019-02-22")
    assert helpers.get_position_holders(3) == [{
        "user_id": 3,
        "first_name": "Caleb",
        "last_name": "Sander",
        "start_date": None,
        "end_date": None
    }, {
        "user_id":
        3,
        "first_name":
        "Caleb",
        "last_name":
        "Sander",
        "start_date":
        datetime.date(2018, 2, 22),
        "end_date":
        datetime.date(2019, 2, 22)
    }]


# Test Routes
# Difficult to test because query arguments are undefined outside Flask context
# def test_get_groups_list(client):
#     assert routes.get_groups_list() is not None


def test_get_group_positions(client):
    assert routes.get_group_positions(1) is not None


def get_groups(client):
    assert routes.get_groups(1) is not None


def test_get_group_members(client):
    assert routes.get_group_members(1) is not None


def test_get_pos_holders(client):
    assert routes.get_pos_holders(1) is not None
