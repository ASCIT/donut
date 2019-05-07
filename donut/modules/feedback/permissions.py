import enum


class BOD_PERMISSIONS(enum.IntEnum):
    # view the summary page (BoD members only)
    SUMMARY = 8
    TOGGLE_READ = 9
    ADD_REMOVE_EMAIL = 10
    VIEW_EMAILS = 11


class ARC_PERMISSIONS(enum.IntEnum):
    SUMMARY = 12
    TOGGLE_READ = 13
    ADD_REMOVE_EMAIL = 14
    VIEW_EMAILS = 15
