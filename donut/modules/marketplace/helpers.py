import flask
import re
from math import ceil

from donut.modules.core.helpers import get_member_data
from donut.auth_utils import get_user_id, check_permission
from donut.resources import Permissions

from . import routes

# taken from donut-legacy, which was apparently taken from a CS11
# C++ assignment by dkong
SKIP_WORDS = set([
    'a', 'all', 'am', 'an', 'and', 'are', 'as', 'at', 'be', 'been', 'but',
    'by', 'did', 'do', 'for', 'from', 'had', 'has', 'have', 'he', 'her',
    'hers', 'him', 'his', 'i', 'if', 'in', 'into', 'is', 'it', 'its', 'me',
    'my', 'not', 'of', 'on', 'or', 'so', 'that', 'the', 'their', 'them',
    'they', 'this', 'to', 'up', 'us', 'was', 'we', 'what', 'who', 'why',
    'will', 'with', 'you', 'your'
])


def render_with_top_marketplace_bar(template_url, **kwargs):
    """
    Provides an easy way for routing functions to pass the variables required
    for rendering the marketplace's top bar to render_template.  Basically
    chains some other arguments on to the render call, namely the list of
    marketplace categories, the list urls to categories, and the width of each
    url column.

    Arguments:
        template_url: The url which is being rendered.
        **kwargs: The variables which are used to render the rest of the page.

    Returns:
        The result of render_template(): Whatever magic Flask does to render the
                                         final page.
    """
    # Get category titles.
    categories = table_fetch_all('marketplace_categories', ['cat_title'])

    # If there's nothing in categories, 404; something's borked.
    if len(categories) == 0:
        return flask.render_template('404.html'), 404

    # Pass the category array, urls array, and width string, along with the
    # arguments passed in to this function, on to Flask in order to render the
    # top bar and the rest of the content.
    return flask.render_template(
        template_url, cats=categories, **kwargs)


###############
# MANAGE PAGE #
###############
def manage_set_active_status(item, is_active):
    """
    Checks permissions and then sets the is_active status of item <item> to
    <is_active>.
    """
    current_user_id = get_user_id(flask.session['username'])
    if current_user_id != get_user_id_of_item(item) and not check_permission(
            Permissions.ADMIN):
        return False

    s = 'UPDATE marketplace_items SET item_active=%s WHERE item_id=%s'
    with flask.g.pymysql_db.cursor() as cursor:
        cursor.execute(s, (is_active, item))

    return True


def manage_delete_item(item_id):
    """
    Checks permissions and then deletes the item.
    """
    current_user_id = get_user_id(flask.session['username'])
    if current_user_id != get_user_id_of_item(
            item_id) and not check_permission(Permissions.ADMIN):
        return False

    return delete_item(item_id)


def manage_display_confirmation(action, item_id):
    """
    Displays a confirmation message where the user can confirm that they want
    to archive, unarchive, or delete of one of their items.
    """
    headers = ['Category', 'Item', 'Price', 'Date']

    fields = [
        'cat_id', 'item_title', 'textbook_title', 'item_price',
        'item_timestamp'
    ]

    field_index_map = {k: v for v, k in enumerate(fields)}

    item_details = table_fetch_one(
        'marketplace_items NATURAL LEFT JOIN marketplace_textbooks',
        fields=fields,
        attrs={'item_id': item_id})

    if item_details == None:
        # The item doesn't exist, something went wrong.
        return flask.render_template('404.html'), 404

    # Pretty timestamps!
    item_details[field_index_map['item_timestamp']] = item_details[
        field_index_map['item_timestamp']].strftime('%m/%d/%y')

    # Convert category ids to category names.
    item_details[field_index_map['cat_id']] = get_category_name_from_id(
        item_details[field_index_map['cat_id']])

    # Overall title is either item_title or textbook_title.
    if item_details[field_index_map['item_title']] == '':
        item_details[field_index_map['item_title']] = item_details[
            field_index_map['textbook_title']]
    del item_details[field_index_map['textbook_title']]

    links = [''] * len(item_details)
    links[field_index_map['item_title']] = flask.url_for(
        '.view_item', item_id=item_id)

    return render_with_top_marketplace_bar(
        'manage/confirm.html',
        action=action,
        headers=headers,
        item=item_details,
        links=links,
        item_id=item_id)


