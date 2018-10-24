"""
Tests donut/auth_utils.py.
"""
import random
import pytest
import binascii
import hashlib

from donut import auth_utils
from donut import misc_utils
from donut import constants
from donut.testing.fixtures import client


def test_hash_password():
    """
  Tests each hash algorithm implemented by hash_password().
  """
    PWD_LENGTH = 64
    password = misc_utils.generate_random_string(PWD_LENGTH)
    salt = auth_utils.generate_salt()

    # PBKDF2_SHA256
    rounds = 100000
    expected_result = binascii.hexlify(
        hashlib.pbkdf2_hmac('sha256', password.encode(), salt.encode(),
                            rounds)).decode()
    result = auth_utils.hash_password(password, salt, rounds, 'pbkdf2_sha256')
    assert result == expected_result

    # MD5
    expected_result = hashlib.md5((salt + password).encode()).hexdigest()
    result = auth_utils.hash_password(password, salt, None, 'md5')
    assert result == expected_result


def test_parser():
    """
  Tests PasswordHashParser implementation.
  """
    PWD_LENGTH = 64
    password = misc_utils.generate_random_string(PWD_LENGTH)
    wrong_password = misc_utils.generate_random_string(PWD_LENGTH)
    assert password != wrong_password

    # Test pbkdf2_sha256(md5(password)).
    md5_salt = auth_utils.generate_salt()
    pbkdf2_sha256_salt = auth_utils.generate_salt()
    pbkdf2_sha256_rounds = 100000

    password_hash = auth_utils.hash_password(password, md5_salt, None, 'md5')
    password_hash = auth_utils.hash_password(password_hash, pbkdf2_sha256_salt,
                                             pbkdf2_sha256_rounds,
                                             'pbkdf2_sha256')

    hash_string = "$md5|pbkdf2_sha256$|{}${}|{}${}".format(
        pbkdf2_sha256_rounds, md5_salt, pbkdf2_sha256_salt, password_hash)

    parser = auth_utils.PasswordHashParser()
    parser.parse(hash_string)

    assert parser.verify_password(password) == True
    assert parser.verify_password(wrong_password) == False
    assert str(parser) == hash_string


def test_compare_secure_strings():
    """
  Tests that compare_secure_strings() returns True when the strings are equal
  and False otherwise. Does not test if the function actually mitigates timing
  side channel attacks.
  """
    LENGTH = 128
    string1 = misc_utils.generate_random_string(LENGTH)
    string2 = misc_utils.generate_random_string(LENGTH)
    assert string1 != string2

    # Make sure compare_secure_strings returns True and False when expected.
    assert misc_utils.compare_secure_strings(string1, string1) == True
    assert misc_utils.compare_secure_strings(string1, string2) == False


def test_get_permissions(client):
    res = auth_utils.get_permissions('dqu')
    assert res == set([1, 3])

    res = auth_utils.get_permissions('reng')
    assert res == set([1, 2, 3])

    res = auth_utils.get_permissions('notreal_user')
    assert res == set()


def test_check_permission(client):
    assert auth_utils.check_permission('dqu', 1)
    assert auth_utils.check_permission('reng', 2)
    assert not auth_utils.check_permission('reng', -1)
