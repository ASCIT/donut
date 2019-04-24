"""Store various constants here"""
from enum import Enum

# Maximum file upload size (in bytes).
MAX_CONTENT_LENGTH = 1 * 1024 * 1024 * 1024

# Authentication/account creation constants
PWD_HASH_ALGORITHM = 'pbkdf2_sha256'
SALT_SIZE = 24
MIN_USERNAME_LENGTH = 2
MAX_USERNAME_LENGTH = 32
MIN_PASSWORD_LENGTH = 8
MAX_PASSWORD_LENGTH = 1024
HASH_ROUNDS = 100000
PWD_RESET_KEY_LENGTH = 32
# Length of time before recovery key expires, in minutes.
PWD_RESET_KEY_EXPIRATION = 1 * 24 * 60
CREATE_ACCOUNT_KEY_LENGTH = 32


class Gender(Enum):
    """Value of members.gender if member's gender is unknown"""
    NO_GENDER = None
    """Value of members.gender if member is female"""
    FEMALE = 0
    """Value of members.gender if member is male"""
    MALE = 1


registrar_gender = {
    'F': Gender.FEMALE.value,
    'M': Gender.MALE.value,
}

registrar_month = {
    'JAN': 1,
    'FEB': 2,
    'MAR': 3,
    'APR': 4,
    'MAY': 5,
    'JUN': 6,
    'JUL': 7,
    'AUG': 8,
    'SEP': 9,
    'OCT': 10,
    'NOV': 11,
    'DEC': 12,
}

registrar_column_labels = [
    'uid', 'last_name', 'first_name', 'preferred_name',
    'middle_name', 'email', 'phone', 'gender', 'birthday', 'msc',
    'address', 'city', 'state', 'zip', 'country',
]