def display_managed_items():
    """
    Handles the generation of the table of managed items.
    """
    headers = ['Category', 'Item', 'Price', 'Date', '', '', '']

    fields = [
        'cat_id', 'item_title', 'textbook_title', 'item_price',
        'item_timestamp', 'item_active', 'item_id'
    ]
    field_index_map = {k: v for v, k in enumerate(fields)}

    # Get all owned items.
    owned_items = table_fetch_all(
        'marketplace_items NATURAL LEFT JOIN marketplace_textbooks',
        fields=fields,
        attrs={'user_id': get_user_id(flask.session['username'])})

    active_items = []
    active_links = []
    inactive_items = []
    inactive_links = []
    for item in owned_items:
        item_active = item[field_index_map['item_active']]
        item_id = item[field_index_map['item_id']]
        (item, field_index_map) = row_text_from_managed_item(
            item, field_index_map)
        links = generate_links_for_managed_item(item, field_index_map,
                                                item_active, item_id)

        if item_active:
            active_items.append(item)
            active_links.append(links)
        else:
            inactive_items.append(item)
            inactive_links.append(links)

    return render_with_top_marketplace_bar(
        'manage/manage.html',
        headers=headers,
        activelist=active_items,
        activelinks=active_links,
        inactivelist=inactive_items,
        inactivelinks=inactive_links)


def row_text_from_managed_item(item, field_index_map):
    """
    For use in routes.manage().  Removes item_active and item_id from item[],
    replacing them with edit, (un)archive, and delete text instead.  Also
    modifies field_index_map to reflect this change.
    """
    # Convert datestrings into actual dates.
    item[field_index_map['item_timestamp']] = item[field_index_map[
        'item_timestamp']].strftime('%m/%d/%y')
    # Convert category ids to category names.
    item[field_index_map['cat_id']] = get_category_name_from_id(
        item[field_index_map['cat_id']])

    if item[field_index_map['item_title']] == '':
        item[field_index_map['item_title']] = item[field_index_map[
            'textbook_title']]

    item_active = item[field_index_map['item_active']]
    # Remove item_active, item_id, and textbook_title.
    del item[field_index_map['item_id']]
    del item[field_index_map['item_active']]
    del item[field_index_map['textbook_title']]
    # This order is important because if we delete item_active first,
    # field_index_map['item_id'] will be wrong, so delete in reverse
    # order.

    # In the real text of the manage page, we need edit, (un)archive, and delete
    # links.
    item.append('Edit')
    field_index_map['edit'] = len(item) - 1

    if item_active:
        item.append('Archive')
    else:
        item.append('Unarchive')
    field_index_map['archive'] = len(item) - 1

    item.append('Delete')
    field_index_map['delete'] = len(item) - 1

    return (item, field_index_map)


def generate_links_for_managed_item(item, field_index_map, item_active,
                                    item_id):
    """
    For use in routes.manage().  Creates links to edit, (un)archive, and delete
    pages.

    Arguments:
        item: The list of item details.

        field_index_map: A map from a field to the index where its info is
                         stored in item.

        item_active: Whether or not the item is active -- affects whether the
                     link is archive or unarchive.

        item_id: ID of the item.

    Returns:
        links: A list the same size as item[], with links to edit, (un)archive,
               and delete pages stored at field_index_map['edit'], ['archive'],
               and ['delete'] respectively, and '' everywhere else.
    """
    links = [''] * len(item)

    links[field_index_map['item_title']] = flask.url_for(
        '.view_item', item_id=item_id)

    links[field_index_map['edit']] = flask.url_for(
        '.sell', item_id=item_id, state='edit')

    if item_active:
        links[field_index_map['archive']] = flask.url_for(
            '.manage_confirm', item=item_id, state='archive')
    else:
        links[field_index_map['archive']] = flask.url_for(
            '.manage_confirm', item=item_id, state='unarchive')

    links[field_index_map['delete']] = flask.url_for(
        '.manage_confirm', item=item_id, state='delete')

    return links


