import flask
import sqlalchemy
from donut.modules.groups import helpers as groups
from donut.modules.core import helpers as core


def get_BoC_member():
    """
    Queries the database and returns list of people on BoC
    """
    # get the group id of BoC
    group_id = groups.get_group_list_data(['group_id'], {'group_name': 'BoC'})
    if group_id != []:
        group_id = group_id[0]['group_id']  # extract from list of dicts
        # get a list of user ids and their position names for a given group
        query = '''
        SELECT user_id, pos_name from
        (SELECT DISTINCT user_id, ph.pos_id FROM positions p LEFT JOIN
        position_relations pr ON p.pos_id=pr.pos_id_to
        INNER JOIN position_holders ph ON ph.pos_id=p.pos_id OR
        pr.pos_id_from=ph.pos_id
        WHERE group_id = %s) sub INNER JOIN positions p
        ON p.pos_id = sub.pos_id'''
        with flask.g.pymysql_db.cursor() as cursor:
            cursor.execute(query, [group_id])
            result = cursor.fetchall()
        members = [row['user_id'] for row in result]
        members = core.get_member_data(members)
        high_pos = []
        pos_house = []
        for i in range(len(result)):
            if 'preferred_name' in members[i]:
                first_name = members[i]['preferred_name']
            else:
                first_name = members[i]['first_name']
            name = first_name + ' ' + members[i]['last_name']
            email = members[i]['email']
            pos_name = result[i]['pos_name']
            if pos_name == 'Chair' or 'ecretary' in pos_name:
                high_pos.append((name, pos_name, email))
            else:
                pos_house.append((name, pos_name, email))
        # sort by position name (brings chair above secretary)
        high_pos.sort(key=lambda tup: tup[1])
        pos_house.sort(key=lambda tup: tup[1])

        fin_result = high_pos + pos_house

        return fin_result
    else:
        return []


def get_CRC_member():
    """
    Queries the database and returns list of people on CRC
    """
    # get the group id of BoC
    group_id = groups.get_group_list_data(['group_id'], {'group_name': 'CRC'})
    print(group_id)
    if group_id != []:
        group_id = group_id[0]['group_id']  # extract from list of dicts
        # get a list of user ids and their position names for a given group
        query = '''
        SELECT user_id, pos_name from
        (SELECT DISTINCT user_id, ph.pos_id FROM positions p LEFT JOIN
        position_relations pr ON p.pos_id=pr.pos_id_to
        INNER JOIN position_holders ph ON ph.pos_id=p.pos_id OR
        pr.pos_id_from=ph.pos_id
        WHERE group_id = %s) sub INNER JOIN positions p
        ON p.pos_id = sub.pos_id'''
        with flask.g.pymysql_db.cursor() as cursor:
            cursor.execute(query, [group_id])
            result = cursor.fetchall()
        members = [row['user_id'] for row in result]
        members = core.get_member_data(members)
        high_pos = []
        pos_house = []
        for i in range(len(result)):
            if 'preferred_name' in members[i]:
                first_name = members[i]['preferred_name']
            else:
                first_name = members[i]['first_name']
            name = first_name + ' ' + members[i]['last_name']
            email = members[i]['email']
            pos_name = result[i]['pos_name']
            if pos_name == 'Chair' or 'ecretary' in pos_name:
                high_pos.append((name, pos_name, email))
            else:
                pos_house.append((name, pos_name, email))
        # sort by position name (brings chair above secretary)
        high_pos.sort(key=lambda tup: tup[1])
        pos_house.sort(key=lambda tup: tup[1])

        fin_result = high_pos + pos_house

        return fin_result
    else:
        return []
