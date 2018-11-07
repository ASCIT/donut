"""
Tests donut/modules/directory_search/
"""
from datetime import date
import flask
import pytest
from donut.testing.fixtures import client
from donut import app
import donut.modules.core.helpers as core_helpers
from donut.modules.directory_search import helpers
from donut.modules.directory_search import routes


#Helpers
def test_hidden_fields(client):
    user_id = helpers.get_user_id('csander')
    assert not helpers.get_hidden_fields('csander', user_id)
    #dqu should see all fields via admin priviledges
    assert not helpers.get_hidden_fields('dqu', user_id)
    assert helpers.get_hidden_fields('dtardif', user_id)
    assert helpers.get_hidden_fields(None, user_id)


def test_get_user(client):
    user_data = helpers.get_user(helpers.get_user_id('csander'))
    assert user_data == {
        'address':
        None,
        'birthday':
        date(1999, 5, 8),
        'building_name':
        'Ruddock House',
        'city':
        'Lincoln',
        'country':
        None,
        'email':
        'csander@caltech.edu',
        'entry_year':
        2017,
        'first_name':
        'Caleb',
        'gender':
        0,
        'gender_custom':
        'Male',
        'gender_string':
        'Male',
        'graduation_year':
        2021,
        'hometown_string':
        'Lincoln, MA',
        'houses': [{
            'group_name': 'Ruddock House',
            'pos_name': 'Full Member'
        }],
        'image':
        1,
        'last_name':
        'Sander',
        'middle_name':
        'Caldwell',
        'msc':
        707,
        'options': [{
            'option_name': 'CS',
            'option_type': 'Major'
        }, {
            'option_name': 'MechE',
            'option_type': 'Minor'
        }],
        'phone':
        '6178003347',
        'phone_string':
        '(617) 800-3347',
        'positions': [{
            'group_name': 'CRC',
            'pos_name': 'Lloyd'
        }],
        'preferred_name':
        'Cleb',
        'room':
        '203',
        'state':
        'MA',
        'uid':
        '2078141',
        'username':
        'csander',
        'zip':
        None
    }
    user_data2 = helpers.get_user(helpers.get_user_id('dqu'))
    assert user_data2['image'] == 0
    assert 'gender_string' not in user_data2
    assert not user_data2['hometown_string']
    assert 'phone_string' not in user_data2
    user_data3 = helpers.get_user(helpers.get_user_id('reng'))
    assert user_data3['phone_string'] == '+11234567890'
    assert helpers.get_user(0) is None


def test_name_query(client):
    assert helpers.get_users_by_name_query('ng') == [{
        'full_name':
        'Robert Eng',
        'user_id':
        2,
        'graduation_year':
        None
    }]
    assert helpers.get_users_by_name_query('eb cl san r') == [{
        'full_name':
        'Cleb Sander',
        'user_id':
        3,
        'graduation_year':
        2021
    }]
    assert helpers.get_users_by_name_query('x') == ()


def test_image(client):
    user_id = helpers.get_user_id('csander')
    assert helpers.get_image(user_id) == ('png', b'NOT_A_REAL_IMAGE')
    core_helpers.set_image(user_id, 'jpg', 'FAKE_JPG')
    assert helpers.get_image(user_id) == ('jpg', b'FAKE_JPG')
    with pytest.raises(Exception):
        helpers.get_image(helpers.get_user_id('dqu'))


