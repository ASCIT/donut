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
                group_name = clean_names(line['org_name'])
                pos_name = line['pos_name']
                control = line['control']
                start_date = line['start_date']
                end_date = line['end_date']
                group_id = get_create_group_id(group_name, db)
                pos_id = get_create_position_id(pos_name, group_id, control,
                                                db)
                user_id = get_user_id_from_uid(uid, db)

                query = """
                INSERT INTO position_holders(pos_id, user_id, start_date, end_date) VALUES(%s, %s, %s, %s) 
                """
                with db.cursor() as cursor:
                    cursor.execute(query,
                                   [pos_id, user_id, start_date, end_date])
        db.commit()
    finally:
        db.close()


def get_create_group_id(group_name, db):
    # I think the vast majority of non-auto created groups are committees.
    insertion_query = "INSERT INTO groups(group_name, type) VALUES(%s, 'committee')"
    res = get_group_id(group_name, db)
    if res is None:
        with db.cursor() as cursor:
            cursor.execute(insertion_query, [group_name])
        res = get_group_id(group_name, db)
    return res['group_id']


def get_group_id(group_name, db):
    group_id_query = "SELECT group_id FROM groups WHERE group_name=%s"
    with db.cursor() as cursor:
        cursor.execute(group_id_query, [group_name])
        res = cursor.fetchone()
    return res


def clean_names(group_name):
    return group_name.replace("Hovse", "House")


def get_user_id_from_uid(uid, db):
    query = "SELECT user_id FROM members WHERE uid = %s"
    with db.cursor() as cursor:
        cursor.execute(query, [uid])
        res = cursor.fetchone()
    return None if res is None else res['user_id']


def get_create_position_id(pos_name, group_id, control, db):
    insertion_query = "INSERT INTO positions(group_id, pos_name, control) VALUES(%s, %s, %s)"
    res = get_position_id(pos_name, group_id, db)
    if res is None:
        with db.cursor() as cursor:
            cursor.execute(insertion_query, [
                group_id, pos_name, True if control == "t" else False
            ])
        res = get_position_id(pos_name, group_id, db)
    return res['pos_id']


def get_position_id(pos_name, group_id, db):
    query = "SELECT pos_id FROM positions WHERE group_id = %s AND pos_name = %s"
    with db.cursor() as cursor:
        cursor.execute(query, [group_id, pos_name])
        res = cursor.fetchone()
    return res


if __name__ == "__main__":
    # Parse input arguments
    parser = argparse.ArgumentParser(
        description='Imports a list of past house members from the old db.')
    # SELECT start_date, end_date,  pos_name , org_name, uid, control
    # FROM position_holders NATURAL JOIN position_titles NATURAL JOIN
    # position_organizations NATURAL JOIN inums NATURAL JOIN undergrads;

    parser.add_argument(
        "-e", "--env", default="dev", help="Database to update")
    parser.add_argument("file", help="Path to old media wiki xml")
    args = parser.parse_args()

    import_file(args.env, args.file)
