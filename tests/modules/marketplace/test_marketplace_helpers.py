from donut.testing.fixtures import client
from donut import app
import donut.modules.groups.helpers as group_helpers
from donut.modules.marketplace import helpers
import flask
from decimal import Decimal


def test_get_category_name_from_id(client):
    cat_name = helpers.get_category_name_from_id(1)
    assert cat_name == 'Furniture'


def test_get_table_list_data(client):
    table = 'marketplace_categories'
    attrs = {'cat_title': 'Furniture'}
    result = helpers.table_fetch(table, attrs=attrs)
    assert len(result) == 1  # only one result

    table = 'marketplace_items'
    fields = ['item_price', 'item_title']
    attrs = {'cat_id': 1}
    result = helpers.table_fetch(table, fields=fields, attrs=attrs)
    assert result == [{'item_price': Decimal('5.99'), 'item_title': 'A table'}]


def test_get_matches(client):
    l1 = [1, 2, 3, 4]
    l2 = [4, 3]
    assert helpers.get_matches(l1, l2) == 2
    assert helpers.get_matches(l2, l1) == 2
    assert helpers.get_matches(l1, l1) == 4
    l3 = []
    assert helpers.get_matches(l3, l3) == 0


def test_tokenize_query(client):
    query = "and,if great testing testing ,.,..,/./,/,./,./,"
    assert helpers.tokenize_query(query) == ['great', 'testing', 'testing']


def test_validate_isbn(client):
    assert helpers.validate_isbn("978-1-60309-419-1")
    assert helpers.validate_isbn("9971-5-0210-0")
    assert helpers.validate_isbn("0-8044-2957-X")
    assert helpers.validate_isbn("0-9752298-0-X")
    assert helpers.validate_isbn("978-3-16-148410-0")

    assert not helpers.validate_isbn('-9971-5-0210-0')
    assert not helpers.validate_isbn('9971-5-0210-0-')
    assert not helpers.validate_isbn('9971-5--0210-0')
    assert not helpers.validate_isbn("978-1-60309-419-0")
    assert not helpers.validate_isbn("9971-5-0210-X")
    assert not helpers.validate_isbn("0-8044-2957-1")
    assert not helpers.validate_isbn("0-9752298-0-2")
    assert not helpers.validate_isbn("978-3-16-148400-0")


def test_validate_edition(client):
    assert helpers.validate_edition('1')
    assert helpers.validate_edition('2')
    assert helpers.validate_edition('2019')
    assert helpers.validate_edition('international')
    assert helpers.validate_edition('InTeRnAtIoNaL')

    assert not helpers.validate_edition('')
    assert not helpers.validate_edition('1a')
    assert not helpers.validate_edition('first')
    assert not helpers.validate_edition('1st')


def test_validate_price(client):
    assert helpers.validate_price('100')
    assert helpers.validate_price('8')
    assert helpers.validate_price('18.29')
    assert helpers.validate_price('.63')
    assert helpers.validate_price('0.45')

    assert not helpers.validate_price('abc')
    assert not helpers.validate_price('')
    assert not helpers.validate_price('012')
    assert not helpers.validate_price('12.')
    assert not helpers.validate_price('12.3')
    assert not helpers.validate_price('12.333')
    assert not helpers.validate_price('00.45')
    assert not helpers.validate_price('.123')
    assert not helpers.validate_price('12a33')
    assert not helpers.validate_price('0b99')


def test_validate_image(client):
    assert helpers.validate_image('http://i.imgur.com/abcdef123.png'
                                  ) == 'http://i.imgur.com/abcdef123.png'
    assert helpers.validate_image('https://i.imgur.com/abcdef123.png'
                                  ) == 'https://i.imgur.com/abcdef123.png'
    assert helpers.validate_image('http://i.imgur.com/abcdef123.jpg'
                                  ) == 'http://i.imgur.com/abcdef123.jpg'
    assert helpers.validate_image('https://i.imgur.com/abcdef123.jpg'
                                  ) == 'https://i.imgur.com/abcdef123.jpg'
    assert helpers.validate_image(
        'http://imgur.com/abcdef123') == 'https://i.imgur.com/abcdef123.png'
    assert helpers.validate_image(
        'https://imgur.com/abcdef123') == 'https://i.imgur.com/abcdef123.png'
    assert helpers.validate_image('abc') is None
    assert helpers.validate_image('http://imgur.com/') is None


