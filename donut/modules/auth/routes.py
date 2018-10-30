import flask
from donut import auth_utils, constants
from donut.modules.auth import blueprint, helpers


@blueprint.route('/login')
def login():
    """Display login page."""
    return flask.render_template('login.html')


@blueprint.route('/login/submit', methods=['POST'])
def login_submit():
    """Handle authentication."""
    mask_and_user = flask.request.form.get('username', None)
    password = flask.request.form.get('password', None)

    # Need to take care of the case when masquerading occurs.
    username = None
    mask = None

    if mask_and_user is not None:
        # Check for the character to split.
        if ':' in mask_and_user:
            # If it's there, we assume the second part is a mask name.
            split = mask_and_user.split(':')
            username, mask = split[0], split[1]

            # But check to make sure the mask exists.
            if not auth_utils.get_user_id(mask):
                flask.flash('That person does not exist to mask.')
                return flask.redirect(flask.url_for('auth.login'))
        else:
            username = mask_and_user

    if username is not None and password is not None:
        user_id = helpers.authenticate(username, password)
        if user_id is not None:
            permissions = auth_utils.get_permissions(username)

            # We need to check if the user has masking permissions.
            #mask_perm = auth_utils.check_permission('mask')

            if mask is not None:
                if mask_perm:
                    # If the user has mask permissions, give them the mask.
                    flask.session['username'] = mask
                    permissions = auth_utils.get_permissions(mask)
                else:
                    # Else, refuse the attempt to masquerade.
                    flask.flash('You do not have permission to masquerade.')
                    return flask.redirect(flask.url_for('auth.login'))
            else:
                flask.session['username'] = username

            flask.session['permissions'] = permissions
            # True if there's any reason to show a link to the admin interface.
            flask.session[
                'show_admin'] = len(auth_utils.generate_admin_links()) > 0
            # Update last login time
            auth_utils.update_last_login(username)

            # Return to previous page if in session
            if 'next' in flask.session:
                redirect_to = flask.session.pop('next')
                return flask.redirect(redirect_to)
            else:
                return flask.redirect(flask.url_for('home'))
    flask.flash('Incorrect username or password. Please try again!')
    return flask.redirect(flask.url_for('auth.login'))


@blueprint.route('/login/forgot')
def forgot_password():
    """Displays a form for the user to reset a forgotten password."""
    return flask.render_template('forgot_password.html')


@blueprint.route('/login/forgot/submit', methods=['POST'])
def forgot_password_submit():
    """Handle forgotten password submission."""
    username = flask.request.form.get('username', None)
    email = flask.request.form.get('email', None)

    if helpers.handle_forgotten_password(username, email):
        flask.flash(
            "An email with a recovery link has been sent. If you no longer have access to your email (alums),"
            " please contact devteam@donut.caltech.edu to recover your account."
        )
        return flask.redirect(flask.url_for('auth.login'))
    else:
        flask.flash(
            "Incorrect username and/or email. If you continue to have issues with account recovery, contact devteam@donut.caltech.edu."
        )
        return flask.redirect(flask.url_for('auth.forgot_password'))


@blueprint.route('/login/reset/<reset_key>')
def reset_password(reset_key):
    """Checks the reset key. If successful, displays the password reset prompt."""
    username = auth_utils.check_reset_key(reset_key)
    if username is None:
        flask.flash(
            'Invalid request. If your link has expired, then you will need to generate a new one. '
            'If you continue to encounter problems, please contact devteam@donut.caltech.edu.'
        )
        return flask.redirect(flask.url_for('auth.forgot_password'))
    return flask.render_template(
        'reset_password.html', username=username, reset_key=reset_key)


@blueprint.route('/login/reset/<reset_key>/submit', methods=['POST'])
def reset_password_submit(reset_key):
    """Handles a password reset request."""
    username = auth_utils.check_reset_key(reset_key)
    if username is None:
        # Reset key was invalid.
        flask.flash("Someone's making it on the naughty list this year...")
        return flask.redirect(flask.url_for('auth.forgot_password'))
    new_password = flask.request.form.get('password', '')
    new_password2 = flask.request.form.get('password2', '')
    if helpers.handle_password_reset(username, new_password, new_password2):
        flask.flash('Password reset was successful.')
        return flask.redirect(flask.url_for('auth.login'))
    else:
        # Password reset handler handles error flashes.
        return flask.redirect(
            flask.url_for('auth.reset_password', reset_key=reset_key))


@blueprint.route('/logout')
def logout():
    flask.session.pop('username', None)
    return flask.redirect(flask.url_for('home'))
