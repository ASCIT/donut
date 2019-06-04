from donut.testing.fixtures import client
from donut import app
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

    assert not helpers.validate_isbn("978-1-60309-419-0")
    assert not helpers.validate_isbn("9971-5-0210-X")
    assert not helpers.validate_isbn("0-8044-2957-1")
    assert not helpers.validate_isbn("0-9752298-0-2")
    assert not helpers.validate_isbn("978-3-16-148400-0")


def test_process_edition(client):
    assert helpers.process_edition(1.0) == "1st"
    assert helpers.process_edition(2.0) == "2nd"
    assert helpers.process_edition(3.0) == "3rd"
    assert helpers.process_edition(4.0) == "4th"
    assert helpers.process_edition(5.0) == "5th"
    assert helpers.process_edition(6.0) == "6th"
    assert helpers.process_edition(7.0) == "7th"
    assert helpers.process_edition(8.0) == "8th"
    assert helpers.process_edition(9.0) == "9th"
    assert helpers.process_edition(10.0) == "10th"
    assert helpers.process_edition(2017.0) == "2017"
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
