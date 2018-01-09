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
    assert res is not None
