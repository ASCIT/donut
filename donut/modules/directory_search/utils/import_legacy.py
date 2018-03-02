#!/usr/bin/env python
"""
Converts CSV files storing donut-legacy directory tables
into SQL insert statements
"""
from datetime import datetime
import os
from donut.pymysql_connection import make_db
from donut.constants import MALE, FEMALE, NO_GENDER
from read_csv import read_csv


def escape_quote(string):
    return string.replace("\\", "\\\\").replace("'", "\\'")


db = make_db('dev')

# Insert options
members = {}  #map of inums to dicts of corresponding information
options = {}  #map of option legacy ids to names
for option in read_csv('undergrad_options'):
    name = option['name']
    options[option['id']] = name
    query = """
        INSERT INTO options (option_name) VALUES (%s)
        ON DUPLICATE KEY UPDATE option_id = option_id
    """
    with db.cursor() as cursor:
        cursor.execute(query, [name])

# Insert members
for user in read_csv('inums'):
    first_middle_names = user['prename'].split(' ', 1)
    if len(first_middle_names) == 1:
        first_middle_names.append('')
    first_name, middle_name = first_middle_names
    first_name = first_name.title()
    member = {
        'email': user['email'],
        'last_name': user['name'].title(),
        'first_name': first_name,
        'middle_name': middle_name
    }
    if middle_name:
        member['middle_name'] = middle_name.title()
    members[user['inum']] = member
for user in read_csv('undergrads'):
    member = members[user['inum']]
    member['uid'] = user['uid']
    entry_year = user['entryear']
    if entry_year:
        member['entry_year'] = int(entry_year)
    grad_year = user['gradyear']
    if grad_year:
        member['graduation_year'] = int(grad_year)
for user in read_csv('directory_phones'):
    member = members.get(user['inum'])
    if member is None:
        continue
    #legacy database doesn't appear to have more than 1 phone for any person
    member['phone'] = user['phone']
for user in read_csv('people'):
    member = members[user['inum']]
    member['gender'] = MALE if user['gender'] == 'm' else FEMALE if user[
        'gender'] == 'f' else NO_GENDER
    birthday = user['birthday']
    #not sure why someone's birthday is in 1987 BC
    if birthday.endswith(' BC'):
        birthday = birthday[:-3]
    member['birthday'] = birthday
buildings = {}  #map of building IDs to names
for building in read_csv('campus_buildings'):
    name = building['name']
    buildings[building['id']] = name
    query = """
        INSERT INTO buildings (building_name) VALUES (%s)
        ON DUPLICATE KEY UPDATE building_id = building_id
    """
    with db.cursor() as cursor:
        cursor.execute(query, [name])
for address in read_csv('directory_campus_addresses'):
    member = members.get(address['inum'])
    if member is None:
        continue
    building = address['building']
    number = address['number']
    if not number:  #no address given
        continue
    if building:  #residential address
        member['building_id'] = buildings[building]
        member['room'] = number
    else:  #MSC
        member['msc'] = int(number)
for address in read_csv('directory_addresses'):
    member = members.get(address['inum'])
    if member is None:
        continue
    member['address'] = address['address'].strip()
    member['city'] = address['city']
    member['state'] = address['state']
    member['zip'] = address['zip']
    country = address['country']
    if country:  #don't store USA
        member['country'] = country
for member in members.values():
    if 'uid' not in member:
        continue  #database requires UID
    keys = ''
    values = ''
    substitution_args = []
    for key, value in member.items():
        if value is None:
            continue
        if keys:
            keys += ', '
            values += ', '
        keys += key
        value_type = type(value)
        if key is 'building_id':
            values += '(SELECT building_id FROM buildings WHERE building_name = %s LIMIT 1)'
        elif value_type is str or value_type is int:
            values += '%s'
        else:
            raise Exception('Unexpected type: ' + str(value_type))
        substitution_args.append(value)
    query = 'INSERT INTO members (' + keys + ') VALUES (' + values + ') ON DUPLICATE KEY UPDATE user_id = user_id'
    with db.cursor() as cursor:
        cursor.execute(query, substitution_args)
