import flask

from donut.testing.fixtures import client
import donut


def test_marketplace_home(client):
    donut.init('test')
    donut.before_request()
    rv = client.get(flask.url_for('marketplace.marketplace'))
    donut.teardown_request(None)

    assert rv.status_code == 200

def test_marketplace_category(client):
    donut.init('test')
    donut.before_request()
    rv = client.get(flask.url_for('marketplace.category', cat=1))
    #assert rv.status_code == 200

    rv = client.get(flask.url_for('marketplace.category', cat=2))
    #assert rv.status_code == 200
    donut.teardown_request(None)

def test_marketplace_query(client):
    rv = client.get(flask.url_for('marketplace.query', cat=2, q='great'))
    #assert rv.status_code == 200

    rv = client.get(flask.url_for('marketplace.query'))
    #assert rv.status_code == 404
