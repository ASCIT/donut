"""
Tests donut/modules/groups/
"""
from donut.testing.fixtures import client
from donut import app
from donut.modules.groups.helpers import get_position_data
from donut.modules.groups.routes import get_positions


# Helpers
def test_get_position_data(client):
    res = get_position_data()
    assert res[0]["group_id"] == 1
    assert res[0]["pos_id"] == 2
    assert res[0]["pos_name"] == "Secretary"
    assert res[0]["user_id"] == 2


# Test Routes
def test_get_positions():
    assert get_positions() is not None