###############
# SEARCH PAGE #
###############
def generate_search_table(fields=None, attrs={}, query=''):
    """
    Provides a centralized way to generate the 2d array of cells that is
    displayed in a table, along with all the stuff that needs to be packaged
    with it.  Calls a few functions further down to get the data, merge some
    columns, and rename the headers.

    Arguments:
        fields: A list of the fields that are requested to be in the table.  For
                example: ['cat_id', 'item_title', 'textbook_title',
                'item_price', ...]

        attrs: A map of fields to values that make up conditions on the fields.
               For example, {'cat_id':1} will only return results for which the
               category id is 1.

        query: The query we want to filter our results by.  If '', no
               filtering happens.

    Returns:
        result: The 2d array that was requested.

        headers: The English-ified headers for each column.

        links: A 2d array that, in each cell, gives the url of the link that
               clicking on the corresponding cell in result should yield.  If
               none, the cell will contain the number 0 instead.
    """

    # We need the item_id to generate the urls that clicking on the item title
    # should go to.
    # Also, we add it to the front so that we can get the id before we need to
    # use it (i.e., when we're adding it to links)
    fields = ['item_id'] + (fields or [])

    if query:
        # Also add cat_id, textbook_author and textbook_isbn to the end so
        # that we can use those fields to query by.
        fields = fields + ['textbook_author', 'textbook_isbn', 'cat_id']

    result = get_table_list_data(
        'marketplace_items NATURAL LEFT JOIN marketplace_textbooks', fields,
        attrs)

    if query:
        # Filter by query.
        result = search_datalist(fields, result, query)
        # Take textbook_author, textbook_isbn, and cat_id (the last 3
        # columns) back out.
        fields = fields[:-3]
        for i in range(len(result)):
            result[i] = result[i][:-3]

    # Maps fields to their index in each result.  Done after search_datalist
    # in order to avoid key conflicts.
    field_index_map = {k: v for v, k in enumerate(fields)}

    (result, fields, field_index_map) = merge_titles(result, fields,
                                                     field_index_map)

    sanitized_res = []
    links = []

    # Format the data, parsing the timestamps, converting the ids to actual
    # information, and adding links
    for item_listing in result:
        #temp_res_row = item_listing
        link_row = [''] * len(item_listing)

        if 'item_id' in field_index_map:
            item_id = int(item_listing[field_index_map['item_id']])

        if 'item_timestamp' in field_index_map:
            item_listing[field_index_map['item_timestamp']] = item_listing[
                field_index_map['item_timestamp']].strftime('%m/%d/%y')

        if 'user_id' in field_index_map:
            link_row[field_index_map['user_id']] = flask.url_for(
                'directory_search.view_user',
                user_id=int(item_listing[field_index_map['user_id']]))

            item_listing[field_index_map['user_id']] = get_name_from_user_id(
                int(item_listing[field_index_map['user_id']]))

        if 'textbook_edition' in field_index_map:
            item_listing[
                field_index_map['textbook_edition']] = process_edition(
                    item_listing[field_index_map['textbook_edition']])

        if 'cat_id' in field_index_map:
            item_listing[field_index_map[
                'cat_id']] = get_category_name_from_id(
                    int(item_listing[field_index_map['cat_id']]))

        if 'item_title' in field_index_map:
            link_row[field_index_map['item_title']] = flask.url_for(
                '.view_item', item_id=item_id)

        if 'textbook_title' in field_index_map:
            link_row[field_index_map['textbook_title']] = flask.url_for(
                '.view_item', item_id=item_id)

        # Strip off the item_id column we added earlier in the function.
        item_listing = item_listing[1:]
        link_row = link_row[1:]

        # Add our rows to the real 2d arrays that we'll return.
        sanitized_res.append(item_listing)
        links.append(link_row)

    # Strip off the item_id column we added at the beginning.
    fields = fields[1:]

    headers = process_category_headers(fields)

    return (sanitized_res, headers, links)


def merge_titles(datalist, fields, field_index_map):
    """
    Takes datalist and merges the two columns, item_title and textbook_title.

    Arguments:
        datalist: a 2d list of data, with columns determined by fields.
        fields: the column titles from the SQL tables.
        field_index_map: a map from fields to their index in datalist.

    Returns:
        datalist: the original table, but with the two columns merged.
        fields: the column titles similarly merged together into item_title.
    """
    item_index = field_index_map.get('item_title')
    textbook_index = field_index_map.get('textbook_title')

    if item_index is None or textbook_index is None:
        # Can't merge, since the two columns aren't there.
        return (datalist, fields, field_index_map)

    for row_index in range(len(datalist)):
        row = datalist[row_index]
        if row[item_index] == '':
            row[item_index] = row[textbook_index]
        del row[textbook_index]
        datalist[row_index] = row
    del fields[textbook_index]

    # Update field_index_map.
    field_index_map = {k: v for v, k in enumerate(fields)}

    return (datalist, fields, field_index_map)