def test_search(client):
    assert set(user['user_id']
               for user in helpers.execute_search(
                   email='',
                   username='',
                   name=None,
                   house_id=None,
                   option_id=None,
                   building_id=None,
                   grad_year=None,
                   state=None)) == set([1, 2, 3])
    assert set(user['user_id']
               for user in helpers.execute_search(
                   email='san',
                   username='',
                   name=None,
                   house_id=None,
                   option_id=None,
                   building_id=None,
                   grad_year=None,
                   state=None)) == set([3])
    assert set(user['user_id']
               for user in helpers.execute_search(
                   email='',
                   username='noone',
                   name=None,
                   house_id=None,
                   option_id=None,
                   building_id=None,
                   grad_year=None,
                   state=None)) == set()
    assert set(user['user_id']
               for user in helpers.execute_search(
                   email='',
                   username='q',
                   name=None,
                   house_id=None,
                   option_id=None,
                   building_id=None,
                   grad_year=None,
                   state=None)) == set([1])
    assert set(user['user_id']
               for user in helpers.execute_search(
                   email='',
                   username='noone',
                   name=None,
                   house_id=None,
                   option_id=None,
                   building_id=None,
                   grad_year=None,
                   state=None)) == set()
    assert set(user['user_id']
               for user in helpers.execute_search(
                   email='',
                   username='',
                   name='ER',
                   house_id=None,
                   option_id=None,
                   building_id=None,
                   grad_year=None,
                   state=None)) == set([2, 3])
    assert set(user['user_id']
               for user in helpers.execute_search(
                   email='',
                   username='',
                   name='abc',
                   house_id=None,
                   option_id=None,
                   building_id=None,
                   grad_year=None,
                   state=None)) == set()
    assert set(user['user_id']
               for user in helpers.execute_search(
                   email='',
                   username='',
                   name=None,
                   house_id=2,
                   option_id=None,
                   building_id=None,
                   grad_year=None,
                   state=None)) == set([3])
    assert set(user['user_id']
               for user in helpers.execute_search(
                   email='',
                   username='',
                   name=None,
                   house_id=100,
                   option_id=None,
                   building_id=None,
                   grad_year=None,
                   state=None)) == set()
    assert set(user['user_id']
               for user in helpers.execute_search(
                   email='',
                   username='',
                   name=None,
                   house_id=None,
                   option_id=1,
                   building_id=None,
                   grad_year=None,
                   state=None)) == set([3])
    assert set(user['user_id']
               for user in helpers.execute_search(
                   email='',
                   username='',
                   name=None,
                   house_id=None,
                   option_id=2,
                   building_id=None,
                   grad_year=None,
                   state=None)) == set([3])
    assert set(user['user_id']
               for user in helpers.execute_search(
                   email='',
                   username='',
                   name=None,
                   house_id=None,
                   option_id=100,
                   building_id=None,
                   grad_year=None,
                   state=None)) == set()
    assert set(user['user_id']
               for user in helpers.execute_search(
                   email='',
                   username='',
                   name=None,
                   house_id=None,
                   option_id=None,
                   building_id=1,
                   grad_year=None,
                   state=None)) == set([3])
    assert set(user['user_id']
               for user in helpers.execute_search(
                   email='',
                   username='',
                   name=None,
                   house_id=None,
                   option_id=None,
                   building_id=10,
                   grad_year=None,
                   state=None)) == set()
    assert set(user['user_id']
               for user in helpers.execute_search(
                   email='',
                   username='',
                   name=None,
                   house_id=None,
                   option_id=None,
                   building_id=None,
                   grad_year=2021,
                   state=None)) == set([3])
    assert set(user['user_id']
               for user in helpers.execute_search(
                   email='',
                   username='',
                   name=None,
                   house_id=None,
                   option_id=None,
                   building_id=None,
                   grad_year=2020,
                   state=None)) == set()
    assert set(user['user_id']
               for user in helpers.execute_search(
                   email='',
                   username='',
                   name=None,
                   house_id=None,
                   option_id=None,
                   building_id=None,
                   grad_year=None,
                   state='MA')) == set([3])
    assert set(user['user_id']
               for user in helpers.execute_search(
                   email='',
                   username='',
                   name=None,
                   house_id=None,
                   option_id=None,
                   building_id=None,
                   grad_year=None,
                   state='CA')) == set()


def test_value_lists(client):
    assert helpers.get_houses() == [{
        'group_id': 2,
        'group_name': 'Ruddock House'
    }]
    assert helpers.get_options() == [{
        'option_id': 1,
        'option_name': 'CS'
    }, {
        'option_id': 2,
        'option_name': 'MechE'
    }]
    assert helpers.get_grad_years() == [2021]
    assert helpers.get_states() == ['MA']


