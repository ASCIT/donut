import argparse
from donut.pymysql_connection import make_db
import csv


def import_file(env, filename):
    # Create reference to DB
    db = make_db(env)
    try:
        db.begin()
        with open(filename, "r") as f:
            reader = csv.DictReader(f, delimiter=",")
            for i, line in enumerate(reader):
                uid = line['uid']
                house = line['house']
                member_type = line['description']
                pos_id = get_position_id(member_type, house, db)
                user_id = get_user_id_from_uid(uid, db)
                if pos_id is None or user_id is None:
                    print("Skipped", line)
                    continue
                query = """
                INSERT INTO position_holders(pos_id, user_id) VALUES( %s, %s) 
                """
                with db.cursor() as cursor:
                    cursor.execute(query, [pos_id, user_id])
        db.commit()
    finally:
        db.close()


def get_user_id_from_uid(uid, db):
    query = "SELECT user_id FROM members WHERE uid = %s"
    with db.cursor() as cursor:
        cursor.execute(query, [uid])
        res = cursor.fetchone()
    return None if res is None else res['user_id']


def get_position_id(member_type, house, db):
    query = "SELECT pos_id FROM positions NATURAL JOIN groups WHERE group_name = %s and pos_name = %s"
    with db.cursor() as cursor:
        cursor.execute(query, [house + " House", member_type])
        res = cursor.fetchone()
    return None if res is None else res['pos_id']


if __name__ == "__main__":
    # Parse input arguments
    parser = argparse.ArgumentParser(
        description='Imports a list of past house members from the old db')
    parser.add_argument(
        "-e", "--env", default="dev", help="Database to update")
    parser.add_argument("file", help="Path to old media wiki xml")
    args = parser.parse_args()

    import_file(args.env, args.file)
