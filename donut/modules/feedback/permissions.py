import enum


class BOD_PERMISSIONS(enum.IntEnum):
    # view the summary page (BoD members only)
    SUMMARY = 8
    TOGGLE_READ = 9
    ADD_REMOVE_EMAIL = 10
    VIEW_EMAILS = 11


class ARC_PERMISSIONS(enum.IntEnum):
    SUMMARY = 13
    TOGGLE_READ = 14
    ADD_REMOVE_EMAIL = 15
    VIEW_EMAILS = 16


class DONUT_PERMISSIONS(enum.IntEnum):
    SUMMARY = 17
    TOGGLE_READ = 18
    ADD_REMOVE_EMAIL = 19
    VIEW_EMAILS = 20