def test_preferred_name(client):
    user_id = helpers.get_user_id('csander')
    assert core_helpers.get_preferred_name(user_id) == 'Cleb'
    core_helpers.set_member_field(user_id, 'preferred_name', 'Belac')
    assert core_helpers.get_preferred_name(user_id) == 'Belac'
    assert core_helpers.get_preferred_name(helpers.get_user_id('reng')) == ''


def test_gender(client):
    user_id = helpers.get_user_id('csander')
    assert core_helpers.get_gender(user_id) == 'Male'
    core_helpers.set_member_field(user_id, 'gender_custom', 'new_gender')
    assert core_helpers.get_gender(user_id) == 'new_gender'
    assert core_helpers.get_gender(helpers.get_user_id('dqu')) == ''


#Routes
def test_search_page(client):
    assert client.get(
        flask.url_for('directory_search.directory_search')).status_code == 200


def test_my_page(client):
    with client.session_transaction() as sess:
        sess['username'] = 'csander'
    res = client.get(flask.url_for('core.my_directory_page'))
    assert res.status_code == 302
    assert res.headers['location'] == flask.url_for(
        'directory_search.view_user', user_id=3)


def test_view_user(client):
    assert client.get(flask.url_for('directory_search.view_user',
                                    user_id=3)).status_code == 200
    assert client.get(
        flask.url_for('directory_search.view_user',
                      user_id=100)).status_code == 200


def test_edit_page(client):
    with client.session_transaction() as sess:
        sess['username'] = 'csander'
    assert client.get(flask.url_for('core.edit_user')).status_code == 200


def test_set_name(client):
    with client.session_transaction() as sess:
        sess['username'] = 'csander'
    assert helpers.get_user(3)['preferred_name'] == 'Belac'
    res = client.post(flask.url_for('core.set_name'), data={'name': 'Clb'})
    assert res.status_code == 302
    assert res.headers['location'] == flask.url_for(
        'directory_search.view_user', user_id=3)
    assert helpers.get_user(3)['preferred_name'] == 'Clb'


def test_set_name(client):
    with client.session_transaction() as sess:
        sess['username'] = 'csander'
    assert helpers.get_user(3)['gender_string'] == 'new_gender'
    res = client.post(
        flask.url_for('core.set_gender'), data={'gender': 'Male'})
    assert res.status_code == 302
    assert res.headers['location'] == flask.url_for(
        'directory_search.view_user', user_id=3)
    assert helpers.get_user(3)['gender_string'] == 'Male'


def test_get_image(client):
    assert client.get(flask.url_for('directory_search.get_image',
                                    user_id=3)).status_code == 200
    with pytest.raises(Exception):
        client.get(flask.url_for('directory_search.get_image', user_id=1))


def test_name_search(client):
    assert client.get(
        flask.url_for('directory_search.search_by_name',
                      name_query='sander')).status_code == 200


