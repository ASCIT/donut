import flask

from donut.testing.fixtures import client
from donut import app
from donut.modules.marketplace import helpers


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

    rv = client.get(
        flask.url_for('marketplace.query'), query_string={'cat': 'abc'})
    assert rv.status_code == 404


def test_marketplace_view_item(client):
    rv = client.get(flask.url_for('marketplace.view_item', item_id=1))
    assert rv.status_code == 200

    rv = client.get(flask.url_for('marketplace.view_item', item_id=1000))
    assert rv.status_code == 404


def test_marketplace_manage(client):
    rv = client.get(flask.url_for('marketplace.manage'))
    assert rv.status_code == 302
    assert rv.location == flask.url_for('auth.login')

    with client.session_transaction() as sess:
        sess['username'] = 'csander'
    rv = client.get(flask.url_for('marketplace.manage'))
    assert rv.status_code == 200
    assert b'Your listings' in rv.data

    rv = client.get(flask.url_for('marketplace.archive', item_id=3))
    assert rv.status_code == 302
    assert rv.location == flask.url_for('marketplace.manage')
    assert not helpers.table_fetch(
        'marketplace_items',
        one=True,
        fields=['item_active'],
        attrs={'item_id': 3})

    rv = client.get(flask.url_for('marketplace.view_item', item_id=3))
    assert rv.status_code == 200
    assert b'This item has been archived!' in rv.data

    rv = client.get(flask.url_for('marketplace.unarchive', item_id=3))
    assert rv.status_code == 302
    assert rv.location == flask.url_for('marketplace.manage')
    assert helpers.table_fetch(
        'marketplace_items',
        one=True,
        fields=['item_active'],
        attrs={'item_id': 3})

    rv = client.get(flask.url_for('marketplace.view_item', item_id=3))
    assert rv.status_code == 200
    assert b'This item has been archived!' not in rv.data

    # Manage should fail if permissions are missing
    with client.session_transaction() as sess:
        sess['username'] = 'ruddock_pres'
    rv = client.get(flask.url_for('marketplace.archive', item_id=3))
    assert rv.status_code == 302
    assert rv.location == flask.url_for('marketplace.marketplace')
    assert helpers.table_fetch(
        'marketplace_items',
        one=True,
        fields=['item_active'],
        attrs={'item_id': 3})
    rv = client.get(flask.url_for('marketplace.unarchive', item_id=3))
    assert rv.status_code == 302
    assert rv.location == flask.url_for('marketplace.marketplace')