def process_category_headers(fields):
    """
    Converts fields from sql headers to English.

    Arguments:
        fields: the list of fields that will be changed into the headers that
                are returned.

    Returns:
        headers: the list of headers that will become the headers of the tables.
    """
    headers = []
    for i in fields:
        if i == 'item_title':
            headers.append('Item')
        elif i == 'item_price':
            headers.append('Price')
        elif i == 'user_id':
            headers.append('Sold by')
        elif i == 'item_timestamp':
            headers.append('Date')
        elif i == 'textbook_title':
            headers.append('Title')
        elif i == 'textbook_author':
            headers.append('Author')
        elif i == 'textbook_edition':
            headers.append('Edition')
        elif i == 'cat_id':
            headers.append('Category')
    return headers


def search_datalist(fields, datalist, query):
    """
    Searches in datalist (which has columns denoted in fields) to
    create a new datalist, sorted first by relevance and then by date
    created.
    """
    # Map column names to indices.
    field_index_map = {k: v for v, k in enumerate(fields)}

    # Add a special column at the end: score.
    field_index_map['score'] = len(fields)

    query_tokens = tokenize_query(query)
    perfect_matches = []
    imperfect_matches = []

    query_isbns = []
    # ISBNs instantly make listings a perfect match
    for token in query_tokens:
        if validate_isbn(token):
            query_isbns.append(token)

    for listing in datalist:
        item_tokens = []
        is_isbn_match = False
        if get_category_name_from_id(
                listing[field_index_map['cat_id']]) == 'Textbooks':
            # if it's a textbook, include the author's name and the
            # book title in the item tokens
            item_tokens = tokenize_query(
                listing[field_index_map['textbook_title']])
            item_tokens += tokenize_query(
                listing[field_index_map['textbook_author']])

            # does the isbn match any of the query's isbns?
            for isbn in query_isbns:
                if listing[field_index_map['textbook_isbn']] == isbn:
                    is_isbn_match = True
                    break
        else:
            # only include the item title
            item_tokens = tokenize_query(
                listing[field_index_map['item_title']])

        score = get_matches(query_tokens, item_tokens)

        # if it's an isbn match, give it a perfect score as well
        # so that it doesn't get placed after all of the other perfect
        # matches
        if is_isbn_match:
            score = len(query_tokens)

        if score == 0:
            continue

        listing.append(score)

        if score == len(query_tokens):
            perfect_matches.append(listing)
        else:
            imperfect_matches.append(listing)

    search_results = []
    # if we have any perfect matches, don't include the imperfect ones
    search_results = perfect_matches or imperfect_matches

    search_results = sorted(
        search_results,
        key=
        lambda item: (item[field_index_map['score']], item[field_index_map['item_timestamp']])
    )

    # chop off the last column, which holds the score
    for i in range(len(search_results)):
        search_results[i].pop()

    return search_results


def get_matches(l1, l2):
    """
    Returns the number of matches between list 1 and list 2.
    """
    l1 = set(l1)
    l2 = set(l2)
    if len(l1) < len(l2):
        return len([x for x in l1 if x in l2])
    else:
        return len([x for x in l2 if x in l1])


def tokenize_query(query):
    """
    Turns a string with a query into a list of tokens that represent the query.
    """
    query = query.split()
    # Validate ISBNs before we remove hyphens.
    tokens = list(filter(validate_isbn, query))
    query = filter(lambda token: not validate_isbn(token), query)

    # Remove punctuation.
    query = ' '.join(query)
    punctuation_regex = r'[,.\-_!;:/\\]'
    query = re.sub(punctuation_regex, ' ', query).split()

    # If any of the words in query are in our SKIP_WORDS, don't add them
    # to tokens.
    for token in query:
        token = token.lower()
        if token not in SKIP_WORDS:
            tokens.append(token)

    return tokens


