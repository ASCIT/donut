from donut.testing.fixtures import client
from donut import app
from donut.modules.marketplace.helpers import (get_category_name_from_id,
                                               get_table_columns,
                                               get_matches,
                                               tokenize_query)


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
