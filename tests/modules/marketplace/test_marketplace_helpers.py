from donut.modules.marketplace.helpers import *
import donut

def test_get_category_name_from_id():
    donut.init('test')
    donut.before_request()
    cat_name = get_category_name_from_id(1)
    donut.teardown_request(None)
    assert cat_name == 'Furniture'

