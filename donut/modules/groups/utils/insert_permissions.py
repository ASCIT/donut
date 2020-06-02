#!/usr/bin/env python

import argparse
from donut.pymysql_connection import make_db
from donut.default_permissions import Permissions
from donut.modules.calendar.permissions import calendar_permissions
from donut.modules.directory_search.permissions import ManageMembersPermissions
from donut.modules.editor.edit_permission import EditPermission as page_edit_permissions
from donut.modules.feedback.permissions import BOD_PERMISSIONS as bod_permissions, ARC_PERMISSIONS as arc_permissions, DONUT_PERMISSIONS as donut_permissions
from donut.modules.uploads.upload_permission import UploadPermissions as upload_permissions
from donut.modules.voting.permissions import Permissions as voting_permissions

# Permissions to assign to all positions in a group with a given control value.
# True means that a position has control over that group.
groups_permissions = {
    "Devteam":
    {
        True: [Permissions.ADMIN], # All
        False: [Permissions.ADMIN] # All
    },
    "IHC":
    {
        # Editing Pages, Upload documents
        True: [page_edit_permissions.ABLE, upload_permissions.ABLE],
        # Editing Pages, Upload documents
        False: [page_edit_permissions.ABLE, upload_permissions.ABLE]
    },
    "ASCIT":
    {   # Editing Pages, Upload documents, View Bodfeedback summary,
        # Edit Bodfeedback, Edit Bodfeedback emails, View Bodfeedback emails
        True: [
                page_edit_permissions.ABLE,
                upload_permissions.ABLE,
                bod_permissions.SUMMARY,
                bod_permissions.TOGGLE_RESOLVED,
                bod_permissions.ADD_REMOVE_EMAIL,
                bod_permissions.VIEW_EMAILS,
            # All the calendars
                calendar_permissions.ASCIT,
                calendar_permissions.AVERY,
                calendar_permissions.BECHTEL,
                calendar_permissions.BLACKER,
                calendar_permissions.DABNEY,
                calendar_permissions.FLEMING,
                calendar_permissions.LLOYD,
                calendar_permissions.PAGE,
                calendar_permissions.RICKETTS,
                calendar_permissions.RUDDOCK,
                calendar_permissions.OTHER,
                calendar_permissions.ATHLETICS,
                # Surveys
                voting_permissions.SURVEYS
            ],
        # View Bodfeedback summary, Edit Bodfeedback, View Bodfeedback emails
        False: [
                bod_permissions.SUMMARY,
                bod_permissions.TOGGLE_RESOLVED,
                bod_permissions.VIEW_EMAILS,
                # Surveys
                voting_permissions.SURVEYS]
    },
    "Academics and Research Committee (ARC)":
    {
        # View Arcfeedback summary, Edit Arcfeedback, Edit Arcfeedback emails
        # View Arcfeedback emails, Surveys
        True: [
                arc_permissions.SUMMARY,
                arc_permissions.TOGGLE_RESOLVED,
                arc_permissions.ADD_REMOVE_EMAIL,
                arc_permissions.VIEW_EMAILS,
                voting_permissions.SURVEYS],
        # View Arcfeedback summary, Edit Arcfeedback, View Arcfeedback emails,
        # Surveys
        False: [arc_permissions.SUMMARY,
                arc_permissions.TOGGLE_RESOLVED,
                arc_permissions.VIEW_EMAILS,
                voting_permissions.SURVEYS],
    },
    "Board of Control (BoC)": {
        True: [page_edit_permissions.ABLE, upload_permissions.ABLE]
    },
    "Avery":
    {
        # Edit Avery Calendar, Manage Avery members
        True: [calendar_permissions.AVERY, ManageMembersPermissions.AVERY],
    },
    "Blacker":
    {
        # Edit Blacker Calendar, Manage Blacker members
        True: [calendar_permissions.BLACKER, ManageMembersPermissions.BLACKER],
    },
    "Dabney":
    {
        # Edit Dabney Calendar, Manage Dabney members
        True: [calendar_permissions.DABNEY, ManageMembersPermissions.DABNEY],
    },
    "Fleming":
    {
        # Edit Fleming Calendar, Manage Fleming members
        True: [calendar_permissions.FLEMING, ManageMembersPermissions.FLEMING],
    },
    "Lloyd":
    {
        # Edit LLoyd Calendar, Manage Lloyd members
        True: [calendar_permissions.LLOYD, ManageMembersPermissions.LLOYD],
    },
    "Page":
    {
        # Edit Page Calendar, Manage Page members
        True: [calendar_permissions.PAGE, ManageMembersPermissions.PAGE],
    },
    "Ricketts":
    {
        # Edit Ricketts Calendar, Manage Ricketts members
        True: [calendar_permissions.RICKETTS, ManageMembersPermissions.RICKETTS],
    },
    "Ruddock":
    {
        # Edit Ruddock Calendar, Manage Ruddock members
        True: [calendar_permissions.RUDDOCK, ManageMembersPermissions.RUDDOCK],
    },
    "Bechtel":
    {
        # Edit Bechtel Calendar
        True: [calendar_permissions.BECHTEL],
    },
    "Review Committee":
    {
        # Editing Pages, Upload documents, Surveys
        True: [
                page_edit_permissions.ABLE,
                upload_permissions.ABLE,
                voting_permissions.SURVEYS]
    }
}


def insert_permissions(env):
    db = make_db(env)
    try:
        db.begin()
        with db.cursor() as cursor:
            for group, group_permissions in groups_permissions.items():
                for control, permission_ids in group_permissions.items():
                    for position in get_positions(group, control, cursor):
                        for permission_id in permission_ids:
                            if add_permission(position['pos_id'],
                                              permission_id.value, cursor):
                                print(
                                    f'Granted "{permission_id.name}" to group "{group}" position "{position["pos_name"]}"'
                                )
        db.commit()
    finally:
        db.close()


def get_positions(group_name, control, cursor):
    query = '''
        SELECT pos_id, pos_name
        FROM groups NATURAL JOIN positions
        WHERE group_name = %s AND control = %s
    '''
    cursor.execute(query, (group_name, control))
    return cursor.fetchall()


def add_permission(position_id, permission_id, cursor):
    query = """
        INSERT INTO position_permissions(pos_id, permission_id)
        VALUES (%s, %s)
        ON DUPLICATE KEY UPDATE pos_id = pos_id
    """
    cursor.execute(query, (position_id, permission_id))
    return cursor.rowcount > 0


if __name__ == "__main__":
    # Parse input arguments
    parser = argparse.ArgumentParser(
        description='Inserts permissions based on control of a position.')
    parser.add_argument(
        "-e", "--env", default="dev", help="Database to update")
    args = parser.parse_args()
    insert_permissions(args.env)
