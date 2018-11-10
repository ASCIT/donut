import enum


class bod_permissions(enum.IntEnum):
    # view the summary page (BoD members only)
    SUMMARY = 8
    TOGGLE_READ = 9
    ADD_REMOVE_EMAIL = 10
    VIEW_EMAILS = 11