def validate_isbn(isbn):
    """
    Determines whether an ISBN is valid or not.  Works with ISBN-10 and ISBN-13,
    validating the length of the string and the check digit as well.

    Arguments:
        isbn: The ISBN, in the form of a string.
    Returns:
        valid: Whether or not the isbn is valid (a boolean).
    """
    if type(isbn) != str:
        return False

    # Hyphens are annoying but there should never be one at start or end,
    # nor should there be two in a row.
    if isbn[0] == '-' or isbn[-1] == '-' or '--' in isbn:
        return False

    # Now that we've done that we can remove them.
    isbn = isbn.replace('-', '')

    # Regexes shamelessly copypasted.
    # The ISBN-10 can have an x at the end (but the ISBN-13 can't).
    if re.match('^[0-9]{9}[0-9x]$', isbn, re.IGNORECASE) != None:
        # Check the check digit.
        total = 0
        for i in range(10):
            char = isbn[i].lower()
            digit = 10  # x has value 10.
            if char != 'x':
                digit = int(char)
            weight = 10 - i
            total += digit * weight
        return total % 11 == 0

    if re.match('^[0-9]{13}$', isbn, re.IGNORECASE) != None:
        # Check the check digit.
        total = 0
        for i in range(13):
            weight = 1
            if i % 2 != 0:
                weight = 3
            digit = int(isbn[i])
            total += digit * weight
        if total % 10 == 0:
            return True
        else:
            return False

    return False


def process_edition(edition):
    """
    Turns a string with an edition in it into a processed string.
    Turns '1.0' into '1st', '2017.0' into '2017', and 'International'
    into 'International'.  So it doesn't do a whole lot, but what it
    does do, it does well.

    Arguments:
        edition: The edition string.
    Returns:
        edition: The processed edition string.
    """

    try:
        edition = int(edition)
        if edition < 100:
            # It's probably an edition, not a year.

            # If the tens digit is 1, it's always 'th'.
            if (edition / 10) % 10 == 1:
                return str(edition) + 'th'
            if edition % 10 == 1:
                return str(edition) + 'st'
            if edition % 10 == 2:
                return str(edition) + 'nd'
            if edition % 10 == 3:
                return str(edition) + 'rd'
            return str(edition) + 'th'
        else:
            return str(edition)
    except ValueError:
        return edition


#################
# TABLE QUERIES #
#################
def get_table_list_data(tables, fields=None, attrs={}):
    """
    Queries the database (specifically, table <table>) and returns list of
    member data constrained by the specified attributes.

    Arguments:
        tables: The table(s) to query.  Ex: 'marketplace_items', or
                'marketplace_items NATURAL LEFT JOIN
                marketplace_textbooks'.
        fields: The fields to return. If None specified, then default_fields
                are used.
        attrs:  The attributes of the members to filter for.
    Returns:
        result: The fields and corresponding values of members with desired
                attributes. In the form of a list of lists.
    """
    if fields == None:
        s_select_columns = 'SELECT * '
    else:
        s_select_columns = 'SELECT ' + ', '.join(fields) + ' '

    s_from = 'FROM ' + tables

    s_where = ''
    if attrs:
        s_where = ' WHERE '
        s_where += ' AND '.join([key + ' = %s' for key in attrs])

    s = s_select_columns + s_from + s_where

    # Execute the query.
    with flask.g.pymysql_db.cursor() as cursor:
        cursor.execute(s, list(attrs.values()))
        result = cursor.fetchall()

    # Return the list of lists.
    result = list(map(lambda a: list(a.values()), result))
    return result


def table_fetch_one(tables, fields=None, attrs={}):
    """
    Queries the database (specifically, table <table>) and returns list of member data
    constrained by the specified attributes.

    Arguments:
        tables: The table(s) to query.  Ex: 'marketplace_items', or
                'marketplace_items NATURAL LEFT JOIN
                marketplace_textbooks'.
        fields: The fields to return. If None specified, then default_fields
                are used.
        attrs:  The attributes of the members to filter for.
    Returns:
        result: The fields and corresponding values of members with desired
                attributes. In the form of a list.
    """
    if fields == None:
        s_select_columns = 'SELECT * '
    else:
        s_select_columns = 'SELECT ' + ', '.join(fields) + ' '

    s_from = 'FROM ' + tables

    s_where = ''
    if attrs:
        s_where = ' WHERE '
        s_where += ' AND '.join([key + ' = %s' for key in attrs.keys()])

    s = s_select_columns + s_from + s_where

    # Execute the query
    with flask.g.pymysql_db.cursor() as cursor:
        cursor.execute(s, list(attrs.values()))
        result = cursor.fetchone()

    # Return the values as a list
    result = list(result.values())

    # If only one field requested, unwrap [_] to _
    if len(fields) == 1:
        result = result[0]

    return result


