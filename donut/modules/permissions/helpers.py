import flask
from donut.modules.groups import helpers as groups

def has_permission(user_id, permission_id):
    ''' 
    Returns True if [user_id] holds a position that directly or indirectly (through
    a position relation) grants them [permission_id].
    Otherwise returns False.
    '''
    # get all position id's with this permission
    query = '''SELECT pos_id FROM position_permissions WHERE permission_id = %s'''
    with flask.g.pymysql_db.cursor() as cursor:
        cursor.execute(query, (permission_id))
        result = cursor.fetchall()
    pos_ids = [row['pos_id'] for row in result]
    for pos_id in pos_ids:
        holders = groups.get_position_holder(pos_id)
        holders = [row['user_id'] for row in holders]
        if user_id in holders: 
            return True
    return False