def test_process_edition(client):
    assert helpers.process_edition('1') == "1st"
    assert helpers.process_edition('2') == "2nd"
    assert helpers.process_edition('3') == "3rd"
    assert helpers.process_edition('4') == "4th"
    assert helpers.process_edition('5') == "5th"
    assert helpers.process_edition('6') == "6th"
    assert helpers.process_edition('7') == "7th"
    assert helpers.process_edition('8') == "8th"
    assert helpers.process_edition('9') == "9th"
    assert helpers.process_edition('10') == "10th"
    assert helpers.process_edition('11') == "11th"
    assert helpers.process_edition('12') == "12th"
    assert helpers.process_edition('13') == "13th"
    assert helpers.process_edition('14') == "14th"
    assert helpers.process_edition('15') == "15th"
    assert helpers.process_edition('16') == "16th"
    assert helpers.process_edition('17') == "17th"
    assert helpers.process_edition('18') == "18th"
    assert helpers.process_edition('19') == "19th"
    assert helpers.process_edition('20') == "20th"
    assert helpers.process_edition('21') == "21st"
    assert helpers.process_edition('2017') == "2017"
    assert helpers.process_edition("hello") == "hello"


def count_textbooks():
    s = "SELECT COUNT(*) FROM marketplace_textbooks"
    with flask.g.pymysql_db.cursor() as cursor:
        cursor.execute(s)
        result = cursor.fetchone()
    return result['COUNT(*)']


def test_add_textbook(client):
    assert count_textbooks() == 0

    assert helpers.add_textbook("title", "author") == 1
    assert helpers.add_textbook("title2", "author") == 2
    assert helpers.add_textbook("title", "author2") == 3
    assert count_textbooks() == 3

    assert helpers.add_textbook("title", "author") == 1
    assert count_textbooks() == 3


def test_can_manage(client):
    # User who is not logged in cannot manage any items
    with app.test_request_context():
        assert not helpers.can_manage({'user_id': 3})

    # Non-admin can only manage their items
    with app.test_request_context():
        flask.session['username'] = 'csander'
        assert helpers.can_manage({'user_id': 3})
        assert not helpers.can_manage({'user_id': 2})

    # Admin can manage everyone's items
    group_helpers.add_position(1, 'Lead')
    group_helpers.create_position_holder(7, 2, None, None)
    query = 'INSERT INTO position_permissions(pos_id, permission_id) VALUES (7, 1)'
    with flask.g.pymysql_db.cursor() as cursor:
        cursor.execute(query)
    with app.test_request_context():
        flask.session['username'] = 'reng'
        assert helpers.can_manage({'user_id': 2})
        assert helpers.can_manage({'user_id': 3})


def test_archive(client):
    item_id = helpers.create_new_listing({
        'user_id': 3,
        'cat_id': 1,
        'item_title': 'Thing',
        'item_condition': 'Good',
        'item_details': '',
        'item_price': '1.23',
        'images': []
    })
    assert helpers.table_fetch(
        'marketplace_items',
        one=True,
        fields=('item_active', ),
        attrs={'item_id': item_id})
    helpers.set_active_status(item_id, False)
    assert not helpers.table_fetch(
        'marketplace_items',
        one=True,
        fields=('item_active', ),
        attrs={'item_id': item_id})
    helpers.set_active_status(item_id, True)
    assert helpers.table_fetch(
        'marketplace_items',
        one=True,
        fields=('item_active', ),
        attrs={'item_id': item_id})


def test_my_items(client):
    with app.test_request_context():
        flask.session['username'] = 'dqu'
        item, = helpers.get_my_items()
        del item['item_timestamp']
        assert item == {
            'item_id': 1,
            'item_title': 'A table',
            'textbook_title': None,
            'item_price': Decimal('5.99'),
            'cat_title': 'Furniture',
            'item_active': 1
        }

    with app.test_request_context():
        flask.session['username'] = 'reng'
        assert helpers.get_my_items() == ()


