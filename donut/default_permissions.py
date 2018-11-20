'''
Use this file to store names for global permissions -- permissions
that don't belong in any particular module. 

For module specific permissions, create an Enum within the module
'''

import enum


class Permissions(enum.IntEnum):
    #Site admins -- always have permission to everything -- Use with caution
    ADMIN = 1
