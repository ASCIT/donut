"""
Tests donut/modules/core/
"""
from donut.testing.fixtures import client
from donut import app
from donut.modules.core.helpers import get_member_data
from donut.modules.core.routes import get_members


# Helpers
def test_get_member_data(client):
    assert get_member_data(1)['user_id'] == 1

# Test Routes
def test_get_members(client):
    assert get_members(1) is not None
