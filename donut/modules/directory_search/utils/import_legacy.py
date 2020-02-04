#!/usr/bin/env python
"""
Converts CSV files storing donut-legacy directory tables
into SQL insert statements
"""
import argparse
from csv import reader
from datetime import datetime
import os
from donut.pymysql_connection import make_db
from donut.constants import Gender


def read_csv(table_name):
    """
    Reads a CSV file containing an exported legacy table
    as a list of dicts mapping column names to string values
    """
    print('Importing', table_name)
    with open(table_name + '.csv', encoding='latin-1') as csv_file:
        headers = None
        for row in reader(csv_file):
            if headers is None:
                headers = row
                continue

            yield dict(zip(headers, row))


def escape_quote(string):
    return string.replace("\\", "\\\\").replace("'", "\\'")

get_gender = lambda gender_string: \
    Gender.MALE if gender_string == 'm' else \
    Gender.FEMALE if gender_string == 'f' else \
    None


def import_tables(db):
    members = read_inums()
    read_undergrads(members)
    read_phones(members)
    read_people(members)
    read_home_addresses(members)
    buildings = import_buildings(db)
    read_campus_addresses(members, buildings)
    import_members(db, members)

    options = import_options(db)
    import_member_options(db, members, options)

    houses = import_houses(db)
    membership_types = read_membership_types()
    import_memberships(db, members, houses, membership_types)

    import_images(db, members)


def read_inums():
    members = {}  # map of inums to dicts of corresponding information
    for user in read_csv('inums'):
        first_middle_names = user['prename'].split(' ', 1)
        if len(first_middle_names) == 1:
            first_middle_names.append('')
        first_name, middle_name = first_middle_names
        members[user['inum']] = {
            'email': user['email'],
            'last_name': user['name'].title(),
            'first_name': first_name.title(),
            'middle_name': middle_name.title()
        }
    return members


def read_undergrads(members):
    missing = set(members)
    for user in read_csv('undergrads'):
        inum = user['inum']
        member = members[inum]
        member['uid'] = user['uid']
        entry_year = user['entryear']
        if entry_year:
            member['entry_year'] = int(entry_year)
        grad_year = user['gradyear']
        if grad_year:
            member['graduation_year'] = int(grad_year)
        missing.remove(inum)

    # Members without a UID cannot be inserted into the database
    for inum in missing:
        del members[inum]


def read_phones(members):
    for user in read_csv('directory_phones'):
        member = members.get(user['inum'])
        if member is None:
            continue

        # Legacy database doesn't appear to have more than 1 phone for any person
        member['phone'] = user['phone']


def read_people(members):
    for user in read_csv('people'):
        member = members.get(user['inum'])
        if member is None:
            continue

        gender = get_gender(user['gender'])
        if gender:
            member['gender'] = gender.value
        birthday = user['birthday']
        # Not sure why someone's birthday is in 1987 BC
        if birthday.endswith(' BC'):
            birthday = birthday[:-3]
        member['birthday'] = birthday


def read_home_addresses(members):
    for address in read_csv('directory_addresses'):
        member = members.get(address['inum'])
        if member is None:
            continue

        member['address'] = address['address'].strip()
        member['city'] = address['city']
        member['state'] = address['state']
        member['zip'] = address['zip']
        country = address['country']
        if country:  # don't store USA
            member['country'] = country


def import_buildings(db):
    query = 'INSERT INTO buildings (building_name) VALUES (%s)'
    buildings = {}  # map of legacy building IDs to new IDs
    building_names = {}  # map of building names to new IDs
    for building in read_csv('campus_buildings'):
        old_id = building['id']
        name = building['name']
        new_id = building_names.get(name)
        if new_id:
            # Some buildings share the same name in legacy database
            buildings[old_id] = new_id
            continue

        with db.cursor() as cursor:
            cursor.execute(query, name)
            new_id = cursor.lastrowid
            buildings[old_id] = new_id
            building_names[name] = new_id
    return buildings


def read_campus_addresses(members, buildings):
    for address in read_csv('directory_campus_addresses'):
        member = members.get(address['inum'])
        if member is None:
            continue

        building = address['building']
        number = address['number']
        if not number:  # no address given
            continue

        if building:  # residential address
            member['building_id'] = buildings[building]
            member['room'] = number
        else:  # MSC
            member['msc'] = int(number)