for option_member in read_csv('undergrad_option_objectives'):
    uid = members[option_member['inum']]['uid']
    option_name = options[option_member['option_id']]
    query = """
        INSERT INTO member_options (user_id, option_id, option_type) VALUES (
            (SELECT user_id FROM members WHERE uid = %s LIMIT 1),
            (SELECT option_id FROM options WHERE option_name = %s LIMIT 1),
            'Major'
        ) ON DUPLICATE KEY UPDATE user_id = user_id
    """
    with db.cursor() as cursor:
        cursor.execute(query, [uid, option_name])

# Insert house memberships
houses = {}  #map of house IDs to names
#map of houses IDs to sets of membership type IDs
memberships_by_house = {}
for house in read_csv('hovses'):
    name = house['name'] + ' House'
    house_id = house['id']
    houses[house_id] = name
    query = """
        INSERT INTO groups (group_name, type) VALUES (%s, 'house')
        ON DUPLICATE KEY UPDATE group_id = group_id
    """
    with db.cursor() as cursor:
        cursor.execute(query, [name])
    memberships_by_house[house_id] = set()
house_membership_types = {
    house_membership_type['id']: house_membership_type['description']
    for house_membership_type in read_csv('hovse_membership_types')
}
for house_member in read_csv('hovse_members'):
    uid = members[house_member['inum']].get('uid')
    if uid is None:
        continue
    house_id = house_member['hovse_id']
    membership_type = house_member['membership_type']
    membership_name = house_membership_types[membership_type]
    house_memberships = memberships_by_house[house_id]
    house_name = houses[house_id]
    group_id_query = '(SELECT group_id FROM groups WHERE group_name = %s LIMIT 1)'
    group_id_args = [house_name]
    pos_id_query = '(SELECT pos_id FROM positions NATURAL JOIN groups WHERE group_name = %s AND pos_name = %s LIMIT 1)'
    pos_id_args = [house_name, membership_name]
    if membership_type not in house_memberships:
        house_memberships.add(membership_type)
        query = 'INSERT INTO positions (group_id, pos_name) SELECT * FROM (SELECT ' + group_id_query + ', %s) as tmp\n'
        query += 'WHERE NOT EXISTS ' + pos_id_query
        with db.cursor() as cursor:
            cursor.execute(query, pos_id_args * 2)
    user_id_query = '(SELECT user_id FROM members WHERE uid = %s LIMIT 1)'
    user_id_args = [uid]
    query = 'INSERT INTO position_holders (group_id, pos_id, user_id)\n'
    query += 'SELECT * FROM (SELECT ' + group_id_query + ', ' + pos_id_query + ', ' + user_id_query + ') as tmp\n'
    query += 'WHERE NOT EXISTS (SELECT * FROM position_holders WHERE group_id = ' + group_id_query + ' AND pos_id = ' + pos_id_query + ' AND user_id = ' + user_id_query + ')'
    with db.cursor() as cursor:
        cursor.execute(query,
                        (group_id_args + pos_id_args + user_id_args) * 2)

#Import images
os.system('rm -r images 2> /dev/null')
os.system("""
    unzip images.zip -d images_tmp > /dev/null &&
    mv images_tmp/home/demo/www/id_photo images &&
    rm -r images_tmp
""")
image_files = {image['id']: image['file'] for image in read_csv('images')}
for inum_image in read_csv('image_inums'):
    uid = members.get(inum_image['inum'], {}).get('uid')
    if uid is None:
        continue
    file = image_files[inum_image['image_id']]
    extension = file.split('.')[-1]
    try:
        with open('images/' + file, 'rb') as image_file:
            contents = image_file.read()
    except FileNotFoundError:
        continue
    query = """
        INSERT INTO images (user_id, extension, image)
        VALUES ((SELECT user_id FROM members WHERE uid = %s LIMIT 1), %s, %s)
        ON DUPLICATE KEY UPDATE user_id = user_id
    """
    with db.cursor() as cursor:
        cursor.execute(query, [uid, extension, contents])
