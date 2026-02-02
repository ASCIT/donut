import enum


class Permissions(enum.IntEnum):
    # Permission to manage all groups (create/edit/delete groups and positions)
    GROUP_EDITORS = 42
