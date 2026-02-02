import enum


class Permissions(enum.IntEnum):
    # Permission to access GPT-SAM chatbot
    # Granted via position_permissions to ASCIT and IHC members
    GPT_SAM = 43
