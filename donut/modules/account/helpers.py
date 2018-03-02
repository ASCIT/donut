import flask

from donut import auth_utils
from donut import email_templates
from donut import email_utils
from donut import misc_utils
from donut import validation_utils


def get_user_data(user_id):
    """Returns user data for the create account form."""
    s = """
    SELECT first_name, last_name, email, uid,
      entry_year, graduation_year
    FROM members
    WHERE user_id = %s
    """
    with flask.g.pymysql_db.cursor() as cursor:
        cursor.execute(s, [str(user_id)])
        result = cursor.fetchone()
    return result


def handle_create_account(user_id, username, password, password2, birthday):
    """Handles account creation.
  Creates account if all values provided are valid.
  Returns:
    bool indicating success.
  """
    # Validate username and password. The validate_* functions will flash errors.
    # We want to check all fields and not just stop at the first error.
    is_valid = True
    if not validation_utils.validate_username(username):
        is_valid = False
    if not validation_utils.validate_password(password, password2):
        is_valid = False
    if not validation_utils.validate_date(birthday):
        is_valid = False

    if not is_valid:
        return False

    # Insert new values into the database. Because the password is updated in a
    # separate step, we must use a transaction to execute this query.
    transaction = flask.g.pymysql_db.begin()
    try:
        # Insert the new row into users.
        s = """
      INSERT INTO users (user_id, username, password_hash)
      VALUES (%s, %s, %s)
      """
        with flask.g.pymysql_db.cursor() as cursor:
            cursor.execute(s, [str(user_id), username, ""])
        # Set the password.
        auth_utils.set_password(username, password)
        # Set the birthday and invalidate the account creation key.
        s = """
      UPDATE members
      SET birthday = %s,
        create_account_key = NULL
      WHERE user_id = %s
      """
        with flask.g.pymysql_db.cursor() as cursor:
            cursor.execute(s, [birthday, str(user_id)])
        transaction.commit()
    except Exception:
        transaction.rollback()
        flask.flash(
            "An unexpected error occurred. Please contact devteam@donut.caltech.edu."
        )
        return False
    # Email the user.
    s = """
    SELECT first_name, email
    FROM members
      NATURAL JOIN users
    WHERE username = %s
    """
    with flask.g.pymysql_db.cursor() as cursor:
        cursor.execute(s, [username])
        result = cursor.fetchone()
    # Send confirmation email to user.
    email = result["email"]
    name = result["first_name"]
    msg = email_templates.CreateAccountSuccessfulEmail.format(name, username)
    subject = "Thanks for creating an account!"
    email_utils.send_email(email, msg, subject)
    return True


def handle_request_account(uid, last_name):
    """Handles a request to create an account.
  Checks that the email and UID match. If so, a create account link is sent to
  the user.
  Returns:
    Tuple (bool, string). The bool indicates success. If not successful,
    the string is an error message.
  """
    s = """
    SELECT first_name, last_name, email, username
    FROM members
      NATURAL LEFT JOIN users
    WHERE uid = %s
    """
    with flask.g.pymysql_db.cursor() as cursor:
        cursor.execute(s, [str(uid)])
        result = cursor.fetchone()
    if result is None or result["last_name"].lower() != last_name.lower():
        return (False, "Incorrect UID and/or name.")
    if result["username"] is not None:
        return (False, "You already have an account. Try recovering it?")
    email = result["email"]
    name = result["first_name"]

    # Generate a new account creation key.
    create_account_key = auth_utils.generate_create_account_key()
    s = """
    UPDATE members
    SET create_account_key = %s
    WHERE uid = %s
    """
    with flask.g.pymysql_db.cursor() as cursor:
        cursor.execute(s, [create_account_key, str(uid)])

    create_account_link = flask.url_for(
        "account.create_account",
        create_account_key=create_account_key,
        _external=True)
    msg = email_templates.CreateAccountRequestEmail.format(
        name, create_account_link)
    subject = "Account creation request"
    email_utils.send_email(email, msg, subject)
    return (True, "")
