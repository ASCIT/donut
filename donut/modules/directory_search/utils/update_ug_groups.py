#!/usr/bin/env python
"""
Updates ug and ug-GRADYEAR groups based on the members table.
"""

import argparse
from datetime import date

from donut.pymysql_connection import make_db

today = date.today()
# Compute the start of the current academic year.
# This is the next calendar year if the script is run between July and December.
year_end = today.year + (1 if today.month > 6 else 0)


def update_ug_groups(env):
    db = make_db(env)
    try:
        db.begin()
        with db.cursor() as cursor:
            ug_group = get_ug_group(cursor)
            ug_type = ug_group['type']
            ug_pos_id = ug_group['pos_id']
            ug_admin_positions = get_ug_admin_positions(cursor)

            remove_ug_group_members(cursor, ug_pos_id)
            remove_ug_year_groups(cursor)
            add_ug_group_members(cursor, ug_pos_id)
            pos_ids = make_ug_year_groups(cursor, ug_type, ug_admin_positions)
            add_ug_year_members(cursor, pos_ids)
        db.commit()
    finally:
        db.close()


def get_ug_group(cursor):
    query = """
        SELECT type, pos_id
        FROM groups NATURAL JOIN positions
        WHERE group_name = 'ug' AND pos_name = 'Member'
    """
    cursor.execute(query)
    ug_group = cursor.fetchone()
    if ug_group is None:
        raise Exception('"ug" group/position not found')

    return ug_group


def get_ug_admin_positions(cursor):
    query = """
        SELECT pos_id_from
        FROM position_relations JOIN positions ON pos_id_to = pos_id NATURAL JOIN groups
        WHERE group_name = 'ug' AND pos_name = 'Admin'
    """
    cursor.execute(query)
    return [relation['pos_id_from'] for relation in cursor.fetchall()]


def remove_ug_group_members(cursor, ug_pos_id):
    cursor.execute('DELETE FROM position_holders WHERE pos_id = %s', ug_pos_id)


def remove_ug_year_groups(cursor):
    cursor.execute("DELETE FROM groups WHERE group_name LIKE 'ug-%'")


def add_ug_group_members(cursor, ug_pos_id):
    query = """
        INSERT INTO position_holders(pos_id, user_id)
        SELECT %s, user_id FROM members WHERE graduation_year >= %s
    """
    members = cursor.execute(query, (ug_pos_id, year_end))
    print('Added', members, 'undergrads to ug')


def make_ug_year_groups(cursor, group_type, ug_admin_positions):
    get_years_query = """
        SELECT DISTINCT graduation_year
        FROM members WHERE graduation_year >= %s
    """
    make_group_query = """
        INSERT INTO groups(group_name, group_desc, type, newsgroups)
        VALUES (%s, %s, %s, TRUE)
    """
    make_position_query = """
        INSERT INTO positions(group_id, pos_name)
        VALUES (%s, 'Member')
    """
    make_admin_position_query = """
        INSERT INTO positions(group_id, pos_name, send, control, receive)
        VALUES (%s, 'Admin', TRUE, TRUE, FALSE)
    """
    add_admin_relation_query = """
        INSERT INTO position_relations(pos_id_from, pos_id_to) VALUES (%s, %s)
    """

    pos_ids = {}
    cursor.execute(get_years_query, year_end)
    for graduation_year in cursor.fetchall():
        year = graduation_year['graduation_year']
        year_str = str(year)
        group_name = 'ug-' + year_str
        group_desc = 'Undergrads graduating in ' + year_str
        cursor.execute(make_group_query, (group_name, group_desc, group_type))
        group_id = cursor.lastrowid
        cursor.execute(make_position_query, group_id)
        pos_ids[year] = cursor.lastrowid
        cursor.execute(make_admin_position_query, group_id)
        admin_pos_id = cursor.lastrowid
        for pos_id in ug_admin_positions:
            cursor.execute(add_admin_relation_query, (pos_id, admin_pos_id))
        print('Created group', group_name)
    return pos_ids


def add_ug_year_members(cursor, pos_ids):
    query = """
        INSERT INTO position_holders(pos_id, user_id)
        SELECT %s, user_id FROM members WHERE graduation_year = %s
    """
    for year, pos_id in pos_ids.items():
        members = cursor.execute(query, (pos_id, year))
        print('Added', members, 'undergrads to ug-' + str(year))


if __name__ == '__main__':
    parser = argparse.ArgumentParser(
        description=
        'Updates ug and ug-GRADYEAR groups based on the members table')
    parser.add_argument(
        '-e', '--env', default='dev', help='Database to update (default dev)')
    args = parser.parse_args()

    update_ug_groups(args.env)
