import flask

from donut.testing.fixtures import client
import donut


def test_marketplace_home(client):
    rv = client.get(flask.url_for('marketplace.marketplace'))
    assert rv.status_code == 200


def test_marketplace_category(client):
    rv = client.get(
        flask.url_for('marketplace.query'), query_string={'cat': 1})
    assert rv.status_code == 200

    rv = client.get(
        flask.url_for('marketplace.query'), query_string={'cat': 'all'})
    assert rv.status_code == 200


def test_marketplace_query(client):
    rv = client.get(
        flask.url_for('marketplace.query'),
        query_string={'cat': 2,
                      'q': 'great'})
    assert rv.status_code == 200

    rv = client.get(flask.url_for('marketplace.query'))
    assert rv.status_code == 404


def test_marketplace_view_item(client):
    rv = client.get(flask.url_for('marketplace.view_item', item_id=1))
    assert rv.status_code == 200
