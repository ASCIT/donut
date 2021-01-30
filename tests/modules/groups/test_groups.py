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
    assert len(helpers.get_members_by_group(3)) == 3


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
    res = sorted(
        res, key=lambda holder: (holder['user_id'], holder['hold_id']))
    assert res == [{
        'user_id': 2,
        'full_name': 'Robert Eng',
        'hold_id': 5,
        'start_date': None,
        'end_date': None
    }, {
        'user_id': 4,
        'full_name': 'Sean Yu',
        'hold_id': 4,
        'start_date': None,
        'end_date': None
    }, {
        'user_id': 4,
        'full_name': 'Sean Yu',
        'hold_id': 6,
        'start_date': None,
        'end_date': None
    }, {
        'user_id': 5,
        'full_name': 'Rachel Lin',
        'hold_id': 7,
        'start_date': None,
        'end_date': None
    }]

    res = helpers.get_position_holders(1)
    res = sorted(
        res, key=lambda holder: (holder['user_id'], holder['hold_id']))
    assert res == [{
        'user_id': 1,
        'full_name': 'David Qu',
        'hold_id': 1,
        'start_date': None,
        'end_date': None
    }, {
        'user_id': 2,
        'full_name': 'Robert Eng',
        'hold_id': 2,
        'start_date': None,
        'end_date': None
    }]

    res = helpers.get_position_holders([1, 5])
    res = sorted(
        res, key=lambda holder: (holder['user_id'], holder['hold_id']))
    assert res == [{
        'user_id': 1,
        'full_name': 'David Qu',
        'hold_id': 1,
        'start_date': None,
        'end_date': None
    }, {
        'user_id': 2,
        'full_name': 'Robert Eng',
        'hold_id': 2,
        'start_date': None,
        'end_date': None
    }, {
        'user_id': 2,
        'full_name': 'Robert Eng',
        'hold_id': 5,
        'start_date': None,
        'end_date': None
    }, {
        'user_id': 4,
        'full_name': 'Sean Yu',
        'hold_id': 4,
        'start_date': None,
        'end_date': None
    }, {
        'user_id': 4,
        'full_name': 'Sean Yu',
        'hold_id': 6,
        'start_date': None,
        'end_date': None
    }, {
        'user_id': 5,
        'full_name': 'Rachel Lin',
        'hold_id': 7,
        'start_date': None,
        'end_date': None
    }]


def test_get_positions_held(client):
    res = helpers.get_positions_held(4)
    assert sorted(res) == [4, 5]

    res = helpers.get_positions_held(2)
    assert sorted(res) == [1, 4, 5]

    res = helpers.get_positions_held(1)
    assert res == [1]

    res = helpers.get_positions_held(-1)
    assert res == []


def test_get_position_id(client):
    res = helpers.get_position_id('Donut Devteam', 'Head')
    assert res == 1
    res = helpers.get_position_id('Not a real group', 'Not a real position')
    assert res is None


def test_get_position_data(client):
    res = helpers.get_position_data()
    assert {
        "user_id": 1,
        "full_name": "David Qu",
        "group_id": 1,
        "group_name": "Donut Devteam",
        "pos_id": 1,
        "pos_name": "Head"
    } in res
    assert {
        "user_id": 2,
        "full_name": "Robert Eng",
        "group_id": 3,
        "group_name": "IHC",
        "pos_id": 5,
        "pos_name": "Member"
    } in res
    assert len(res) == 8


def test_get_group_data(client):
    assert helpers.get_group_data(4) == {}
    assert helpers.get_group_data(1, ["not_a_real_field"]) == "Invalid field"
    assert helpers.get_group_data(1) == group
    assert helpers.get_group_data(1, ["group_name"]) == {
        "group_name": "Donut Devteam"
    }


def test_create_pos_holders(client):
    helpers.create_position_holder(3, 3, "2018-02-22", "3005-01-01")
    res = helpers.get_position_holders(3)
    res = sorted(res, key=lambda holder: holder['hold_id'])
    assert res == [{
        'user_id': 3,
        'full_name': 'Belac Sander',
        'hold_id': 3,
        'start_date': None,
        'end_date': None
    }, {
        'user_id': 3,
        'full_name': 'Belac Sander',
        'hold_id': 8,
        'start_date': datetime.date(2018, 2, 22),
        'end_date': datetime.date(3005, 1, 1)
    }]


def test_create_group(client):
    group_id = helpers.create_group("Page House", "May the work be light",
                                    "House", False, False, True)
    assert helpers.get_group_data(group_id, [
        "group_id", "group_name", "group_desc", "type", "anyone_can_send",
        "newsgroups", "visible"
    ]) == {
        "group_name": "Page House",
        "group_desc": "May the work be light",
        "type": "House",
        "newsgroups": False,
        "anyone_can_send": False,
        "visible": True,
        "group_id": group_id
    }

    # check that a new position with name "Member" was created
    assert helpers.get_group_positions(group_id) == [{
        "pos_id": 6,
        "pos_name": "Member"
    }]
    helpers.delete_group(group_id)
    assert helpers.get_group_data(group_id) == {}
    assert helpers.get_group_positions(group_id) == []


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
