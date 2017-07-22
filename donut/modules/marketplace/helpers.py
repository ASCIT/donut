import flask
import sqlalchemy
from datetime import date, datetime

import routes


def render_top_marketplace_bar(template_url, **kwargs):
    """
    Provides an easy way for routing functions to pass the variables required for
    rendering the marketplace's top bar to render_template.  Basically chains
    some other arguments on to the render call, namely the list of marketplace
    categories, the list urls to categories, and the width of each url column.

    Arguments:
        template_url: The url which is being rendered.
        **kwargs: The variables which are used to render the rest of the page.

    Returns:
        The result of render_template(): Whatever magic Flask does to render the
                                         final page.
    """
    query = sqlalchemy.sql.select(["cat_title"]).select_from(sqlalchemy.text("marketplace_categories"))
    result = flask.g.db.execute(query)

    # Convert result, in the form of a strange SQL object, into an array,
    # so that we can retrieve the length without having to execute a special
    # length query or anything.
    categories = []
    for column in result:
        categories.append(column[0])

    # Get number of rows and columns to display categories nicely. This is a
    # little tricky - we want to aim for a table with either 4 categories or 5
    # categories per row, with the last row catching the remainder. However, we
    # want to avoid having exactly 1 category in the remainder row if possible.
    num_cats = len(categories);
    num_cols = num_cats
    if num_cats <= 5:
        num_cols = num_cats
    elif num_cats % 5 == 0:
        num_cols = 5
    elif num_cats % 4 == 0:
        num_cols = 4
    elif num_cats % 5 == 4:
        num_cols = 5
    elif num_cats % 4 == 3:
        num_cols = 4
    elif num_cats % 5 != 1:
        num_cols = 5
    elif num_cats % 4 != 1:
        num_cols = 4
    else:
        num_cols = 5

    num_rows = num_cats // num_cols

    # Break categories into a 2d array so that it's easy to arrange in rows
    # in the html file.
    cats2d = [[]] * num_rows
    for cat_index in range(len(categories)):
        cats2d[cat_index / num_cols].append(categories[cat_index])

    # This is simpler than a bootstrap col-sm-something, since we want a variable number of columns.
    width = "width: " + str(100.0 / (num_cols)) + "%"

    # Pass the 2d category array, urls array, and width string, along with the arguments passed in to this
    # function, on to Flask in order to render the top bar and the rest of the content.
    return flask.render_template(template_url, cats=cats2d, width=width, **kwargs)


def get_marketplace_items_list_data(fields=None, attrs={}):
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
    all_returnable_fields = ["item_id", "cat_id", "user_id", "item_title", "item_details",
                             "item_condition", "item_price", "item_timestamp", "item_active",
                             "textbook_id", "textbook_edition", "textbook_isbn"]
    default_fields = all_returnable_fields
    if fields == None:
        fields = default_fields
    else:
        if any(f not in all_returnable_fields for f in fields):
            return "Invalid field"

    # Build the SELECT and FROM clauses
    s = sqlalchemy.sql.select(fields).select_from(sqlalchemy.text("marketplace_items"))

    # Build the WHERE clause
    for key, value in attrs.items():
        s = s.where(sqlalchemy.text(key + "= :" + key))

    # Execute the query
    result = flask.g.db.execute(s, attrs).fetchall()
    sanitized_res = []

    # Sanitize the data to be able to JSONify it
    # Probably will remove this when we get the real tables working, since
    # we really don't need a REST API, but for now it's good to see that the code is working
    for item_listing in result:
        temp_row = []
        for data in item_listing:
            if isinstance(data, (datetime, date)):
                temp_row.append(data.strftime("%m/%d/%y"))
            elif data == None:
                temp_row.append("")
            else:
                try:
                    temp_row.append(float(data))
                except:
                    temp_row.append(data)
        sanitized_res.append(temp_row)

    # Return the row in the form of a of dict
    result = [{ f:t for f,t in zip(fields, res) } for res in sanitized_res]
    print(get_textbook_info_from_textbook_id(1))

    return result


def get_name_from_user_id(user_id):
    """
    Queries the database and returns the full name (first and last) of the user with the specified user id (NOT UID).

    Arguments:
        user_id: The user id of the requested user (NOT UID).
    Returns:
        result: A string of the user's full name.
                (first + " " + last)
    """
    query = sqlalchemy.text("""SELECT first_name, last_name FROM members WHERE user_id=:user_id""")
    result = flask.g.db.execute(query, user_id=user_id).first()
    return " ".join(result)


def get_textbook_info_from_textbook_id(textbook_id):
    """
    Queries the database and returns the title and author of the textbook with the specified id.

    Arguments:
        textbok_id: The id of the requested textbook.
    Returns:
        result: A list of the textbook title and author.
    """
    query = sqlalchemy.text("""SELECT textbook_title, textbook_author FROM marketplace_textbooks WHERE textbook_id=:textbook_id""")
    result = flask.g.db.execute(query, textbook_id=textbook_id).first()
    return list(result)