def test_search_table(client):
    furniture = helpers.generate_search_table({'cat_id': 1}, '')
    for item in furniture:
        del item['item_timestamp']
    furniture = sorted(furniture, key=lambda item: item['item_id'])
    assert furniture == [{
        'item_id': 1,
        'cat_title': 'Furniture',
        'item_title': 'A table',
        'textbook_title': None,
        'item_price': Decimal('5.99'),
        'user_id': 1,
        'user_url': 'http://127.0.0.1/1/users/1',
        'user_name': 'David Qu',
        'url': 'http://127.0.0.1/marketplace/view_item/1'
    }, {
        'item_id': 2,
        'cat_title': 'Furniture',
        'item_title': 'Thing',
        'textbook_title': None,
        'item_price': Decimal('1.23'),
        'user_id': 3,
        'user_url': 'http://127.0.0.1/1/users/3',
        'user_name': 'Belac Sander',
        'url': 'http://127.0.0.1/marketplace/view_item/2'
    }]
    assert not helpers.generate_search_table({'cat_id': 2}, '')
    tables = helpers.generate_search_table({'cat_id': 1}, 'table')
    for item in tables:
        del item['item_timestamp']
    assert tables == [{
        'item_id': 1,
        'cat_title': 'Furniture',
        'item_title': 'A table',
        'textbook_title': None,
        'item_price': Decimal('5.99'),
        'user_id': 1,
        'textbook_author': None,
        'textbook_isbn': None,
        'user_url': 'http://127.0.0.1/1/users/1',
        'user_name': 'David Qu',
        'url': 'http://127.0.0.1/marketplace/view_item/1'
    }]
    assert helpers.create_new_listing({
        'user_id':
        3,
        'cat_id':
        2,
        'item_condition':
        'New',
        'item_details':
        None,
        'item_price':
        '.99',
        'textbook_id':
        helpers.add_textbook('Algebra', 'Serge Lang'),
        'textbook_edition':
        '3',
        'textbook_isbn':
        '9780387953854',
        'images': ['https://i.imgur.com/az1234.gif']
    }) == 3
    algebras = helpers.generate_search_table({}, 'algebra')
    for item in algebras:
        del item['item_timestamp']
    assert algebras == [{
        'item_id': 3,
        'cat_title': 'Textbooks',
        'item_title': 'Algebra',
        'textbook_title': 'Algebra',
        'item_price': Decimal('0.99'),
        'user_id': 3,
        'textbook_author': 'Serge Lang',
        'textbook_isbn': '9780387953854',
        'user_url': 'http://127.0.0.1/1/users/3',
        'user_name': 'Belac Sander',
        'url': 'http://127.0.0.1/marketplace/view_item/3'
    }]
    item = helpers.table_fetch(
        'marketplace_items', one=True, fields=None, attrs={'item_id': 3})
    del item['item_timestamp']
    assert item == {
        'item_id': 3,
        'cat_id': 2,
        'user_id': 3,
        'item_title': None,
        'item_details': None,
        'item_condition': 'New',
        'item_price': Decimal('0.99'),
        'item_active': 1,
        'textbook_id': 4,
        'textbook_edition': '3',
        'textbook_isbn': '9780387953854'
    }
    assert helpers.get_image_links(3) == ['https://i.imgur.com/az1234.gif']


def test_update_listing(client):
    helpers.update_current_listing(3, {
        'cat_id':
        1,
        'item_title':
        'A chair',
        'item_condition':
        'Terrible',
        'item_details':
        'Lots of deets',
        'item_price':
        '1.11',
        'images':
        ['https://i.imgur.com/new1.png', 'https://i.imgur.com/new2.jpg']
    })
    item = helpers.table_fetch(
        'marketplace_items', one=True, fields=None, attrs={'item_id': 3})
    del item['item_timestamp']
    assert item == {
        'item_id': 3,
        'cat_id': 1,
        'user_id': 3,
        'item_title': 'A chair',
        'item_details': 'Lots of deets',
        'item_condition': 'Terrible',
        'item_price': Decimal('1.11'),
        'item_active': 1,
        'textbook_id': None,
        'textbook_edition': None,
        'textbook_isbn': None
    }
    assert helpers.get_image_links(3) == [
        'https://i.imgur.com/new1.png', 'https://i.imgur.com/new2.jpg'
    ]
