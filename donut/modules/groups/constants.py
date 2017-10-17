from enum import Enum

# Enum for group types in the groups table
class GroupTypes(Enum):
    HOUSE = 'house'
    COMMITTEE = 'committee' # i.e IHC, BOC, CRC
    ASCIT = 'ascit' # For all groups that are involved with ascit
    PUBLICATION = 'publication' # i.e The Tech
    UGCURRENT = 'ugcurrent' # current student groups i.e ug2020
    UGALUMN = 'ugalumn' # alumn groups, i.e ug2010 
