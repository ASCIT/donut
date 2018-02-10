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
            name + "') LIMIT 1;\n"
        ])
    sql_file.write('\n')

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
        buildings[building['id']] = building['name']
    for address in read_csv('directory_campus_addresses'):
        member = members.get(address['inum'])
        if member is None:
            continue
        building = address['building']
        number = address['number']
        if building:  #residential address
            member['building'] = buildings[building]
            try:
                member['room_num'] = int(number)
            except ValueError:  #room number is not numeric
                pass
        else:  #MSC
            if not number:  #no address given
                continue
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
            if value_type is str:
                values += "'" + value.replace("\\", "\\\\").replace(
                    "'", "\\'") + "'"
            elif value_type is int:
                values += str(value)
            else:
                raise Exception('Unexpected type: ' + str(value_type))
        sql_file.writelines([
            'INSERT INTO members (' + keys + ') VALUES (' + values + ')\n',
            'ON DUPLICATE KEY UPDATE uid = uid;\n'  #do nothing if member already exists
        ])
    sql_file.write('\n')
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
