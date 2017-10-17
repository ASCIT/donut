from enum import Enum

# Enum for group types in the groups table
class GroupTypes(Enum):
    # For all groups that represent a house
    HOUSE = 'house'
    # For all groups that are committees
    COMMITTEE = 'committee'
    # For all groups that are invovled with ascit
    ASCIT = 'ascit'
    # For all groups that are publications (i.e. The Tech)
    PUBLICATION = 'publication'
    # For all groups that are associated with current undergrad students
    # i.e ug2020
    UGCURRENT = 'ugcurrent'
    # For all groups that are associated with alumnus
    # i.e ug2010
    UGALUMN = 'ugalumn' 
