from donut.testing.fixtures import client
from donut import app
from donut.modules.marketplace.helpers import (get_category_name_from_id,
                                               get_table_columns)


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
