from datetime import date, datetime
import flask
from flask import jsonify

from donut.auth_utils import get_user_id, is_admin
from donut.modules.groups import blueprint, helpers

YYYY_MM_DD = "%Y-%m-%d"


@blueprint.route("/1/groups")
def get_groups_list():
    args = flask.request.args
    # Create a dict of the passed in attribute which are filterable
    filterable_attrs = ["group_id", "group_name", "group_desc", "type"]
    attrs = {
        attr: value
        for attr, value in args.items() if attr in filterable_attrs
    }
    fields = None
    if "fields" in args:
        fields = [f.strip() for f in args["fields"].split(',')]
    return jsonify(helpers.get_group_list_data(fields=fields, attrs=attrs))


@blueprint.route("/1/groups", methods=["POST"])
def create_group():
    """POST /1/groups - Create a new group"""
    username = flask.session.get('username')
    if not username:
        return jsonify({'success': False, 'message': 'Not logged in'})

    user_id = get_user_id(username)
    # Only admins and superuser positions can create groups
    if not (is_admin() or helpers.is_position_superuser(user_id)):
        return jsonify({
            'success': False,
            'message': 'You do not have permission to create groups'
        })

    form = flask.request.form
    group_name = form.get('group_name', '').strip()
    if not group_name:
        return jsonify({'success': False, 'message': 'Group name is required'})

    group_desc = form.get('group_desc', '').strip()
    group_type = form.get('group_type', 'committee')

    try:
        group_id = helpers.create_group(
            group_name,
            group_desc=group_desc,
            group_type=group_type
        )
        return jsonify({'success': True, 'group_id': group_id})
    except Exception as e:
        flask.current_app.logger.exception(f'Failed to create group: {e}')
        return jsonify({'success': False, 'message': 'Unable to create group'})


@blueprint.route("/1/groups/<int:group_id>/positions")
def get_group_positions(group_id):
    """GET /1/groups/<int:group_id>/positions"""
    return jsonify(helpers.get_group_positions(group_id))


@blueprint.route("/1/positions", methods=["GET"])
def get_positions():
    return jsonify(helpers.get_position_data())


@blueprint.route("/1/positions", methods=["POST"])
def create_position():
    form = flask.request.form
    group_id = form.get('group_id')
    try:
        group_id = int(group_id)
    except ValueError:
        return jsonify({'success': False, 'message': 'Invalid group'})
    pos_name = form.get('pos_name')
    if not pos_name:
        return jsonify({'success': False, 'message': 'Invalid position'})
    username = flask.session.get('username')
    if not (username and helpers.can_control(get_user_id(username), group_id)):
        return jsonify({
            'success': False,
            'message': 'You do not control this group'
        })

    send = 'send' in form
    control = 'control' in form
    receive = 'receive' in form
    try:
        helpers.add_position(
            group_id, pos_name, send=send, control=control, receive=receive)
    except Exception as e:
        flask.current_app.logger.exception(f'Failed to create position: {e}')
        return jsonify({'success': False, 'message': 'Unable to add position'})

    return jsonify({'success': True})


@blueprint.route("/1/groups/<int:group_id>")
def get_groups(group_id):
    """GET /1/groups/<int:group_id>"""
    return jsonify(helpers.get_group_data(group_id))


@blueprint.route("/1/groups/<int:group_id>", methods=["DELETE"])
def delete_group(group_id):
    """DELETE /1/groups/<int:group_id> - Delete a group (only if empty)"""
    username = flask.session.get('username')
    if not username:
        return jsonify({'success': False, 'message': 'Not logged in'})

    user_id = get_user_id(username)
    # Only admins and superuser positions can delete groups
    if not (is_admin() or helpers.is_position_superuser(user_id)):
        return jsonify({
            'success': False,
            'message': 'You do not have permission to delete groups'
        })

    # Check if group has any members
    members = helpers.get_members_by_group(group_id)
    if members:
        return jsonify({
            'success': False,
            'message': 'Cannot delete group: it still has {} member(s). Remove all members first.'.format(len(members))
        })

    try:
        helpers.delete_group(group_id)
        return jsonify({'success': True})
    except Exception as e:
        flask.current_app.logger.exception(f'Failed to delete group: {e}')
        return jsonify({'success': False, 'message': 'Unable to delete group'})


@blueprint.route("/1/groups/<int:group_id>/members")
def get_group_members(group_id):
    """GET /1/groups/<int:group_id>"""
    return jsonify(helpers.get_members_by_group(group_id))


@blueprint.route("/1/positions/<int:pos_id>", methods=["GET"])
def get_pos_holders(pos_id):
    """GET /1/positions/<int:pos_id>"""
    return jsonify(helpers.get_position_holders(pos_id))


