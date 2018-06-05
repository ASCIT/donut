import flask
from donut.modules.groups import helpers as groups


def has_permission(user_id, permission_id):
    ''' 
    Returns True if [user_id] holds a position that directly 
    or indirectly (through a position relation) grants 
    them [permission_id]. Otherwise returns False.
    '''
    if not (isinstance(user_id, int) and isinstance(permission_id, int)):
        return False
    # get all position id's with this permission
    query = '''SELECT pos_id FROM position_permissions WHERE permission_id = %s'''
    with flask.g.pymysql_db.cursor() as cursor:
        cursor.execute(query, permission_id)
        result = cursor.fetchall()
    pos_ids = [row['pos_id'] for row in result]
    for pos_id in pos_ids:
        holders = groups.get_position_holders(pos_id)
        if {'user_id': user_id} in holders:
            return True
    return False
