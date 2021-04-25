import re
import datetime
import flask
import pymysql.cursors

from donut import constants

username_regex = re.compile(r'^[a-z][a-z0-9_-]*$', re.I)
name_regex = re.compile(r"^[a-z][a-z '-]{0,30}[a-z]$", re.I)
uid_regex = re.compile(r'^[0-9]{7}$')
year_regex = re.compile(r'^[0-9]{4}$')
email_regex = re.compile(r'^[a-z0-9\.\_\%\+\-]+@[a-z0-9\.\-]+\.[a-z]+$', re.I)


def validate_username(username, flash_errors=True):
    """
  Checks to make sure username is valid. If flash_errors is True, then the
  errors will be displayed as flashes. Returns True if valid, else False.
  """
    error = None
    if len(username) == 0:
        error = 'You must provide a username!'
    elif len(username) < constants.MIN_USERNAME_LENGTH:
        error = 'Username must be at least {0} characters long!'.format(
            constants.MIN_USERNAME_LENGTH)
    elif len(username) > constants.MAX_USERNAME_LENGTH:
        error = 'Username cannot be more than {0} characters long!'.format(
            constants.MAX_USERNAME_LENGTH)
    elif username_regex.match(username) is None:
        error = 'Username may contain only alphanumeric characters, hyphens, or underscores and must begin with a letter.'
    else:
        # Check if username is already in use.
        query = "SELECT 1 FROM users WHERE username = %s"
        with flask.g.pymysql_db.cursor() as cursor:
            cursor.execute(query, username)
            result = cursor.fetchone()
        if result is not None:
            error = 'Username is already in use!'

    if error is not None:
        if flash_errors:
            flask.flash(error)
        return False
    return True


def validate_password(password, password2, flash_errors=True):
    """
  Checks to make sure a password is valid. password and password2 should be the
  values from both times the user enters a password. If you need to check a
  password outside of the context of a user setting/changing a password, then
  use the same value for both inputs. If flash_errors is set to True, then the
  errors will be displayed as flashes.
  Returns True if valid, else False.
  """
    error = None
    if len(password) == 0:
        error = 'You must provide a password!'
    elif len(password2) == 0:
        error = 'You must confirm your password!'
    elif password != password2:
        error = 'Passwords do not match. Please try again!'
    elif len(password) < constants.MIN_PASSWORD_LENGTH:
        error = 'Your password must be at least {0} characters long!'.format(
            constants.MIN_PASSWORD_LENGTH)
    elif len(password) > constants.MAX_PASSWORD_LENGTH:
        error = 'Your password cannot be more than {0} characters long!'.format(
            constants.MAX_PASSWORD_LENGTH)

    if error is not None:
        if flash_errors:
            flask.flash(error)
        return False
    return True


def validate_name(name, flash_errors=True):
    """Validates a name. Flashes errors if flash_errors is True."""
    # Allow letters, spaces, hyphens, and apostrophes.
    # First and last characters must be letters.
    if not name_regex.match(name):
        if flash_errors:
            flask.flash("'{0}' is not a valid name.".format(name))
        return False
    return True


def validate_uid(uid, flash_errors=True):
    """Validates a UID. Flashes errors if flash_errors is True."""
    if not uid_regex.match(uid):
        if flash_errors:
            flask.flash("'{0}' is not a valid UID.".format(uid))
        return False
    return True


def check_uid_exists(uid):
    """Returns True if the UID exists in the database."""
    if not validate_uid(uid, flash_errors=False):
        return False

    query = "SELECT 1 FROM members WHERE uid = %s"
    with flask.g.pymysql_db.cursor() as cursor:
        cursor.execute(query, uid)
        result = cursor.fetchone()
    return result is not None


def validate_year(year, flash_errors=True):
    """Validates a year. Flashes errors if flash_errors is True."""
    # Also check that the year is in the range supported by MySQL's year type.
    if year_regex.match(year) \
        and int(year) >= 1901 \
        and int(year) <= 2155:
        return True
    if flash_errors:
        flask.flash("'{0}' is not a valid year.".format(year))
    return False


def validate_email(email, flash_errors=True):
    """Validates an email. Flashes errrors if flash_errors is True."""
    if not email_regex.match(email):
        if flash_errors:
            flask.flash("'{0}' is not a valid email.".format(email))
        return False
    return True


def validate_date(date, flash_errors=True):
    """
  Validates date string. Format should be YYYY-MM-DD. Flashes errors if
  flash_errors is True.
  """
    try:
        datetime.datetime.strptime(date, '%Y-%m-%d')
    except ValueError:
        if flash_errors:
            flask.flash(
                'Invalid date provided. Make sure dates are in YYYY-MM-DD format.'
            )
        return False
    return True


def validate_exists(form, param, flash_errors=True):
    """
    Validates that the specified parameter exists in the POST data
    """
    if param not in form:
        if flash_errors:
            flask.flash("Missing form parameter: " + param)
        return False
    return True


def validate_in(value, values, flash_errors=True):
    """
    Validates that value is in the iterable values
    """
    if value not in values:
        if flash_errors:
            flask.flash("'" + value + "' not in " + str(values))
        return False
    return True


def validate_int(int_str, min=None, max=None, flash_errors=True):
    """
    Requires that the given string represent an integer
    and the integer lies between the bounds (inclusive) if provided
    """
    try:
        int_value = int(int_str)
    except ValueError:
        if flash_errors:
            flask.flash("Not an integer: '" + int_str + "'")
        return False

    if not ((min is None or min <= int_value) and
            (max is None or int_value <= max)):
        if flash_errors:
            flask.flash("Not between " + str(min) + " and " + str(max) + ": " +
                        int_str)
        return False

    return True


def validate_matches(value1, value2, flash_errors=True):
    """
    Validates that the two values match
    """
    matches = value1 == value2
    if not matches and flash_errors:
        flask.flash(repr(value1) + " and " + repr(value2) + " do not match")
    return matches


def validate_length(value, min_len=None, max_len=None, flash_errors=True):
    """
    Validates that the given string is between the length bounds (inclusive)
    """
    length = len(value)
    if not ((min_len is None or min_len <= length) and
            (max_len is None or length <= max_len)):
        if flash_errors:
            flask.flash("Length not between " + str(min_len) + " and " +
                    str(max_len) + ": got \"" + value  + "\" of length " + 
                    str(length))
        return False
    return True
