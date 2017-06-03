import flask
import sqlalchemy

def get_member_data(user_id, fields=None):
    """
    Queries the database and returns member data for the specified user_id.

    Arguments:
        user_id: The member to look up
        fields:  The fields to return. If None specified, then default_fields
                 are used.
    Returns:
        result: The fields and corresponding values of member with user_id. In
                the form of a dict with key:value of columnname:columnvalue.
    """
    all_returnable_fields = ["user_id", "uid", "last_name", "first_name", 
            "middle_name", "email", "phone", "gender", "gender_custom", 
            "birthday", "entry_year", "graduation_year", "msc", "building",
            "room_num", "address", "city", "state", "zip", "country"]
    default_fields = ["user_id", "first_name", "last_name", "email", "uid",
              "entry_year", "graduation_year"]
    if fields == None:
        fields = default_fields
    else:
        if any(f not in all_returnable_fields for f in fields):
            return "Invalid field"

    # Build the SELECT and FROM clauses
    s = sqlalchemy.sql.select(fields).select_from(sqlalchemy.text("members"))

    # Execute the query
    result = flask.g.db.execute(s, user_id=user_id).first()
    
    # Return the row in the form of a of dict
    result = { f:t for f,t in zip(fields, result) }
    return result


def get_member_list_data(fields=None, attrs={}):
    """
    Queries the database and returns list of member data constrained by the 
    specified attributes.

    Arguments:
        fields: The fields to return. If None specified, then default_fields
                are used.
        attrs:  The attributes of the members to filter for.
    Returns:
        result: The fields and corresponding values of members with desired
                attributes. In the form of a list of dicts with key:value of 
                columnname:columnvalue.
    """
    all_returnable_fields = ["user_id", "uid", "last_name", "first_name", 
            "middle_name", "email", "phone", "gender", "gender_custom", 
            "birthday", "entry_year", "graduation_year", "msc", "building",
            "room_num", "address", "city", "state", "zip", "country"]
    default_fields = ["user_id", "first_name", "last_name", "email", "uid",
              "entry_year", "graduation_year"]
    if fields == None:
        fields = default_fields
    else:
        if any(f not in all_returnable_fields for f in fields):
            return "Invalid field"

    # Build the SELECT and FROM clauses
    s = sqlalchemy.sql.select(fields).select_from(sqlalchemy.text("members"))
    
    # Build the WHERE clause 
    for key, value in attrs.items():
        s = s.where(sqlalchemy.text(key + "= :" + key))

    # Execute the query
    result = flask.g.db.execute(s, attrs).fetchall()
    
    # Return the rows in the form of a list of dicts
    result = [{ f:t for f,t in zip(fields, res) } for res in result]
    return result

def get_organization_data(org_id, fields=None):
    """
    Queries the database and returns organization data for the specified org_id.

    Arguments:
        org_id: The member to look up
        fields:  The fields to return. If None specified, then default_fields
                 are used.
    Returns:
        result: The fields and corresponding values of organization with org_id. In
                the form of a dict with key:value of columnname:columnvalue.
    """
    all_returnable_fields = ["org_id", "org_name", "type"]
    default_fields = ["org_id", "org_name", "type"]
    if fields == None:
        fields = default_fields
    else:
        if any(f not in all_returnable_fields for f in fields):
            return "Invalid field"

    # Build the SELECT and FROM clauses
    s = sqlalchemy.sql.select(fields).select_from(sqlalchemy.text("organizations"))

    # Execute the query
    result = flask.g.db.execute(s, org_id=org_id).first()
    
    # Return the row in the form of a of dict
    result = { f:t for f,t in zip(fields, result) }
    return result


def get_organization_list_data(fields=None, attrs={}):
    """
    Queries the database and returns list of organization data constrained by the 
    specified attributes.

    Arguments:
        fields: The fields to return. If None specified, then default_fields
                are used.
        attrs:  The attributes of the organizations to filter for.
    Returns:
        result: The fields and corresponding values of organizations with desired
                attributes. In the form of a list of dicts with key:value of 
                columnname:columnvalue.
    """
    all_returnable_fields = ["org_id", "org_name", "type"]
    default_fields = ["org_id", "org_name", "type"]
    if fields == None:
        fields = default_fields
    else:
        if any(f not in all_returnable_fields for f in fields):
            return "Invalid field"

    # Build the SELECT and FROM clauses
    s = sqlalchemy.sql.select(fields).select_from(sqlalchemy.text("organizations"))
    
    # Build the WHERE clause 
    for key, value in attrs.items():
        s = s.where(sqlalchemy.text(key + "= :" + key))

    # Execute the query
    result = flask.g.db.execute(s, attrs).fetchall()
    
    # Return the rows in the form of a list of dicts
    result = [{ f:t for f,t in zip(fields, res) } for res in result]
    return result

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
    all_returnable_fields = ["group_id", "group_name", "group_desc"] 
    default_fields = ["group_id", "group_name", "group_desc"]
    if fields == None:
        fields = default_fields
    else:
        if any(f not in all_returnable_fields for f in fields):
            return "Invalid field"

    # Build the SELECT and FROM clauses
    s = sqlalchemy.sql.select(fields).select_from(sqlalchemy.text("groups"))
    
    # Build the WHERE clause 
    for key, value in attrs.items():
        s = s.where(sqlalchemy.text(key + "= :" + key))

    # Execute the query
    result = flask.g.db.execute(s, attrs).fetchall()
    
    # Return the rows in the form of a list of dicts
    result = [{ f:t for f,t in zip(fields, res) } for res in result]
    return result





