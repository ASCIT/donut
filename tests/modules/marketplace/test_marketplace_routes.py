import flask

from donut.testing.fixtures import client
import donut


def test_marketplace_home(client):
    rv = client.get(flask.url_for('marketplace.marketplace'))
    assert rv.status_code == 200


def test_marketplace_category(client):
    rv = client.get('marketplace/view?cat=1')
    assert rv.status_code == 200

    rv = client.get('marketplace/view?cat=2')
    assert rv.status_code == 200


def test_marketplace_query(client):
    rv = client.get(
        flask.url_for('marketplace.query'),
        query_string={'cat': 2,
                      'q': 'great'})
    assert rv.status_code == 200

    rv = client.get(flask.url_for('marketplace.query'))
    assert rv.status_code == 404
