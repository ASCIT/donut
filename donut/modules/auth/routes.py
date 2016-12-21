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
  # TODO: Add login logic.
  username = flask.request.form.get('username', None)
  password = flask.request.form.get('password', None)

  if username is not None and password is not None:
    user_id = helpers.authenticate(username, password)
    if user_id is not None:
      permissions = auth_utils.get_permissions(username)
      flask.session['username'] = username
      flask.session['permissions'] = permissions
      # True if there's any reason to show a link to the admin interface.
      flask.session['show_admin'] = len(auth_utils.generate_admin_links()) > 0
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

@blueprint.route('/userreg')
def user_reg():
  return flask.render_template('userreg.html')

@blueprint.route('/userreg/submit', methods = ['POST'])
def user_reg_submit():
  return ""

@blueprint.route('/recover', methods = ['POST'])
def recover():
  return ""
