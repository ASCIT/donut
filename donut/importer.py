#!/usr/bin/env python
"""
Imports the Registrar Office's exports of current students for the
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
    "PHONE"
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
import sys

from donut.pymysql_connection import make_db

# -----------------------------------------
# GLOBALS
# -----------------------------------------

# Create reference to DB
db = make_db("dev")

# The following values are updated on duplicate keys:
# msc, preferred_name
# This were chosen because they're the only values that someone
# might have update with or be updated by the Registrar that
# warrant changing.
# Note to self: See if you can specify a nickname on new Donut
# and, if so, get rid of preferred_name from this update.
query = """
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
    ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
    ON DUPLICATE KEY UPDATE msc = msc, preferred_name = preferred_name
"""

# -----------------------------------------
# FUNCTIONS
# -----------------------------------------

def parse_data(file):
    # Begin parsing TSV data
    data_list = list(csv.reader(open(args.file, "rb"), delimiter="\t"))

    if len(data_list) < 1:
        raise Exception("There must at least exist headers in the file.")
        return

    users = {}
    
    # We assume that the first row is the headers as specified above
    headers = data_list[0]

    for i in range(1, len(data_list)):
        row = dict(zip(headers, data_list[i]))
        uid = row["UID"]
        
        if uid not in users:
            try:
                users[uid] = row
            except e:
                print("Error parsing student (ASCIT member)!", row, file=sys.stderr)
                print(e, file=sys.stderr)

    for user in users:
        add_user_to_db(user)


def add_user_to_db(user):
    with db.cursor() as cursor:
        cursor.execute(
                query,
                user["UID"],
                user["LAST_NAME"],
                user["FIRST_NAME"],
                user["NICK_NAME"],
                user["MIDDLE_NAME"],
                user["EMAIL"],
                user["PHONE"],
                user["GENDER"],
                user["BIRTH_DATE"],
                "",
                "",
                user["MSC"],
                ", ".join(filter(None, [user["LINE1"], user["LINE2"], user["LINE3"])),
                user["CITY"],
                user["STATE"],
                user["ZIP"],
                user["COUNTRY"])


if __name__ == "__main__":
    # Parse input arguments
    parser = argparse.ArgumentParser(description="Manages the importing of Registrar student data.")

    parser.add_argument("file",
                        help="Path to registrar file, e.g. ascit_190927.txt")
    args = parser.parse_args()

    parse_data(args.file)

