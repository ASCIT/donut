#!usr/bin/env python

"""
Registrar student data upload script.

Args:
    filename: registrar provided file of new students
    database: select "dev" or "prod" database
    -v: increase output verbosity

Written by Michael Huynh
July 05, 2017
"""

import argparse, re, datetime, db
from sqlalchemy.sql import text

# set up argument parser
def parse_args():
    """
    Set up the argument parser and parse all input arguments.
    """
    global verbose
    parser = argparse.ArgumentParser()
    parser.add_argument("filename",
        help="registrar provided file of new students")
    parser.add_argument("database", choices=["dev", "prod"],
        help="select dev or prod database")
    parser.add_argument("-v", "--verbose", help="increase output verbosity",
        action="store_true")
    args = parser.parse_args()
    return args

# parse the registrar provided file
def parse_file(filename, verbose = False):
    """
    Parse the file and return an array of member objects, representing the new
    members.
    """
    with open(filename) as registrar_file:
        if verbose:
            print "Loaded file \"" + args.filename + "\""
        print registrar_file.readline()
        do_skip_first_line = raw_input("Is this line a formatting line? [y/n] ")
        while not (do_skip_first_line == "y" or do_skip_first_line == "n"):
            print "Unrecognized command {}.".format(do_skip_first_line)
            do_skip_first_line = raw_input(
                "Is this line a formatting line? [y/n] "
            )
        if do_skip_first_line == "n":
            registrar_file.seek(0)
        parsed_data = []
        for raw_line in registrar_file:
            # use regex to get all entries from between quotes
            parsed_line = [None if entry == "" else entry
                for entry in re.findall(r"\"(.*?)\"", raw_line)]
            # instanciate a new member
            new_member = {
                "last_name": parsed_line[1],
                "first_name": parsed_line[2],
                "middle_name": parsed_line[3],
                "uid": parsed_line[4],
                "gender": 0 if parsed_line[5] == "M" else 1,
                "birthday": datetime.datetime
                    .strptime(parsed_line[6].lower(), "%d-%b-%Y").date(),
                "msc": int(re.findall(r"\d+", parsed_line[10])[0]),
                "phone": parsed_line[11],
                "email": parsed_line[12],
                "address": "".join(["" if line == None else line for line in
                    parsed_line[13:15]]),
                "city": parsed_line[16],
                "state": parsed_line[17],
                "zip": parsed_line[18],
                "country": "United States" if parsed_line[19] == None
                    else parsed_line[19]
            }
            parsed_data.append(new_member)
        if verbose:
            print "Loaded and parsed {} students.".format(len(parsed_data))
        return parsed_data
    
# connect to the desired database
def upload_to_db(member_data, database, verbose = False):
    """
    Establish a connection to the desired database and upload student data to
    it. Data is an array of member objects, where each member object is a
    member parsed from the registrar file.
    """
    if verbose:
        print "Connecting to \"{}\" database.".format(database)
    db_conn = db.DB(database)
    
    if verbose:
        print "Connected."
        print "Staging changes..."
        
    transaction = db_conn.db.begin()
        
    for member in member_data:
        cmd = ("INSERT INTO members (last_name, first_name, middle_name, uid, "
        "gender, birthday, msc, phone, email, address, city, state, zip, "
        "country) VALUES (\"{last_name}\", \"{first_name}\", "
        "\"{middle_name}\", \"{uid}\", {gender}, \"{birthday}\", {msc}, "
        "\"{phone}\", \"{email}\", \"{address}\", \"{city}\", \"{state}\", "
        "\"{zip}\", \"{country}\") ON DUPLICATE KEY UPDATE "
        "last_name=\"{last_name}\", first_name=\"{first_name}\", "
        "middle_name=\"{middle_name}\", uid=\"{uid}\", gender={gender}, "
        "birthday=\"{birthday}\", msc={msc}, phone=\"{phone}\", "
        "email=\"{email}\", address=\"{address}\", "
        "city=\"{city}\", state=\"{state}\", zip=\"{zip}\", "
        "country=\"{country}\"").format(**member)
        db_conn.db.execute(text(cmd))

    do_commit = raw_input("Staged uploading {} members. Commit changes? [y/n] "
        .format(len(member_data)))
    while not (do_commit == "y" or do_commit == "n"):
        print "Unrecognized command {}.".format(do_commit)
        do_commit = raw_input("Staged uploading {} members. Commit changes? [y/n] "
            .format(len(member_data)))
    if do_commit == "y":
        try:
            transaction.commit()
        except IntegrityError as e:
            print e
            print "Rolling back all server changes..."
            transaction.rollback()
    else:
        print "Rolling back all server changes..."
        transaction.rollback()
    if verbose:
        print "Disconnecting from server."
    
if __name__ == "__main__":
    args = parse_args()
    data = parse_file(args.filename, args.verbose)
    upload_to_db(data, args.database, args.verbose)
    print "Done."