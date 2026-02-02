"""
GPT-SAM Routes
Provides the chatbot interface for group/position management assistance.
"""

import flask
from flask import jsonify, request

from donut.auth_utils import get_user_id, get_permissions, is_admin
from donut.modules.gpt_sam import blueprint, helpers
from donut.modules.gpt_sam.permissions import Permissions as GptSamPermissions
from donut.default_permissions import Permissions


@blueprint.route('/gpt-sam')
def gpt_sam():
    """Render the GPT-SAM chat interface"""
    # Check if user is logged in
    username = flask.session.get('username')
    if not username:
        flask.flash('You must be logged in to access GPT-SAM.')
        return flask.redirect(flask.url_for('auth.login'))

    # Check if user has permission (Admin or GPT_SAM via ASCIT/IHC membership)
    user_permissions = get_permissions(username)
    has_access = (
        Permissions.ADMIN in user_permissions or
        GptSamPermissions.GPT_SAM in user_permissions
    )

    if not has_access:
        flask.flash('You do not have permission to access GPT-SAM. This feature is only available to ASCIT and IHC members.')
        return flask.redirect(flask.url_for('home'))

    return flask.render_template('gpt_sam.html')


@blueprint.route('/gpt-sam/chat', methods=['POST'])
def chat():
    """Handle chat API requests"""
    # Check authentication
    username = flask.session.get('username')
    if not username:
        return jsonify({'error': 'Not authenticated'}), 401

    # Check permissions (Admin or GPT_SAM via ASCIT/IHC membership)
    user_permissions = get_permissions(username)
    has_access = (
        Permissions.ADMIN in user_permissions or
        GptSamPermissions.GPT_SAM in user_permissions
    )

    if not has_access:
        return jsonify({'error': 'Permission denied'}), 403

    # Get request data
    data = request.get_json()
    if not data or 'messages' not in data:
        return jsonify({'error': 'Missing messages'}), 400

    messages = data['messages']
    user_id = get_user_id(username)

    # Get current user info to pass to the chatbot
    current_user = {
        'user_id': user_id,
        'username': username
    }

    try:
        response = helpers.chat(messages, current_user=current_user)
        return jsonify({'response': response})
    except FileNotFoundError as e:
        flask.current_app.logger.error(f'GPT-SAM config error: {e}')
        return jsonify({'error': 'GPT-SAM is not configured. Please contact an administrator.'}), 500
    except Exception as e:
        flask.current_app.logger.error(f'GPT-SAM error: {e}')
        return jsonify({'error': 'An error occurred processing your request.'}), 500
