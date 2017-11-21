"""
Tests donut/modules/groups/
"""
from donut.testing.fixtures import client
from donut import app
from donut.modules.groups.helpers import get_position_data
from donut.modules.groups.routes import get_positions


# Helpers
def test_get_position_data(client):
    test_list = ["Head", "Secretary"]
    assert get_position_data() == test_list

# Test Routes
def test_get_positions():
    assert get_positions() is not None