def table_fetch_all(tables, fields=None, attrs={}):
    """
    Queries the database (specifically, table <table>) and returns list of member data
    constrained by the specified attributes.

    Arguments:
        tables: The table(s) to query.  Ex: 'marketplace_items', or
                'marketplace_items NATURAL LEFT JOIN
                marketplace_textbooks'.
        fields: The fields to return. If None specified, then default_fields
                are used.
        attrs:  The attributes of the members to filter for.
    Returns:
        result: The fields and corresponding values of members with desired
                attributes. In the form of a list of lists.
    """
    if fields == None:
        s_select_columns = 'SELECT * '
    else:
        s_select_columns = 'SELECT ' + ', '.join(fields) + ' '

    s_from = 'FROM ' + tables

    s_where = ''
    if attrs:
        s_where = ' WHERE '
        s_where += ' AND '.join([key + ' = %s' for key in attrs.keys()])

    s = s_select_columns + s_from + s_where

    # Execute the query
    with flask.g.pymysql_db.cursor() as cursor:
        cursor.execute(s, list(attrs.values()))
        result = cursor.fetchall()

    # Return the list of lists
    result = list(map(lambda a: list(a.values()), result))

    # If only one field requested, unwrap [[_], [_], [_]] to [_, _, _]
    if len(fields) == 1:
        result = list(map(lambda a: a[0], result))

    return result


#############
# SELL PAGE #
#############
def generate_hidden_form_elements(skip_fields):
    """
    Creates a list of names of parameters and values, gathered from flask.request.form, to be passed into sell_*.html.
    There, they will be turned into hidden form elements and passed into the request form.
    Some fields are skipped because including them would overwrite other fields.

    Arguments:
        skip_fields: The fields to skip.
    Returns:
        to_return: The list of parameters and values, in a 2d list where each row is of the form ['parameter', value]
    """
    parameters = [
        'cat_id', 'item_title', 'item_condition', 'item_details', 'item_price',
        'textbook_id', 'textbook_edition', 'textbook_isbn', 'state'
    ]

    to_return = []
    for parameter in parameters:
        if parameter in skip_fields:
            continue
        if parameter in flask.request.form:
            to_return.append([parameter, flask.request.form[parameter]])

    if 'item_images' not in skip_fields:
        if 'item_images[]' in flask.request.form:
            for image in flask.request.form.getlist('item_images[]'):
                to_return.append(['item_images[]', image])

    return to_return


def validate_data():
    """
    Validates the data submitted in the sell form.

    Returns:
        A list of all the validation errors; an empty list if no errors.
    """
    errors = []
    try:
        category_id = int(flask.request.form['cat_id'])
    except ValueError:
        # this should never happen through normal form use
        errors.append('Somehow the category got all messed up.')

    cat_title = get_table_list_data(
        'marketplace_categories',
        fields=['cat_title'],
        attrs={'cat_id': category_id})
    if len(cat_title) == 0:
        # the category id doesn't correspond to any category
        errors.append('Somehow the category got all messed up.')
    else:
        # 2d array to a single element
        # [['Furniture']] -> 'Furniture'
        cat_title = cat_title[0][0]

    if cat_title == 'Textbooks':
        # regex to make sure the textbook edition is valid
        if 'textbook_edition' in flask.request.form:
            edition_regex = '^(|[0-9]+|international)$'
            if re.match(edition_regex,
                        str(flask.request.form['textbook_edition']),
                        re.IGNORECASE) == None:
                errors.append(
                    'Textbook edition is invalid. Try providing a number or \'International\'.'
                )

        # validate the isbn too, if it's present
        if 'textbook_isbn' in flask.request.form and flask.request.form['textbook_isbn'] != '':
            if not validate_isbn(flask.request.form['textbook_isbn']):
                errors.append(
                    'Textbook ISBN appears to be invalid. Please check that you typed it in correctly.'
                )

    else:
        # just need to make sure the item_title exists
        if not 'item_title' in flask.request.form or flask.request.form['item_title'] == '':
            errors.append('Item title cannot be empty.')

    # condition is mandatory
    if not 'item_condition' in flask.request.form or flask.request.form['item_condition'] == '':
        errors.append('Item condition must be set.')

    # price must be present and valid
    if not 'item_price' in flask.request.form or flask.request.form['item_price'] == '':
        errors.append('Price cannot be left blank.')
    else:
        price_regex = '^([0-9]{1,4}\.[0-9]{0,2}|[0-9]{1,4}|\.[0-9]{1,2})$'
        # matches prices of the form ****.**, ****, and .**
        # examples:
        # first capture group:
        # 123.98
        # 1234.9
        # 12.
        # second capture group:
        # 12
        # 123
        # third capture group:
        # .9
        # .98
        if re.match(price_regex, flask.request.form['item_price']) == None:
            errors.append(
                'Price must be between 0 (inclusive) and 10,000 (exclusive) with at most 2 decimal places.'
            )

    image_regex_1 = "^https?://i\.imgur\.com/[a-z0-9]+\.(jpg|png|gif)$"
    image_regex_2 = "^https?://imgur\.com/[a-z0-9]+$"
    for image in flask.request.form.get('item_images', []):
        if image == "":
            continue

        if re.match(image_regex_1, image, re.IGNORECASE) == None:
            if re.match(image_regex_2, image, re.IGNORECASE) != None:
                # if it's in format 2, convert it to format 1 by taking
                # the key and adding .png.  Imgur automatically
                # converts any image uploaded to all three types (jpg, png, gif).
                key = image.split('/')[-1]
                image = "https://i.imgur.com/" + key + ".png"
            else:
                errors.append(
                    'Some image links appear to be invalid - try re-uploading?'
                )

    return errors


