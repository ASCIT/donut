import flask
import sqlalchemy


def get_BoC_member():
    """
    Queries the database and returns list of people on BoC
    """
    sqlText1 = "groups NATURAL JOIN positions NATURAL JOIN position_holders "
    sqlText2 = "NATURAL JOIN members"
    s = sqlalchemy.sql.select(["first_name, last_name, pos_name, email"]).select_from(sqlalchemy.text(sqlText1 + sqlText2))

    s = s.where(sqlalchemy.text("group_name = 'BoC'"))
    result = flask.g.db.execute(s)

    high_pos = []
    pos_house = []
    counter = 0
    for fname, lname, pos_name, email in result:
        name = fname + lname
        if pos_name == 'Chair' or 'ecretary' in pos_name:
            high_pos.append((name, pos_name, email))
        else:
            pos_house.append((name, pos_name, email))

    high_pos.sort(key=lambda tup:tup[1])
    pos_house.sort(key=lambda tup:tup[1])

    fin_result = high_pos + pos_house

    return fin_result

def get_CRC_member():
    """
    Queries the database and returns list of people on CRC
    """
    sqlText1 = "groups NATURAL JOIN positions NATURAL JOIN position_holders "
    sqlText2 = "NATURAL JOIN members"
    s = sqlalchemy.sql.select(["first_name, last_name, pos_name, email"]).select_from(sqlalchemy.text(sqlText1 + sqlText2))

    s = s.where(sqlalchemy.text("group_name = 'CRC'"))
    result = flask.g.db.execute(s)

    high_pos = []
    pos_house = []
    counter = 0
    for fname, lname, pos_name, email in result:
        name = fname + lname
        if pos_name == 'Chair' or 'ecretary' in pos_name:
            high_pos.append((name, pos_name, email))
        else:
            pos_house.append((name, pos_name, email))

    high_pos.sort(key=lambda tup:tup[1])
    pos_house.sort(key=lambda tup:tup[1])

    fin_result = high_pos + pos_house

    return fin_result

