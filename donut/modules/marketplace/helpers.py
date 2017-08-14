import flask
import sqlalchemy
import re

from donut.modules.core.helpers import get_member_data

import routes

# taken from donut-legacy, which was apparently taken from a CS11
# C++ assignment by dkong
skip_words = ["a", "all", "am", "an", "and", "are", "as", "at",
        "be", "been", "but", "by",
        "did", "do",
        "for", "from",
        "had", "has", "have", "he", "her", "hers", "him", "his",
        "i", "if", "in", "into", "is", "it", "its",
        "me", "my",
        "not",
        "of", "on", "or",
        "so",
        "that", "the", "their", "them", "they", "this", "to",
        "up", "us",
        "was", "we", "what", "who", "why", "will", "with",
        "you", "your"]


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
    # Thus we do our best to prevent num_cats % num_cols from being 1.
    num_cats = len(categories);
    if num_cats <= 5:
        num_cols = num_cats
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


def generate_search_table(fields=None, attrs={}):
    """
    Provides a centralized way to generate the 2d array of cells that is displayed
    in a table, along with all the stuff that needs to be packaged with it.  Calls
    a few functions further down to get the data, merge some columns, and rename
    the headers.

    Arguments:
        fields: A list of the fields that are requested to be in the table.  For
                example: ["cat_id", "item_title", "textbook_title", "item_price",
                ...]

        attrs: A map of fields to values that make up conditions on the fields.
               For example, {"cat_id":1} will only return results for which the
               category id is 1.

    Returns:
        result: The 2d array that was requested.

        headers: The English-ified headers for each column.

        links: A 2d array that, in each cell, gives the url of the link that
               clicking on the corresponding cell in result should yield.  If none,
               the cell will contain the number 0 instead.
    """

    # we need the item_id to generate the urls that clicking on the item title
    # should go to.
    # also, we add it to the front so that we can get the id before we need to use
    # it (i.e., when we're adding it to links)
    fields = ["item_id"] + fields

    result = get_marketplace_items_list_data(fields, attrs)
    (result, fields) = merge_titles(result, fields)

    sanitized_res = []
    links = []

    # Format the data, parsing the timestamps and converting the ids to
    # actual information
    for item_listing in result:
        temp_res_row = []
        temp_link_row = []
        item_listing = list(item_listing)
        field_index = 0
        for data in item_listing:
            added_link = False
            if data == None:
                temp_res_row.append("")
            else:
                if fields[field_index] == "item_timestamp":
                    temp_res_row.append(data.strftime("%m/%d/%y"))

                elif fields[field_index] == "user_id":
                    temp_link_row.append("")
                    added_link = True

                    temp_res_row.append(get_name_from_user_id(int(data)))

                elif fields[field_index] == "textbook_edition":
                    temp_res_row.append(process_edition(data))

                elif fields[field_index] == "cat_id":
                    temp_res_row.append(get_category_name_from_id(int(data)))

                elif fields[field_index] == "item_title" or fields[field_index] == "textbook_title":
                    temp_link_row.append("")
                    # it'll be a url_for for some route (that I haven't
                    # implemented yet but whatever)
                    #
                    added_link = True

                    temp_res_row.append(data)

                else:
                    temp_res_row.append(data)

            if not added_link:
                temp_link_row.append(0)
            field_index += 1

        # strip off the item_id column we added at the beginning of the function
        temp_res_row = temp_res_row[1:]
        temp_link_row = temp_link_row[1:]

        # add our temporary rows to the real 2d arrays that we'll return
        sanitized_res.append(temp_res_row)
        links.append(temp_link_row)

    fields = fields[1:] # strip off the item_id column we added at the beginning

    headers = process_category_headers(fields)

    return (sanitized_res, headers, links)


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
                attributes. In the form of a list of lists.
    """
    all_returnable_fields = ["item_id", "cat_id", "user_id", "item_title", "item_details",
                             "item_condition", "item_price", "item_timestamp", "item_active",
                             "textbook_title", "textbook_author", "textbook_edition", "textbook_isbn"]
    default_fields = all_returnable_fields

    if fields == None:
        fields = default_fields
    else:
        if any(f not in all_returnable_fields for f in fields):
            return "Invalid field"


    # Build the SELECT and FROM clauses
    s = sqlalchemy.sql.select(fields).select_from(sqlalchemy.text("marketplace_items INNER JOIN marketplace_textbooks"))

    # Build the WHERE clause
    for key, value in attrs.items():
        s = s.where(sqlalchemy.text(key + "= :" + key))

    # Execute the query
    result = flask.g.db.execute(s, attrs).fetchall()
    # Return the list of lists
    for i in range(len(result)):
        result[i] = list(result[i])
    return result


def merge_titles(datalist, fields):
    """
    Takes datalist and merges the two columns, item_title and textbook_title.

    Arguments:
        datalist: a 2d list of data, with columns determined by fields
        fields: the column titles from the SQL tables

    Returns:
        datalist: the original table, but with the two columns merged
        fields: the column titles similarly merged together into item_title
    """
    item_index = -1
    textbook_index = -1
    for i in range(len(fields)):
        if fields[i] == "item_title":
            item_index = i
        if fields[i] == "textbook_title":
            textbook_index = i

    if item_index == -1 or textbook_index == -1:
        # can't merge, since the two columns aren't there
        return (datalist, fields)

    for row_index in range(len(datalist)):
        row = datalist[row_index]
        if row[item_index] == "":
            row[item_index] = row[textbook_index]
        del row[textbook_index]
        datalist[row_index] = row
    del fields[textbook_index]
    return (datalist, fields)


def process_category_headers(fields):
    """
    Converts fields from sql headers to English.

    Arguments:
        fields: the list of fields that will be changed into the headers that are returned

    Returns:
        headers: the list of headers that will become the headers of the tables
    """
    headers = []
    for i in fields:
        if i == "item_title":
            headers.append("Item")
        elif i == "item_price":
            headers.append("Price")
        elif i == "user_id":
            headers.append("Sold by")
        elif i == "item_timestamp":
            headers.append("Date")
        elif i == "textbook_title":
            headers.append("Title")
        elif i == "textbook_author":
            headers.append("Author")
        elif i == "textbook_edition":
            headers.append("Edition")
        elif i == "cat_id":
            headers.append("Category")
    return headers


def tokenize_query(query):
    """
    Turns a string with a query into a list of tokens that represent the query.
    """
    global skip_words
    tokens = []

    query = query.split()
    # Validate ISBNs before we remove hyphens
    for token_index in range(len(query)):
        token = query[token_index]
        if(validate_isbn(token)):
            tokens.append(token)
            del query[token_index]

    query = " ".join(query)
    # Remove punctuation
    punctuation = [",", ".", "-", "_", "!", ";", ":", "/", "\\"]
    for p in punctuation:
        query = query.replace(p, " ")
    query = query.split()

    # if any of the words in query are in our skip_words, don't add them
    # to tokens
    for token in query:
        if True:
            pass

    return tokens

def validate_isbn(isbn):
    """
    Determines whether an ISBN is valid or not.  Works with ISBN-10 and ISBN-13,
    validating the length of the string and the check digit as well.

    Arguments:
        isbn: The ISBN, in the form of a string.
    Returns:
        valid: Whether or not the isbn is valid.
    """
    if type(isbn) != str:
        return False

    # hyphens are annoying but there should never be one at start or end,
    # nor should there be two in a row.
    if isbn[0] == "-" or isbn[-1] == "-" or "--" in isbn:
        return False

    # now that we've done that we can remove them
    isbn.replace("-", "")

    # regexes shamelessly copypasted
    # the ISBN-10 can have an x at the end (but the ISBN-13 can't)
    if re.match("^[0-9]{9}[0-9x]$", isbn, re.IGNORECASE) != None:
        return True
    elif re.match("^[0-9]{13}$", isbn, re.IGNORECASE) != None:
        return True
    return False



def process_edition(edition):
    """
    Turns a string with an edition in it into a processed string.
    Turns "1.0" into "1st", "2017.0" into "2017", and "International"
    into "International".  So it doesn't do a whole lot, but what it
    does do, it does well.

    Arguments:
        edition: The edition string.
    Returns:
        edition: The processed edition string.
    """

    try:
        edition = int(edition)
        if edition < 1000:
            # it's probably an edition, not a year

            # if the tens digit is 1, it's always "th"
            if (edition / 10) % 10 == 1:
                return str(edition) + "th"
            if edition%10 == 1:
                return str(edition) + "st"
            if edition%10 == 2:
                return str(edition) + "nd"
            if edition%10 == 3:
                return str(edition) + "rd"
            return str(edition) + "th"
        else:
            return str(edition)
    except ValueError:
        return edition


def get_name_from_user_id(user_id):
    """
    Queries the database and returns the full name (first and last) of the user with the specified user id (NOT UID).

    Arguments:
        user_id: The user id of the requested user (NOT UID).
    Returns:
        result: A string of the user's full name.
                (first + " " + last)
    """
    query = sqlalchemy.text("""SELECT full_name FROM members_full_name WHERE user_id=:user_id""")
    result = flask.g.db.execute(query, user_id=user_id).first()
    return result[0]


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


def get_category_name_from_id(cat_id):
    """
    Queries the database and returns the name of the category with the specified id.

    Arguments:
        cat_id: The id of the requested category.
    Returns:
        result: A string with the name of the category.
    """
    query = sqlalchemy.text("""SELECT cat_title FROM marketplace_categories WHERE cat_id=:cat_id""")
    result = flask.g.db.execute(query, cat_id=cat_id).first()
    return result[0]