def create_new_listing(stored):
    """
    Inserts into the database!

    Arguments:
        stored: a map with the info
    Returns:
        the item_id, or -1 if it fails
    """
    user_id = int(stored['user_id'])
    cat_id = int(stored['cat_id'])
    cat_title = stored['cat_title']
    item_condition = stored['item_condition']
    item_details = stored['item_details']
    item_price = stored['item_price']
    item_images = []
    item_images = stored['item_images']
    result = []
    item_id = -1
    if cat_title == 'Textbooks':
        textbook_id = int(stored['textbook_id'])
        textbook_edition = stored['textbook_edition']
        textbook_isbn = stored['textbook_isbn'].replace('-', '')
        s = '''INSERT INTO marketplace_items
                (user_id, cat_id, item_condition, item_details, item_price, textbook_id, textbook_edition, textbook_isbn)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s)'''
        with flask.g.pymysql_db.cursor() as cursor:
            cursor.execute(s, [
                user_id, cat_id, item_condition, item_details, item_price,
                textbook_id, textbook_edition, textbook_isbn
            ])
            item_id = cursor.lastrowid
    else:
        item_title = stored['item_title']
        s = '''INSERT INTO marketplace_items (user_id, cat_id, item_title, item_condition, item_details, item_price) VALUES (%s, %s, %s, %s, %s, %s)'''
        with flask.g.pymysql_db.cursor() as cursor:
            cursor.execute(s, [
                user_id, cat_id, item_title, item_condition, item_details,
                item_price
            ])
            item_id = cursor.lastrowid

    if item_id == -1:
        return -1

    s = 'INSERT INTO marketplace_images (item_id, img_link) VALUES (%s, %s);'
    for image in item_images:
        if image == "":
            continue
        with flask.g.pymysql_db.cursor() as cursor:
            cursor.execute(s, [item_id, image])
    return item_id


def update_current_listing(item_id, stored):
    """
    Changes items in the database!

    Arguments:
        stored: a map with the info
    Returns:
        the item_id, or -1 if it fails
    """
    user_id = int(stored['user_id'])
    cat_id = int(stored['cat_id'])
    cat_title = stored['cat_title']
    item_condition = stored['item_condition']
    item_details = stored['item_details']
    item_price = stored['item_price']
    item_images = []
    item_images = stored['item_images']
    result = []
    if cat_title == 'Textbooks':
        textbook_id = int(stored['textbook_id'])
        textbook_edition = stored['textbook_edition']
        textbook_isbn = stored['textbook_isbn'].replace('-', '')
        s = '''UPDATE marketplace_items SET
                user_id=%s, cat_id=%s, item_condition=%s, item_details=%s, item_price=%s,
                textbook_id=%s, textbook_edition=%s, textbook_isbn=%s WHERE item_id=%s'''
        with flask.g.pymysql_db.cursor() as cursor:
            cursor.execute(s, [
                user_id, cat_id, item_condition, item_details, item_price,
                textbook_id, textbook_edition, textbook_isbn, item_id
            ])
    else:
        item_title = stored['item_title']
        s = '''UPDATE marketplace_items SET
                user_id=%s, cat_id=%s, item_title=%s, item_condition=%s, item_details=%s,
                item_price=%s WHERE item_id=%s'''
        with flask.g.pymysql_db.cursor() as cursor:
            cursor.execute(s, [
                user_id, cat_id, item_title, item_condition, item_details,
                item_price, item_id
            ])

    # clean the database of all items that used to be affiliated with <item_id>
    s = 'DELETE FROM marketplace_images WHERE item_id = %s'
    with flask.g.pymysql_db.cursor() as cursor:
        cursor.execute(s, [item_id])

    s = 'INSERT INTO marketplace_images (item_id, img_link) VALUES (%s, %s);'
    for image in item_images:
        if image == "":
            continue
        with flask.g.pymysql_db.cursor() as cursor:
            cursor.execute(s, [item_id, image])
    return item_id