@blueprint.route("/1/positions/<int:pos_id>", methods=["PUT"])
def update_position(pos_id):
    """PUT /1/positions/<int:pos_id> - Update position settings"""
    username = flask.session.get('username')
    if not username:
        return jsonify({'success': False, 'message': 'Not logged in'})

    user_id = get_user_id(username)
    group_id = helpers.get_position_group(pos_id)
    if not (group_id and helpers.can_control(user_id, group_id)):
        return jsonify({
            'success': False,
            'message': 'You do not control this group'
        })

    form = flask.request.form
    send = form.get('send') == '1'
    control = form.get('control') == '1'
    receive = form.get('receive') == '1'

    try:
        helpers.update_position(pos_id, send=send, control=control, receive=receive)
        return jsonify({'success': True})
    except Exception as e:
        flask.current_app.logger.exception(f'Failed to update position: {e}')
        return jsonify({'success': False, 'message': 'Unable to update position'})


@blueprint.route("/1/positions/<int:pos_id>", methods=["DELETE"])
def delete_position(pos_id):
    """DELETE /1/positions/<int:pos_id> - Delete a position (only if no holders)"""
    username = flask.session.get('username')
    if not username:
        return jsonify({'success': False, 'message': 'Not logged in'})

    user_id = get_user_id(username)
    group_id = helpers.get_position_group(pos_id)
    if not (group_id and helpers.can_control(user_id, group_id)):
        return jsonify({
            'success': False,
            'message': 'You do not control this group'
        })

    try:
        if helpers.delete_position(pos_id):
            return jsonify({'success': True})
        else:
            return jsonify({
                'success': False,
                'message': 'Cannot delete position: it still has holders. Remove all holders first.'
            })
    except Exception as e:
        flask.current_app.logger.exception(f'Failed to delete position: {e}')
        return jsonify({'success': False, 'message': 'Unable to delete position'})


@blueprint.route("/1/positions/<int:pos_id>", methods=["POST"])
def create_pos_holder(pos_id):
    form = flask.request.form
    user_id = form.get('user_id')
    try:
        user_id = int(user_id)
    except ValueError:
        return jsonify({'success': False, 'message': 'Invalid user'})
    start_date = form.get('start_date')
    try:
        start_date = datetime.strptime(start_date, YYYY_MM_DD)
    except:
        return jsonify({'success': False, 'message': 'Invalid start date'})
    end_date = form.get('end_date')
    try:
        end_date = datetime.strptime(end_date, YYYY_MM_DD)
    except:
        return jsonify({'success': False, 'message': 'Invalid end date'})
    if end_date.date() < date.today() or end_date < start_date:
        return jsonify({'success': False, 'message': 'End date is too early'})
    username = flask.session.get('username')
    group_id = helpers.get_position_group(pos_id)
    if not (username and group_id
            and helpers.can_control(get_user_id(username), group_id)):
        return jsonify({
            'success': False,
            'message': 'You do not control this group'
        })

    try:
        helpers.create_position_holder(pos_id, user_id, start_date, end_date)
    except Exception as e:
        flask.current_app.logger.exception(
            f'Failed to add position holder: {e}')
        return jsonify({
            'success': False,
            'message': 'Unable to add position holder'
        })
    return jsonify({'success': True})


@blueprint.route("/1/admin/positions", methods=["GET"])
def get_admin_positions():
    """
    GET /1/admin/positions
    Returns all positions with holders for groups the user can control.
    Used by the admin UI to load all data in a single request.
    """
    username = flask.session.get('username')
    if not username:
        return jsonify({'positions': []})

    user_id = get_user_id(username)
    # Get the group IDs from query param (passed from frontend which knows approved groups)
    group_ids_param = flask.request.args.get('group_ids', '')
    if not group_ids_param:
        return jsonify({'positions': []})

    try:
        group_ids = [int(gid) for gid in group_ids_param.split(',') if gid]
    except ValueError:
        return jsonify({'positions': []})

    # Verify user can control these groups
    group_ids = [gid for gid in group_ids if helpers.can_control(user_id, gid)]

    return jsonify(helpers.get_admin_positions_with_holders(group_ids))


@blueprint.route("/1/position_holds/<int:hold_id>", methods=("DELETE", ))
def remove_pos_holder(hold_id):
    username = flask.session.get('username')
    group_id = helpers.get_hold_group(hold_id)
    if not (username and group_id
            and helpers.can_control(get_user_id(username), group_id)):
        return jsonify({
            'success': False,
            'message': 'You do not control this group'
        })

    try:
        helpers.end_position_holder(hold_id)
    except Exception as e:
        flask.current_app.logger.exception(
            f'Failed to remove position holder: {e}')
        return jsonify({
            'success': False,
            'message': 'Unable to remove position holder'
        })
    return jsonify({'success': True})