def test_marketplace_sell(client):
    rv = client.get(flask.url_for('marketplace.sell'))
    assert rv.status_code == 302
    assert rv.location == flask.url_for('auth.login')

    with client.session_transaction() as sess:
        sess['username'] = 'csander'
    rv = client.get(flask.url_for('marketplace.sell', state='abc'))
    assert rv.status_code == 302
    assert rv.location == flask.url_for('marketplace.sell')

    rv = client.get(flask.url_for('marketplace.sell'))
    assert rv.status_code == 200
    assert b'Please select a category for your item' in rv.data

    item = {}
    for cat in (None, 'abc', '10'):
        item['cat'] = cat
        rv = client.post(flask.url_for('marketplace.sell'), data=item)
        assert rv.status_code == 200
        assert b'Invalid category' in rv.data

    item['cat'] = '1'  # Furniture
    rv = client.post(flask.url_for('marketplace.sell'), data=item)
    assert rv.status_code == 200
    assert b'Invalid category' not in rv.data
    assert b'Missing item title' in rv.data

    item['item_title'] = 'Couch'
    rv = client.post(flask.url_for('marketplace.sell'), data=item)
    assert rv.status_code == 200
    assert b'Missing item title' not in rv.data
    assert b'Missing condition' in rv.data

    item['item_condition'] = 'Saggy'
    rv = client.post(flask.url_for('marketplace.sell'), data=item)
    assert rv.status_code == 200
    assert b'Missing condition' not in rv.data
    assert b'Invalid price' in rv.data

    for price in ('cash $$$', '1.3'):
        item['item_price'] = price
        rv = client.post(flask.url_for('marketplace.sell'), data=item)
        assert rv.status_code == 200
        assert b'Invalid price' in rv.data

    item['item_price'] = '12.34'
    item['images'] = ['not_an_image']
    rv = client.post(flask.url_for('marketplace.sell'), data=item)
    assert rv.status_code == 200
    assert b'Invalid price' not in rv.data
    assert b'Invalid image' in rv.data

    item['images'] = ['http://imgur.com/abcdef123']
    rv = client.post(
        flask.url_for('marketplace.sell'), data=item, follow_redirects=True)
    assert rv.status_code == 200
    assert b'Invalid image' not in rv.data
    assert b'Posted!' in rv.data

    rv = client.get(flask.url_for('marketplace.view_item', item_id=4))
    assert rv.status_code == 200
    assert b'Furniture' in rv.data
    assert b'Couch' in rv.data
    assert b'Saggy' in rv.data
    assert b'$12.34' in rv.data
    assert b'https://i.imgur.com/abcdef123.png' in rv.data
    assert b'csander' in rv.data

    item = {'cat': '2'}
    rv = client.post(flask.url_for('marketplace.sell'), data=item)
    assert rv.status_code == 200
    assert b'Missing textbook title' in rv.data

    item['textbook_title'] = 'Algebra'
    rv = client.post(flask.url_for('marketplace.sell'), data=item)
    assert rv.status_code == 200
    assert b'Missing textbook title' not in rv.data
    assert b'Missing textbook author' in rv.data

    item['textbook_author'] = 'Serge Lang'
    rv = client.post(flask.url_for('marketplace.sell'), data=item)
    assert rv.status_code == 200
    assert b'Missing textbook author' not in rv.data

    item['textbook_id'] = '10'
    rv = client.post(flask.url_for('marketplace.sell'), data=item)
    assert rv.status_code == 200
    assert b'Invalid textbook' in rv.data
    del item['textbook_id']

    item['textbook_edition'] = 'not_an_edition'
    rv = client.post(flask.url_for('marketplace.sell'), data=item)
    assert rv.status_code == 200
    assert b'Invalid textbook edition' in rv.data

    item['textbook_edition'] = '3'
    item['textbook_isbn'] = 'not_an_isbn'
    rv = client.post(flask.url_for('marketplace.sell'), data=item)
    assert rv.status_code == 200
    assert b'Invalid textbook edition' not in rv.data
    assert b'Invalid textbook ISBN' in rv.data

    item['textbook_isbn'] = '0-387-95385-X'
    item['item_condition'] = 'New'
    item['item_price'] = '69'
    item['item_details'] = 'Caused much pain and suffering'
    rv = client.post(
        flask.url_for('marketplace.sell'), data=item, follow_redirects=True)
    assert rv.status_code == 200
    assert b'Invalid textbook ISBN' not in rv.data
    assert b'Posted!' in rv.data

    rv = client.get(flask.url_for('marketplace.view_item', item_id=5))
    assert rv.status_code == 200
    assert b'Textbooks' in rv.data
    assert b'Algebra' in rv.data
    assert b'Serge Lang' in rv.data
    assert b'New' in rv.data
    assert b'038795385X' in rv.data
    assert b'$69.00' in rv.data
    assert b'Caused much pain and suffering' in rv.data
    assert b'csander' in rv.data


def test_marketplace_edit(client):
    with client.session_transaction() as sess:
        sess['username'] = 'csander'

    rv = client.get(
        flask.url_for('marketplace.sell', state='edit'), follow_redirects=True)
    assert rv.status_code == 200
    assert b'Invalid item' in rv.data

    rv = client.get(
        flask.url_for('marketplace.sell', state='edit', item_id=100),
        follow_redirects=True)
    assert rv.status_code == 200
    assert b'Invalid item' in rv.data

    rv = client.get(
        flask.url_for('marketplace.sell', state='edit', item_id=1),
        follow_redirects=True)
    assert rv.status_code == 200
    assert b'You do not have permission to edit this item' in rv.data

    rv = client.get(flask.url_for('marketplace.sell', state='edit', item_id=4))
    assert rv.status_code == 200
    assert b'Couch' in rv.data
    assert b'12.34' in rv.data

    new_item = {
        'cat': 1,
        'item_title': 'Slouch',
        'item_condition': 'Poor',
        'item_price': '.77',
        'item_details': 'Possibly cursed'
    }
    rv = client.post(
        flask.url_for('marketplace.sell', state='edit', item_id=4),
        data=new_item,
        follow_redirects=True)
    assert rv.status_code == 200
    assert b'Updated!' in rv.data

    rv = client.get(flask.url_for('marketplace.view_item', item_id=4))
    assert rv.status_code == 200
    assert b'Furniture' in rv.data
    assert b'Slouch' in rv.data
    assert b'Poor' in rv.data
    assert b'$0.77' in rv.data
    assert b'https://i.imgur.com/abcdef123.png' not in rv.data
    assert b'csander' in rv.data