def add_textbook(title, author):
    """
    Adds a textbook to the database, with title <title> and author
    <author>.

    Arguments:
        title: The title.
        author: The author.

    Returns:
        True if the insert succeeds, and False if not (the textbook
        already exists)
    """
    # check if the textbook exists
    s = '''SELECT textbook_title FROM
            marketplace_textbooks WHERE textbook_title = %s AND
            textbook_author = %s'''
    with flask.g.pymysql_db.cursor() as cursor:
        cursor.execute(s, [title, author])
        result = cursor.fetchone()
    if result:
        # the textbook already exists
        return False

    s = '''INSERT INTO marketplace_textbooks
            (textbook_title, textbook_author) VALUES (%s,
            %s)'''
    with flask.g.pymysql_db.cursor() as cursor:
        cursor.execute(s, [title, author])

    return True


def delete_item(item_id):
    """
    Deletes an item.

    Arguments:
        item_id: The id of the item to delete.

    Returns:
        True if the delete succeeds, and False if not (the item doesn't exist)
    """
    s = 'SELECT item_id FROM marketplace_items WHERE item_id = %s'
    with flask.g.pymysql_db.cursor() as cursor:
        cursor.execute(s, [item_id])
        result = cursor.fetchone()
    if result == None:
        # the item doesn't exist
        return False

    s = 'DELETE FROM marketplace_items WHERE item_id=%s'
    with flask.g.pymysql_db.cursor() as cursor:
        cursor.execute(s, [item_id])
    return True


#####################
# HELPFUL FUNCTIONS #
#####################
def get_user_id_of_item(item_id):
    """
    Gets the user_id of the user who owns the item <item_id>.

    Arguments:
        item_id: The id of the item.

    Returns:
        The user_id
    """
    s = 'SELECT user_id FROM marketplace_items WHERE item_id = %s'
    with flask.g.pymysql_db.cursor() as cursor:
        cursor.execute(s, [item_id])
        result = cursor.fetchone()
    if result == None:
        # the item doesn't exist
        return False
    return result['user_id']


def get_name_from_user_id(user_id):
    """
    Queries the database and returns the full name (first and last) of the user with the specified user id (NOT UID).

    Arguments:
        user_id: The user id of the requested user (NOT UID).
    Returns:
        result: A string of the user's full name.
                (first + ' ' + last)
    """
    s = 'SELECT full_name FROM members_full_name WHERE user_id=%s'
    with flask.g.pymysql_db.cursor() as cursor:
        cursor.execute(s, [user_id])
        result = cursor.fetchone()
    if result == None:
        return None
    return result['full_name']


def get_textbook_info_from_textbook_id(textbook_id):
    """
    Queries the database and returns the title and author of the textbook with the specified id.

    Arguments:
        textbok_id: The id of the requested textbook.
    Returns:
        result: A list of the textbook title and author.
    """
    s = 'SELECT textbook_title, textbook_author FROM marketplace_textbooks WHERE textbook_id=%s'

    with flask.g.pymysql_db.cursor() as cursor:
        cursor.execute(s, [textbook_id])
        result = cursor.fetchone()

    if result == None:
        return None
    return [result['textbook_title'], result['textbook_author']]


def get_category_name_from_id(cat_id):
    """
    Queries the database and returns the name of the category with the specified id.

    Arguments:
        cat_id: The id of the requested category.
    Returns:
        result: A string with the name of the category.
    """
    s = 'SELECT cat_title FROM marketplace_categories WHERE cat_id=%s'

    with flask.g.pymysql_db.cursor() as cursor:
        cursor.execute(s, [cat_id])
        result = cursor.fetchone()
    if result == None:
        return None
    return result['cat_title']