def import_members(db, members):
    for member in members.values():
        for value in member.values():
            value_type = type(value)
            if value_type not in (str, int):
                raise Exception('Unexpected type: ' + str(value_type))

        keys = ', '.join(member)
        values = ', '.join('%s' for key in member)
        query = 'INSERT INTO members (' + keys + ') VALUES (' + values + ')'
        with db.cursor() as cursor:
            cursor.execute(query, tuple(member.values()))
            member['user_id'] = cursor.lastrowid


def import_options(db):
    query = 'INSERT INTO options (option_name) VALUES (%s)'
    options = {}  # map of legacy option IDs to new IDs
    for option in read_csv('undergrad_options'):
        with db.cursor() as cursor:
            cursor.execute(query, option['name'])
            options[option['id']] = cursor.lastrowid
    return options


def import_member_options(db, members, options):
    query = """
        INSERT INTO member_options (user_id, option_id, option_type)
        VALUES (%s, %s, 'Major')
    """
    for option_member in read_csv('undergrad_option_objectives'):
        user_id = members[option_member['inum']]['user_id']
        option_id = options[option_member['option_id']]
        with db.cursor() as cursor:
            cursor.execute(query, (user_id, option_id))


def import_houses(db):
    query = "INSERT INTO groups (group_name, type) VALUES (%s, 'house')"
    houses = {}  # map of legacy house IDs to new IDs
    for house in read_csv('hovses'):
        with db.cursor() as cursor:
            cursor.execute(query, house['name'] + ' House')
            houses[house['id']] = cursor.lastrowid
    return houses


read_membership_types = lambda: {
    membership_type['id']: membership_type['description']
    for membership_type in read_csv('hovse_membership_types')
}


def import_memberships(db, members, houses, membership_types):
    group_query = 'SELECT group_id FROM groups WHERE group_name = %s LIMIT 1'
    position_query = """
        SELECT pos_id FROM positions
        WHERE group_id = %s AND pos_name = %s LIMIT 1
    """
    insert_position_query = 'INSERT INTO positions (group_id, pos_name) VALUES (%s, %s)'
    query = 'INSERT INTO position_holders (pos_id, user_id) VALUES (%s, %s)'

    # Cache membership position IDs
    pos_ids = {}

    def get_pos_id(group_id, membership_name):
        position_key = (group_id, membership_name)
        pos_id = pos_ids.get(position_key)
        if not pos_id:
            with db.cursor() as cursor:
                # Add new membership position
                cursor.execute(insert_position_query, position_key)
                pos_id = cursor.lastrowid
            pos_ids[position_key] = pos_id
        return pos_id

    for house_member in read_csv('hovse_members'):
        member = members.get(house_member['inum'])
        if member is None:
            continue

        house_id = house_member['hovse_id']
        membership_type = house_member['membership_type']
        pos_id = get_pos_id(houses[house_id],
                            membership_types[membership_type])
        with db.cursor() as cursor:
            cursor.execute(query, (pos_id, member['user_id']))


def import_images(db, members):
    # The legacy database has duplicate images; we take the latest one
    query = """
        INSERT INTO images (user_id, extension, image) VALUES (%s, %s, %s)
        ON DUPLICATE KEY UPDATE image = image
    """
    os.system("""
        unzip images.zip -d images_tmp > /dev/null &&
        mv images_tmp/home/demo/www/id_photo images &&
        rm -r images_tmp
    """)
    image_files = {image['id']: image['file'] for image in read_csv('images')}
    for inum_image in read_csv('image_inums'):
        member = members.get(inum_image['inum'])
        if member is None:
            continue

        file = image_files[inum_image['image_id']]
        extension = file.split('.')[-1]
        try:
            with open('images/' + file, 'rb') as image_file:
                contents = image_file.read()
        except FileNotFoundError:
            continue

        with db.cursor() as cursor:
            cursor.execute(query, (member['user_id'], extension, contents))
    os.system('rm -r images')


if __name__ == '__main__':
    # Parse input arguments
    parser = argparse.ArgumentParser(
        description='Imports tables exported from the legacy database')
    parser.add_argument(
        '-e', '--env', default='dev', help='Database to update')
    args = parser.parse_args()

    db = make_db(args.env)
    try:
        db.begin()
        import_tables(db)
        db.commit()
    finally:
        db.close()
