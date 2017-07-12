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

# import all that good stuff
import argparse, re, datetime, db
from sqlalchemy import Column, Integer, String, Date
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

Base = declarative_base()

class Member(Base):
    __tablename__ = "members";
    
    user_id = Column(Integer, primary_key = True)
    uid = Column(String, unique = True)
    last_name = Column(String)
    first_name = Column(String)
    preferred_name = Column(String)
    middle_name = Column(String)
    email = Column(String)
    phone = Column(String)
    gender = Column(Integer)
    gender_custom = Column(String)
    birthday = Column(Date)
    entry_year = Column(Integer)
    graduation_year = Column(Integer)
    msc = Column(Integer)
    building = Column(String)
    room_num = Column(Integer)
    address = Column(String)
    city = Column(String)
    state = Column(String)
    zip = Column(String)
    country = Column(String)
    create_account_key = Column(String)
    
    def __repr__(self):
        return "<User(uid=\"%s\", last_name=\"%s\", first_name=\"%s\")" %\
            (self.uid, self.last_name, self.first_name)

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
        parsed_data = []
        for raw_line in registrar_file:
            # use regex to get all entries from between quotes
            parsed_line = [None if entry == "" else entry
                for entry in re.findall(r"\"(.*?)\"", raw_line)]
            # instanciate a new member
            new_member = Member(
                last_name = parsed_line[1],
                first_name = parsed_line[2],
                middle_name = parsed_line[3],
                uid = int(parsed_line[4]),
                gender = 0 if parsed_line[5] == "M" else 1,
                birthday = datetime.datetime
                    .strptime(parsed_line[6], "%d-%b-%Y").date(),
                msc = int(re.findall(r"\d+", parsed_line[10])[0]),
                phone = parsed_line[11],
                email = parsed_line[12],
                address = "".join(["" if line == None else line for line in
                    parsed_line[13:15]]),
                city = parsed_line[16],
                state = parsed_line[17],
                zip = parsed_line[18],
                country = "United States" if parsed_line[19] == None
                    else parsed_line[19]
            )
            parsed_data.append(new_member)
        if verbose:
            print "Loaded and parsed %d students." % len(parsed_data)
        return parsed_data
    
# connect to the desired database
def upload_to_db(student_data, database, verbose = False):
    """
    Establish a connection to the desired database and upload student data to
    it. Data is an array of member objects, where each member object is a
    member parsed from the registrar file.
    """
    if verbose:
        print "Connecting to \"%s\" database." % database
    db_conn = db.DB(database)
    Session = sessionmaker(bind = db_conn.engine)
    session = Session()
    if verbose:
        print "Connected."
    
    if verbose:
        print "Uploading students."
    for student in student_data:
        session.add(student)
    try:
        session.commit()
    except IntegrityError as e:
        print e
        print "Rolling back all server changes..."
        session.rollback()
    if verbose:
        print "Disconnecting from server."
    
if __name__ == "__main__":
    args = parse_args()
    data = parse_file(args.filename, args.verbose)
    upload_to_db(data, args.database, args.verbose)
    print "Done."