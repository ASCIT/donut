"""
Tests donut/modules/committee_sites/
"""
from datetime import date
import flask
import pytest
from donut.testing.fixtures import client
from donut import app
import donut.modules.core.helpers as core_helpers
from donut.modules.committee_sites import helpers
from donut.modules.committee_sites import routes


def test_routes(client):
    assert client.get(flask.url_for('committee_sites.boc')).status_code == 200
    assert client.get(
        flask.url_for('committee_sites.defendants')).status_code == 200
    assert client.get(
        flask.url_for('committee_sites.witnesses')).status_code == 200
    assert client.get(flask.url_for('committee_sites.FAQ')).status_code == 200
    assert client.get(
        flask.url_for('committee_sites.reporters')).status_code == 200
    assert client.get(
        flask.url_for('committee_sites.bylaws')).status_code == 200
    assert client.get(
        flask.url_for('committee_sites.ascit_bylaws')).status_code == 200
    assert client.get(flask.url_for(
        'committee_sites.honor_system_handbook')).status_code == 200
    assert client.get(flask.url_for('committee_sites.CRC')).status_code == 200


def test_get_boc(client):
    result = helpers.get_member('BoC')
    assert result == [('David Qu', 'Chair', 'davidqu12345@gmail.com'),
                      ('Robert Eng', 'Avery', 'reng@caltech.edu')]


def test_get_crc(client):
    result = helpers.get_member('CRC')
    assert result == [('Robert Eng', 'Chair', 'reng@caltech.edu'),
                      ('Caleb Sander', 'Lloyd', 'csander@caltech.edu')]
