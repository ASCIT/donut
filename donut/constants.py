"""Store various constants here"""
from enum import Enum

# Maximum file upload size (in bytes).
MAX_CONTENT_LENGTH = 10 * 1024 * 1024
MAX_CONTENT_LENGTH_STRING = '10 MB'

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
        'name': 'Jennifer Jahner',
        'role': 'Dean of Undergraduate Studies',
        'email': 'jahner@hss.caltech.edu'
    }, {
        'name': 'Lesley Nye',
        'role': 'Senior Associate Dean',
        'email': 'lnye@caltech.edu'
    }, {
        'name': 'Kristin Weyman',
        'role':
        'Associate Dean for Undergraduate Students and Dean of First and Second Year Students',
        'email': 'kweyman@caltech.edu'
    }, {
        'name': 'Maura McDinger',
        'role': 'Director of Conduct and Community Standards',
        'email': 'mmcdinge@caltech.edu'
    }, {
        'name': 'Therese Bagsit',
        'role': 'Operations Lead',
        'email': 'bagsit@caltech.edu'
    }, {
        'name': 'Sara Loredo',
        'role': 'Office Assistant',
        'email': 'sara@caltech.edu'
    }],
    'Student Life': [{
        'name':
        'Tom Mannion',
        'role':
        'Senior Director of Campus Activities and Engagement',
        'email':
        'mannion@caltech.edu'
    }, {
        'name':
        'Kevin Gilmartin',
        'role':
        'Vice President for Student Affairs and Faculty Dean of Students',
        'email':
        'kmg@hss.caltech.edu'
    }, {
        'name':
        'Joseph Greenwell',
        'role':
        'Associate Vice President for Student Life and Chief Student Affairs Officer',
        'email':
        'jgreenwe@caltech.edu'
    }, {
        'name':
        'Felicia Hunt',
        'role':
        'Assistant Vice President for Student Affairs and Student And Family Engagement',
        'email':
        'fhunt@caltech.edu'
    }, {
        'name': 'Maria Katsas',
        'role': 'Executive Director, Student Auxiliary Services',
        'email': 'maria@caltech.edu'
    }, {
        'name': 'Lynzie De Veres',
        'role': 'Assistant Vice President for Equity and Equity Investigations, Title IX Coordinator',
        'email': 'ldeveres@caltech.edu'
    }]
}
