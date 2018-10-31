import enum

class arc_permissions(enum.IntEnum):
    # view the summary page (ARC members only)
    SUMMARY = 4
    TOGGLE_READ = 5
    ADD_REMOVE_EMAIL = 6
    VIEW_EMAILS = 7
