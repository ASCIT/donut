import flask
import sqlalchemy


def get_group_list_data(fields=None, attrs={}):
    """
    Queries the database and returns list of group data constrained by the
    specified attributes.

    Arguments:
        fields: The fields to return. If None specified, then default_fields
                are used.
        attrs:  The attributes of the group to filter for.
    Returns:
        result: The fields and corresponding values of groups with desired
                attributes. In the form of a list of dicts with key:value of
                columnname:columnvalue.
    """
    all_returnable_fields = [
        "group_id", "group_name", "group_desc", "type", "anyone_can_send",
        "members_can_send", "newsgroups", "visible", "admin_control_members"
    ]
    default_fields = ["group_id", "group_name", "group_desc", "type"]
    if fields == None:
        fields = default_fields
    else:
        if any(f not in all_returnable_fields for f in fields):
            return "Invalid field"

    # Build the SELECT and FROM clauses
    s = sqlalchemy.sql.select(fields).select_from(sqlalchemy.text("groups"))

    # Build the WHERE clause
    for key, value in list(attrs.items()):
        s = s.where(sqlalchemy.text(key + "= :" + key))

    # Execute the query
    result = flask.g.db.execute(s, attrs).fetchall()

    # Return the rows in the form of a list of dicts
    result = [{f: t for f, t in zip(fields, res)} for res in result]
    return result


def get_group_data(group_id, fields=None):
    """
    Queries the databse and returns member data for the specified group_id.

    Arguments:
        group_id: The group to look up
        fields:   The fields to return. If None are specified, then
                  default_fields are used

    Returns:
        result:   The fields and corresponding values of group with group_id.
                  In the form of a dict with key:value of columnname:columnalue
    """
    all_returnable_fields = [
        "group_id", "group_name", "group_desc", "type", "anyone_can_send",
        "members_can_send", "newsgroups", "visible", "admin_control_members"
    ]
    default_fields = ["group_id", "group_name", "group_desc", "type"]
    if fields is None:
        fields = default_fields
    else:
        if any(f not in all_returnable_fields for f in fields):
            return "Invalid field"

    # Build the SELECT and FROM clauses
    s = sqlalchemy.sql.select(fields).select_from(sqlalchemy.text("groups"))

    # Build the WHERE clause
    s = s.where(sqlalchemy.text("group_id = :g"))

    # Execute the query
    result = flask.g.db.execute(s, g=group_id).first()

    # Check to see if query returned anything
    if result is None:
        return {}

    # Return the row in the form of a dict
    result = {f: t for f, t in zip(fields, result)}
    return result


def get_position_data(fields=None):
    all_returnable_fields = ["user_id", "group_id", "pos_id", "pos_name"]
    default_fields = ["user_id", "pos_id", "pos_name", "group_id"]

    if fields is None:
        fields = default_fields
    else:
        if any(f not in all_returnable_fields for f in fields):
            return "Invalid field"

    field_string = "positions.pos_id"
    for field in fields:
        if (field == "group_id"):
            field_string += ", positions.group_id"
        elif (field != "pos_id"):
            field_string += ", " + field

    
    result = flask.g.db.execute("SELECT " + field_string + "\nFROM positions NATURAL JOIN position_holders WHERE positions.pos_id = position_holders.pos_id;")

    if result is None:
        return {}

    user_position_arr = [{f: t for f, t in zip(fields, row)} for row in result]
    return user_position_arr
