"""
Converts CSV files storing donut-legacy directory tables
into SQL insert statements
"""
import csv
from datetime import datetime
import os
import sys
sys.path.append('../../..')
from constants import MALE, FEMALE, NO_GENDER


def read_csv(table_name):
    with open(table_name + '.csv', encoding='latin-1') as csv_file:
        headers = None
        for row in csv.reader(csv_file):
            if headers is None:
                headers = row
                continue
            row_dict = {}
            for k, v in zip(headers, row):
                row_dict[k] = v
            yield row_dict


def escape_quote(string):
    return string.replace("\\", "\\\\").replace("'", "\\'")


with open('create_directory.sql', 'w') as sql_file:
    # Insert options
    options = {}  #map of option legacy ids to names
    for option in read_csv('undergrad_options'):
        name = option['name']
        options[option['id']] = name
        sql_file.writelines([
            "INSERT INTO options (option_name) SELECT * FROM (SELECT '" + name
            + "') AS tmp\n",
            "WHERE NOT EXISTS (SELECT * from options WHERE option_name = '" +
            name + "' LIMIT 1);\n"
        ])

    # Insert members
    members = {}  #map of inums to dicts of corresponding information
    for user in read_csv('inums'):
        first_middle_names = user['prename'].split(' ', 1)
        if len(first_middle_names) == 1:
            first_middle_names.append(None)
        first_name, middle_name = first_middle_names
        first_name = first_name.title()
        if middle_name is not None:
            middle_name = middle_name.title()
        members[user['inum']] = {
            'email': user['email'],
            'last_name': user['name'].title(),
            'first_name': first_name,
            'middle_name': middle_name
        }
    for user in read_csv('undergrads'):
        member = members[user['inum']]
        member['uid'] = user['uid']
        entry_year = user['entryear']
        member['entry_year'] = int(entry_year) if entry_year else None
        grad_year = user['gradyear']
        member['graduation_year'] = int(grad_year) if grad_year else None
    for user in read_csv(
            'directory_phones'
    ):  #legacy database doesn't appear to have more than 1 phone for any person
        member = members.get(user['inum'])
        if member is None:
            continue
        member['phone'] = user['phone']
    for user in read_csv('people'):
        member = members[user['inum']]
        member['gender'] = MALE if user['gender'] == 'm' else FEMALE if user[
            'gender'] == 'f' else NO_GENDER
        birthday = user['birthday']
        if birthday[
                -3:] == ' BC':  #not sure why someone's birthday is in 1987 BC
            birthday = birthday[:-3]
        member['birthday'] = birthday
    buildings = {}  #map of building IDs to names
    for building in read_csv('campus_buildings'):
        name = building['name']
        buildings[building['id']] = name
        sql_file.writelines([
            "INSERT INTO buildings (building_name) VALUES ('" +
            escape_quote(name) + "')\n",
            'ON DUPLICATE KEY UPDATE building_id = building_id;\n'
        ])
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
        keys = ''
        values = ''
        for key, value in member.items():
            if value is None:
                continue
            if keys:
                keys += ', '
                values += ', '
            keys += key
            value_type = type(value)
            if key is 'building_id':
                values += "(SELECT building_id FROM buildings WHERE building_name = '" + value + "' LIMIT 1)"
            elif value_type is str:
                values += "'" + escape_quote(value) + "'"
            elif value_type is int:
                values += str(value)
            else:
                raise Exception('Unexpected type: ' + str(value_type))
        sql_file.writelines([
            'INSERT INTO members (' + keys + ') VALUES (' + values + ')\n',
            'ON DUPLICATE KEY UPDATE uid = uid;\n'  #do nothing if member already exists
        ])
    for option_member in read_csv('undergrad_option_objectives'):
        member_uid = members[option_member['inum']]['uid']
        option_name = options[option_member['option_id']]
        sql_file.writelines([
            'INSERT INTO member_options (user_id, option_id, option_type) VALUES (\n',
            "    (SELECT user_id FROM members WHERE uid = '" + member_uid +
            "' LIMIT 1),\n",
            "    (SELECT option_id FROM options WHERE option_name = '" +
            option_name + "' LIMIT 1),\n", "    'Major'\n",
            ') ON DUPLICATE KEY UPDATE user_id=user_id;\n'
        ])

    # Insert house memberships
    houses = {}  #map of house IDs to names
    memberships_by_house = {
    }  #map of houses IDs to sets of membership type IDs
    for house in read_csv('hovses'):
        name = house['name'] + ' House'
        house_id = house['id']
        houses[house_id] = name
        sql_file.writelines([
            'INSERT INTO groups (group_name, type) VALUES\n',
            "    ('" + name + "', 'house')\n",
            "    ON DUPLICATE KEY UPDATE group_id=group_id;\n"
        ])
        memberships_by_house[house_id] = set()
    house_membership_types = {}  #map of membership type IDs to descriptions
    for house_membership_type in read_csv('hovse_membership_types'):
        house_membership_types[house_membership_type[
            'id']] = house_membership_type['description']
    for house_member in read_csv('hovse_members'):
        member_uid = members[house_member['inum']].get('uid')
        if member_uid is None:
            continue
        house_id = house_member['hovse_id']
        membership_type = house_member['membership_type']
        membership_name = house_membership_types[membership_type]
        house_memberships = memberships_by_house[house_id]
        house_name = houses[house_id]
        group_id_query = "(SELECT group_id FROM groups WHERE group_name = '" + house_name + "' LIMIT 1)"
        pos_id_query = "(SELECT pos_id FROM positions NATURAL JOIN groups WHERE group_name = '" + house_name + "' AND pos_name = '" + membership_name + "' LIMIT 1)"
        if membership_type not in house_memberships:
            house_memberships.add(membership_type)
            sql_file.writelines([
                'INSERT INTO positions (group_id, pos_name) SELECT * FROM (SELECT '
                + group_id_query + ", '" + membership_name + "') AS tmp\n",
                'WHERE NOT EXISTS ' + pos_id_query + ';\n'
            ])
        user_id_query = "(SELECT user_id FROM members WHERE uid = '" + member_uid + "' LIMIT 1)"
        sql_file.writelines([
            'INSERT INTO position_holders (group_id, pos_id, user_id) SELECT * FROM (SELECT'
            + group_id_query + ', ' + pos_id_query + ', ' + user_id_query +
            ') AS tmp\n',
            'WHERE NOT EXISTS (SELECT * FROM position_holders WHERE group_id = '
            + group_id_query + ' AND pos_id = ' + pos_id_query +
            ' AND user_id = ' + user_id_query + ');\n'
        ])
