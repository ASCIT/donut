import argparse
from donut.pymysql_connection import make_db
from donut.modules.auth.permissions import Permissions as auth_permissions
from donut.modules.calendar.permissions import calendar_permissions
from donut.modules.directory_search.permissions import Directory_Permissions as directory_permissions
from donut.modules.editor.edit_permission import EditPermission as page_edit_permissions
from donut.modules.feedback.permissions import BOD_PERMISSIONS as bod_permissions, ARC_PERMISSIONS as arc_permissions, DONUT_PERMISSIONS as donut_permissions
from donut.modules.uploads.upload_permission import UploadPermissions as upload_permissions
from donut.modules.voting.permissions import Permissions as voting_permissions

valid_permissions = {
    "Devteam":
    {
        # True means that a position has control over that group.
        True: [1], # All
        False: [1] # All
    },
    "IHC":
    {
        # Editing Pages, Upload documents
        True: [page_edit_permissions.ABLE.value, upload_permissions.ABLE.value],
        # Editing Pages, Upload documents
        False: [page_edit_permissions.ABLE.value, upload_permissions.ABLE.value]
    },
    "ASCIT":
    {   # Editing Pages, Upload documents, View Bodfeedback summary,
        # Edit Bodfeedback, Edit Bodfeedback emails, View Bodfeedback emails
        True: [
                page_edit_permissions.ABLE.value,
                upload_permissions.ABLE.value,
                bod_permissions.SUMMARY.value,
                bod_permissions.TOGGLE_READ.value,
                bod_permissions.ADD_REMOVE_EMAIL.value,
                bod_permissions.VIEW_EMAILS.value,
            # All the calendars
                calendar_permissions.ASCIT.value,
                calendar_permissions.AVERY.value,
                calendar_permissions.BECHTEL.value,
                calendar_permissions.BLACKER.value,
                calendar_permissions.DABNEY.value,
                calendar_permissions.FLEMING.value,
                calendar_permissions.LLOYD.value,
                calendar_permissions.PAGE.value,
                calendar_permissions.RICKETTS.value,
                calendar_permissions.RUDDOCK.value,
                calendar_permissions.OTHER.value,
                calendar_permissions.ATHLETICS.value,
                # Surveys
                voting_permissions.SURVEYS.value
            ],
        # View Bodfeedback summary, Edit Bodfeedback, View Bodfeedback emails
        False: [
                bod_permissions.SUMMARY.value,
                bod_permissions.TOGGLE_READ.value,
                bod_permissions.VIEW_EMAILS.value,
                # Surveys
                voting_permissions.SURVEYS.value]
    },
    "Academics and Research Committee (ARC)":
    {
        # View Arcfeedback summary, Edit Arcfeedback, Edit Arcfeedback emails
        # View Arcfeedback emails, Surveys
        True: [
                arc_permissions.SUMMARY.value,
                arc_permissions.TOGGLE_READ.value,
                arc_permissions.ADD_REMOVE_EMAIL.value,
                arc_permissions.VIEW_EMAILS.value,
                voting_permissions.SURVEYS.value],
        # View Arcfeedback summary, Edit Arcfeedback, View Arcfeedback emails,
        # Surveys
        False: [arc_permissions.SUMMARY.value,
                arc_permissions.TOGGLE_READ.value,
                arc_permissions.VIEW_EMAILS.value,
                voting_permissions.SURVEYS.value],
    },
    "Avery":
    {   # Edit Avery Calendar
        True: [calendar_permissions.AVERY.value],
    },
    "Blacker":
    {
        # Edit Blacker Calendar
        True: [calendar_permissions.BLACKER.value],
    },
    "Dabney":
    {
        # Edit Dabney Calendar
        True: [calendar_permissions.DABNEY.value],
    },
    "Fleming":
    {
        # Edit Fleming Calendar
        True: [calendar_permissions.FLEMING.value],
    },
    "Lloyd":
    {
        # Edit LLoyd Calendar
        True: [calendar_permissions.LLOYD.value],
    },
    "Page":
    {
        # Edit Page Calendar
        True: [calendar_permissions.PAGE.value],
    },
    "Ricketts":
    {
        # Edit Ricketts Calendar
        True: [calendar_permissions.RICKETTS.value],
    },
    "Ruddock":
    {
        # Edit Ruddock Calendar
        True: [calendar_permissions.RUDDOCK.value],
    },
    "Bechtel":
    {
        # Edit Bechtel Calendar
        True: [calendar_permissions.BECHTEL.value],
    },
    "Review Committee":
    {
        # Editing Pages, Upload documents, Surveys
        True: [
                page_edit_permissions.ABLE.value,
                upload_permissions.ABLE.value,
                voting_permissions.SURVEYS.value]
    }
}


def insert_permissions(env):
    db = make_db(env)
    try:
        db.begin()
        query = '''
            INSERT INTO position_permissions(pos_id, permission_id)
            VALUES (%s, %s)
            ON DUPLICATE KEY UPDATE pos_id = pos_id
        '''
        for group, group_permissions in valid_permissions.items():
            for control, permission_ids in group_permissions.items():
                position_ids = get_position_id(group, control, db)
                for position_id in position_ids:
                    for permission_id in permission_ids:
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
