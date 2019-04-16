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


CONTACTS = {
    'Administration': [{
        'name': 'Kevin Gilmartin',
        'role': 'Dean of Undergraduate Students',
        'email': 'kmg@hss.caltech.edu'
    }, {
        'name': 'Lesley Nye',
        'role': 'Dean of Undergraduate Students',
        'email': 'lnye@caltech.edu'
    }, {
        'name': 'Kristin Weyman',
        'role': 'Associate Dean of Undergraduate Students',
        'email': 'kweyman@caltech.edu'
    }, {
        'name': 'Beth Larranaga',
        'role': 'Office Manager',
        'email': 'rosel@caltech.edu'
    }, {
        'name': 'Sara Loredo',
        'role': 'Office Assistant',
        'email': 'sara@caltech.edu'
    }],
    'Student Life': [{
        'name':
        'Tom Mannion',
        'role':
        'Senior Director, Student Activities and Programs',
        'email':
        'mannion@caltech.edu'
    }, {
        'name': 'Joe Shepherd',
        'role': 'Vice President for Student Affairs',
        'email': 'joseph.e.shepherd@caltech.edu'
    }, {
        'name':
        'Felicia Hunt',
        'role':
        'Assistant Vice President for Student Affairs and Residential Experience',
        'email':
        'fhunt@caltech.edu'
    }, {
        'name': 'Maria Katsas',
        'role': 'Director of Housing',
        'email': 'maria@caltech.edu'
    }, {
        'name':
        'Allie McIntosh',
        'role':
        'Community Educator and Deputy Title IX Coordinator',
        'email':
        'allie@caltech.edu'
    }, {
        'name': 'Jaime Reyes',
        'role': 'Acting Director of Dining Services',
        'email': 'reyes@caltech.edu'
    }]
}