def test_search(client):
    res = client.post(
        flask.url_for('directory_search.search'),
        data={
            'name': '',
            'house': '',
            'option': '',
            'residence': '',
            'graduation': '',
            'state': '',
            'username': '',
            'email': ''
        })
    assert res.status_code == 200  #3 results
    res = client.post(
        flask.url_for('directory_search.search'),
        data={
            'name': 'san',
            'house': '',
            'option': '',
            'residence': '',
            'graduation': '',
            'state': '',
            'username': '',
            'email': ''
        })
    assert res.status_code == 302
    assert res.headers['location'] == flask.url_for(
        'directory_search.view_user', user_id=3)
    res = client.post(
        flask.url_for('directory_search.search'),
        data={
            'name': '',
            'house': '2',
            'option': '',
            'residence': '',
            'graduation': '',
            'state': '',
            'username': '',
            'email': ''
        })
    assert res.status_code == 302
    assert res.headers['location'] == flask.url_for(
        'directory_search.view_user', user_id=3)
    res = client.post(
        flask.url_for('directory_search.search'),
        data={
            'name': '',
            'house': '100',
            'option': '',
            'residence': '',
            'graduation': '',
            'state': '',
            'username': '',
            'email': ''
        })
    assert res.status_code == 200  #no results
    res = client.post(
        flask.url_for('directory_search.search'),
        data={
            'name': '',
            'house': '',
            'option': '1',
            'residence': '',
            'graduation': '',
            'state': '',
            'username': '',
            'email': ''
        })
    assert res.status_code == 302
    assert res.headers['location'] == flask.url_for(
        'directory_search.view_user', user_id=3)
    res = client.post(
        flask.url_for('directory_search.search'),
        data={
            'name': '',
            'house': '',
            'option': '100',
            'residence': '',
            'graduation': '',
            'state': '',
            'username': '',
            'email': ''
        })
    assert res.status_code == 200  #no results
    res = client.post(
        flask.url_for('directory_search.search'),
        data={
            'name': '',
            'house': '',
            'option': '',
            'residence': '1',
            'graduation': '',
            'state': '',
            'username': '',
            'email': ''
        })
    assert res.status_code == 302
    assert res.headers['location'] == flask.url_for(
        'directory_search.view_user', user_id=3)
    res = client.post(
        flask.url_for('directory_search.search'),
        data={
            'name': '',
            'house': '',
            'option': '',
            'residence': '100',
            'graduation': '',
            'state': '',
            'username': '',
            'email': ''
        })
    assert res.status_code == 200  #no results
    res = client.post(
        flask.url_for('directory_search.search'),
        data={
            'name': '',
            'house': '',
            'option': '',
            'residence': '',
            'graduation': '2021',
            'state': '',
            'username': '',
            'email': ''
        })
    assert res.status_code == 302
    assert res.headers['location'] == flask.url_for(
        'directory_search.view_user', user_id=3)
    res = client.post(
        flask.url_for('directory_search.search'),
        data={
            'name': '',
            'house': '',
            'option': '',
            'residence': '',
            'graduation': '2019',
            'state': '',
            'username': '',
            'email': ''
        })
    assert res.status_code == 200  #no results
    res = client.post(
        flask.url_for('directory_search.search'),
        data={
            'name': '',
            'house': '',
            'option': '',
            'residence': '',
            'graduation': '',
            'state': 'MA',
            'username': '',
            'email': ''
        })
    assert res.status_code == 302
    assert res.headers['location'] == flask.url_for(
        'directory_search.view_user', user_id=3)
    res = client.post(
        flask.url_for('directory_search.search'),
        data={
            'name': '',
            'house': '',
            'option': '',
            'residence': '',
            'graduation': '',
            'state': 'IA',
            'username': '',
            'email': ''
        })
    assert res.status_code == 200  #no results
    res = client.post(
        flask.url_for('directory_search.search'),
        data={
            'name': '',
            'house': '',
            'option': '',
            'residence': '',
            'graduation': '',
            'state': '',
            'username': 'qu',
            'email': ''
        })
    assert res.status_code == 302
    assert res.headers['location'] == flask.url_for(
        'directory_search.view_user', user_id=1)
    res = client.post(
        flask.url_for('directory_search.search'),
        data={
            'name': '',
            'house': '',
            'option': '',
            'residence': '',
            'graduation': '',
            'state': '',
            'username': 'abc',
            'email': ''
        })
    assert res.status_code == 200  #no results
    res = client.post(
        flask.url_for('directory_search.search'),
        data={
            'name': '',
            'house': '',
            'option': '',
            'residence': '',
            'graduation': '',
            'state': '',
            'username': '',
            'email': 'reng'
        })
    assert res.status_code == 302
    assert res.headers['location'] == flask.url_for(
        'directory_search.view_user', user_id=2)
    res = client.post(
        flask.url_for('directory_search.search'),
        data={
            'name': '',
            'house': '',
            'option': '',
            'residence': '',
            'graduation': '',
            'state': '',
            'username': '',
            'email': 'xyz'
        })
    assert res.status_code == 200  #no results
