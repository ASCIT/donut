#!/usr/bin/env python
"""
Imports the Registrar Office"s exports of current students for the
year. This adds in new students for the moment, and does not remove
graduated students.

The CSV parser expects the file to be tab delimited with the following
columns, where row values can all be imported as strings:
    "FULL_NAME"
    "LAST_NAME"
    "FIRST_NAME"
    "MIDDLE_NAME"
    "GENDER"
    "UID"
    "BIRTH_DATE"
    "OPTION"
    "OPTION2"
    "YOS"
    "MSC"
    "PHONE_NUMBER"
    "EMAIL"
    "LINE1" -- note that LINEs forms an address
    "LINE2"
    "LINE3"
    "CITY"
    "STATE"
    "ZIP"
    "COUNTRY"
    "HOUSE_AFFILIATION_1"
    "HOUSE_AFFILIATION_2"
    "HOUSE_AFFILIATION_3"
    "NICK_NAME"
"""

import argparse
import csv
from datetime import date, datetime
import re

from donut.constants import Gender
from donut.pymysql_connection import make_db

MSC_MATCH = r"MSC (\d+)"

today = date.today()
# Compute the start of the current academic year.
# This is the last calendar year if the script is run between December and June.
year_start = today.year - (1 if today.month < 7 else 0)
graduation_years = {
    "Senior": year_start + 1,
    "Junior": year_start + 2,
    "Sophomore": year_start + 3,
    "Freshman": year_start + 4,
    "UGrad Exchange": year_start + 1
}

get_options_query = "SELECT * FROM options"
get_house_poss_query = """
    SELECT group_name, pos_id
    FROM group_houses NATURAL JOIN positions
    WHERE pos_name = 'Full Member'
"""
# The following values are updated on duplicate keys:
# msc, preferred_name
# This were chosen because they"re the only values that someone
# might have update with or be updated by the Registrar that
# warrant changing.
# Note to self: See if you can specify a nickname on new Donut
# and, if so, get rid of preferred_name from this update.
insert_member_query = """
    INSERT INTO members (
        uid,
        last_name,
        first_name,
        preferred_name,
        middle_name,
        email,
        phone,
        gender,
        birthday,
        entry_year,
        graduation_year,
        msc,
        address,
        city,
        state,
        zip,
        country
    ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
    ON DUPLICATE KEY UPDATE
        msc = msc,
        preferred_name = preferred_name,
        graduation_year = graduation_year
"""
get_user_id_query = "SELECT user_id FROM members WHERE uid = %s"
add_option_query = "INSERT INTO options(option_name) VALUES (%s)"
delete_options_query = "DELETE FROM member_options WHERE user_id = %s"
insert_option_query = """
    INSERT INTO member_options(user_id, option_id, option_type)
    VALUES (%s, %s, 'Major')
"""
get_house_membership_query = """
    SELECT hold_id FROM position_holders WHERE user_id = %s AND pos_id = %s
"""
add_house_membership_query = """
    INSERT INTO position_holders (user_id, pos_id) VALUES (%s, %s)
"""
end_house_membership_query = """
    DELETE FROM position_holders WHERE user_id = %s AND pos_id IN
"""


def import_file(env, file):
    # Create reference to DB
    db = make_db(env)
    try:
        db.begin()
        with db.cursor() as cursor:
            option_ids = get_option_ids(cursor)
            house_pos_ids = get_house_pos_ids(cursor)

            # Read the TSV row-by-row TSV data
            with open(file, encoding="latin-1", newline="") as tsv_file:
                headers = None
                for row in csv.reader(tsv_file, delimiter="\t"):
                    if headers is None:
                        headers = row
                        continue

                    row_dict = dict(zip(headers, row))
                    add_user_to_db(cursor, row_dict, option_ids, house_pos_ids)
        db.commit()
    finally:
        db.close()


def get_option_ids(cursor):
    cursor.execute(get_options_query)
    return {
        option["option_name"]: option["option_id"]
        for option in cursor.fetchall()
    }


def get_house_pos_ids(cursor):
    cursor.execute(get_house_poss_query)
    return {
        house["group_name"]: house["pos_id"]
        for house in cursor.fetchall()
    }


def add_user_to_db(cursor, student, option_ids, house_pos_ids):
    # Insert into members table
    uid = student["UID"]
    print('UID', uid)
    first_name = student["FIRST_NAME"]
    nick_name = student["NICK_NAME"]
    graduation_year = graduation_years.get(student["YOS"])
    if not graduation_year:
        raise Exception("Unknown YOS: " + student["YOS"])
    address = ", ".join(
        line for line in (student["LINE1"], student["LINE2"], student["LINE3"])
        if line)
    cursor.execute(insert_member_query, (
        uid,
        student["LAST_NAME"],
        first_name,
        nick_name if nick_name and nick_name != first_name else None,
        student["MIDDLE_NAME"] or None,
        student["EMAIL"],
        student["PHONE_NUMBER"] or None,
        parse_gender(student["GENDER"]),
        parse_date(student["BIRTH_DATE"]),
        year_start,
        graduation_year,
        parse_msc(student["MSC"]),
        address or None,
        student["CITY"] or None,
        student["STATE"] or None,
        student["ZIP"] or None,
        student["COUNTRY"] or None, ))

    # Update options
    cursor.execute(get_user_id_query, uid)
    user_id = cursor.fetchone()["user_id"]
    cursor.execute(delete_options_query, user_id)
    for option in (student["OPTION"], student["OPTION2"]):
        if option and option != "Undeclared":
            option_id = option_ids.get(option)
            if not option_id:
                cursor.execute(add_option_query, option)
                option_id = cursor.lastrowid
                option_ids[option] = option_id
            cursor.execute(insert_option_query, (user_id, option_id))

    # Update house memberships
    # TODO: use start and end dates to determine if position is active
    house = student["HOUSE_AFFILIATION_1"]  # 2 and 3 appear unpopulated
    if house and house != "Unaffiliated":
        pos_id = house_pos_ids.get(house)
        if not pos_id:
            raise Exception("Unknown house: " + house)
        cursor.execute(get_house_membership_query, (user_id, pos_id))
        if not cursor.fetchone():
            cursor.execute(add_house_membership_query, (user_id, pos_id))
    else:
        position_ids = ", ".join(str(id) for id in house_pos_ids.values())
        cursor.execute(end_house_membership_query + " (" + position_ids + ")",
                       user_id)


parse_gender = lambda gender: \
    Gender.MALE.value if gender == "M" else \
        Gender.FEMALE.value if gender == "F" else None
parse_date = lambda date: datetime.strptime(date, "%d-%b-%Y").date()


def parse_msc(msc):
    match = re.fullmatch(MSC_MATCH, msc)
    return match and match[1]


if __name__ == "__main__":
    # Parse input arguments
    parser = argparse.ArgumentParser(
        description="Imports a list of students exported by the registrar")
    parser.add_argument(
        "-e", "--env", default="dev", help="Database to update")
    parser.add_argument(
        "file", help="Path to registrar file, e.g. ascit_190927.txt")
    args = parser.parse_args()

    import_file(args.env, args.file)
