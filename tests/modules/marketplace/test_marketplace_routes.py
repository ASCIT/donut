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


def test_marketplace_view_item(client):
    rv = client.get(
        flask.url_for('marketplace.view_item'), query_string={'item_id': 1})
    assert rv.status_code == 200

    rv = client.get(
        flask.url_for('marketplace.view_item'),
        query_string={'item_id': 'not a number'})
    assert rv.status_code == 404

    rv = client.get(flask.url_for('marketplace.view_item'))
    assert rv.status_code == 404


def page_has_no_alerts(page):
    if b'alert alert-warning' in page:
        return False
    if b'id="error"' in page:
        return False
    return True


def test_marketplace_sell(client):
    rv = client.get(flask.url_for('marketplace.sell'))
    assert rv.status_code == 200
    assert page_has_no_alerts(rv.data)

    with client as c:
        # this with block is necessary to keep the client around,
        # as we can only dig into flask.request[] during the actual
        # request (see http://flask.pocoo.org/docs/0.12/testing/#keeping-the-context-around)
        rv = c.post(
            flask.url_for('marketplace.sell'), data=dict(page='CATEGORY'))
        assert rv.status_code == 200
        assert page_has_no_alerts(rv.data)

        rv = c.post(
            flask.url_for('marketplace.sell'), data=dict(page='TEXTBOOK'))
        assert rv.status_code == 200
        assert page_has_no_alerts(rv.data)

        rv = c.post(
            flask.url_for('marketplace.sell'),
            data=dict(page='INFORMATION', cat_id=1))
        assert rv.status_code == 200
        assert page_has_no_alerts(rv.data)

        rv = c.post(
            flask.url_for('marketplace.sell'),
            data=dict(page='CONFIRMATION', cat_id=1))
        assert rv.status_code == 200
        assert not page_has_no_alerts(rv.data)

        rv = c.post(
            flask.url_for('marketplace.sell'),
            data=dict(page='SUBMIT', cat_id=1))
        assert rv.status_code == 200
        assert not page_has_no_alerts(rv.data)

        # next time: look at postman errors and fix .html files
