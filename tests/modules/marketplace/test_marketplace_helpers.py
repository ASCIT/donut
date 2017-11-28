from donut.testing.fixtures import client
from donut import app
from donut.modules.marketplace.helpers import (
    get_category_name_from_id, get_table_columns, get_matches, tokenize_query,
    validate_isbn, process_edition, add_textbook)
import sqlalchemy, flask


def test_get_category_name_from_id(client):
    cat_name = get_category_name_from_id(1)
    assert cat_name == 'Furniture'


def test_get_table_columns(client):
    table_columns = get_table_columns('marketplace_categories')
    assert table_columns == ['cat_id', 'cat_title', 'cat_active', 'cat_order']

    table_columns = get_table_columns(
        ['marketplace_categories', 'marketplace_items'])
    assert table_columns == [
        'cat_id', 'cat_title', 'cat_active', 'cat_order', 'item_id', 'cat_id',
        'user_id', 'item_title', 'item_details', 'item_condition',
        'item_price', 'item_timestamp', 'item_active', 'textbook_id',
        'textbook_edition', 'textbook_isbn'
    ]


def test_get_matches(client):
    l1 = [1, 2, 3, 4]
    l2 = [4, 3]
    assert get_matches(l1, l2) == 2
    assert get_matches(l2, l1) == 2
    assert get_matches(l1, l1) == 4
    l3 = []
    assert get_matches(l3, l3) == 0


def test_tokenize_query(client):
    query = "and,if great testing testing ,.,..,/./,/,./,./,"
    assert tokenize_query(query) == ['great', 'testing', 'testing']


def test_validate_isbn(client):
    assert validate_isbn("978-1-60309-419-1") == True
    assert validate_isbn("9971-5-0210-0") == True
    assert validate_isbn("0-8044-2957-X") == True
    assert validate_isbn("0-9752298-0-X") == True
    assert validate_isbn("978-3-16-148410-0") == True

    assert validate_isbn("978-1-60309-419-0") == False
    assert validate_isbn("9971-5-0210-X") == False
    assert validate_isbn("0-8044-2957-1") == False
    assert validate_isbn("0-9752298-0-2") == False
    assert validate_isbn("978-3-16-148400-0") == False


def test_process_edition(client):
    assert process_edition(1.0) == "1st"
    assert process_edition(2.0) == "2nd"
    assert process_edition(3.0) == "3rd"
    assert process_edition(4.0) == "4th"
    assert process_edition(5.0) == "5th"
    assert process_edition(6.0) == "6th"
    assert process_edition(7.0) == "7th"
    assert process_edition(8.0) == "8th"
    assert process_edition(9.0) == "9th"
    assert process_edition(10.0) == "10th"
    assert process_edition(2017.0) == "2017"
    assert process_edition("hello") == "hello"


def count_textbooks():
    query = sqlalchemy.sql.text("SELECT COUNT(*) FROM marketplace_textbooks")
    result = list(flask.g.db.execute(query))
    return result[0][0]


def test_add_textbook(client):
    num_textbooks_begin = count_textbooks()
    textbooks_added_successfully = 0

    if add_textbook("title", "author"):
        textbooks_added_successfully += 1
    if add_textbook("title2", "author"):
        textbooks_added_successfully += 1
    if add_textbook("title", "author2"):
        textbooks_added_successfully += 1

    assert add_textbook("title", "author") == False

    num_textbooks_end = count_textbooks()
    assert (num_textbooks_end -
            num_textbooks_begin) == textbooks_added_successfully
