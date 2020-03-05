import argparse
from donut.pymysql_connection import make_db

valid_permissions = {
    "Devteam":
    {
        # True means that a position has control over that group.
        True: [1], # All
        False: [1] # All
    },
    "IHC":
    {
        True: [2, 4, 5], #Edit Rotation Info, Editing Pages, Upload documents
        False: [2, 4, 5] #Edit Rotation Info, Editing Pages, Upload documents
    },
    "ASCIT":
    {   # Editing Pages, Upload documents, View Bodfeedback summary,
        # Edit Bodfeedback, Edit Bodfeedback emails, View Bodfeedback emails
        True: [4, 5, 8,
            9, 10, 11,
            # All the calendars
            21, 22, 23, 24, 25, 26, 27, 28, 29, 30, 31, 32,
            # Surveys
            33],
        # View Bodfeedback summary, Edit Bodfeedback, View Bodfeedback emails
        False: [8, 9, 11,
            # Surveys
            33]
    },
    "Academics and Research Committee (ARC)":
    {
        # View Arcfeedback summary, Edit Arcfeedback, Edit Arcfeedback emails
        # View Arcfeedback emails, Surveys
        True: [13, 14, 15, 16, 33],
        # View Arcfeedback summary, Edit Arcfeedback, View Arcfeedback emails,
        # Surveys
        False: [13, 14, 16, 33]
    },
    "Avery":
    {   # Edit Avery Calendar
        True: [21],
    },
    "Blacker":
    {
        # Edit Blacker Calendar
        True: [24],
    },
    "Dabney":
    {
        # Edit Dabney Calendar
        True: [25],
    },
    "Fleming":
    {
        # Edit Fleming Calendar
        True: [26],
    },
    "Lloyd":
    {
        # Edit Fleming Calendar
        True: [27],
    },
    "Page":
    {
        # Edit Fleming Calendar
        True: [28],
    },
    "Ricketts":
    {
        # Edit Ricketts Calendar
        True: [29],
    },
    "Ruddock":
    {
        # Edit Ruddock Calendar
        True: [30],
    },
    "Review Committee":
    {
        # Editing Pages, Upload documents, Surveys
        True: [4, 5, 33]
    }
}


def insert_permissions(env):
    db = make_db(env)
    try:
        db.begin()
        for group in valid_permissions:
            query = '''INSERT INTO position_permissions(pos_id, permission_id)
                        VALUES (%s, %s) '''
            for control in valid_permissions[group]:
                position_ids = get_position_id(group, control, db)
                for position_id in position_ids:
                    for permission_id in valid_permissions[group][control]:
                        with db.cursor() as cursor:
                            cursor.execute(query, [position_id, permission_id])
        db.commit()
    finally:
        db.close()


def get_position_id(group_name, control, db):
    query = '''
        SELECT pos_id
            FROM groups NATURAL JOIN positions
            WHERE group_name = %s and control = %s
        '''
    with db.cursor() as cursor:
        cursor.execute(query, [group_name, control])
        res = cursor.fetchall()
    return [result["pos_id"] for result in res]


if __name__ == "__main__":
    # Parse input arguments
    parser = argparse.ArgumentParser(
        description='Inserts permissions based on control of a position.')
    parser.add_argument(
        "-e", "--env", default="dev", help="Database to update")
    args = parser.parse_args()
    insert_permissions(args.env)
