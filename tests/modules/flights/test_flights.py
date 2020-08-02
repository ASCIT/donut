import flask
from donut.modules.flights import helpers
from donut.testing.fixtures import client


def test_update(client):
    helpers.update('', False)
    assert helpers.get_settings() == {'visible': False, 'link': ''}
    helpers.update('valid_link', True)
    assert helpers.get_settings() == {'visible': True, 'link': 'valid_link'}
