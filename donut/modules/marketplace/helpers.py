import flask
import re

from donut.modules.core.helpers import get_member_data, get_name_and_email
from donut.auth_utils import get_user_id, check_permission
from donut.resources import Permissions

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

PUNCTUATION = r'[,.\-_!;:/\\]'
EDITION = r'^(\d+|international)$'
# matches prices of the form ****.**, ****, and .**
# examples:
# first capture group:
# 123.98
# 123
# second capture group:
# 0.98
# .98
PRICE = r'^([1-9]\d*(\.\d{2})?|0?\.\d{2})$'
IMGUR_IMAGE = r'^https?://i\.imgur\.com/[a-z\d]+\.(jpg|png|gif)'
IMGUR_POST = r'^https?://imgur\.com/([a-z\d]+)$'

ALL_CATEGORY = 'all'


def get_categories():
    return table_fetch(
        'marketplace_categories', fields=['cat_id', 'cat_title'])


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
    categories = get_categories()

    # If there's nothing in categories, 404; something's borked.
    if not categories:
        flask.abort(404)

    categories.insert(0,
                      {'cat_id': ALL_CATEGORY,
                       'cat_title': 'All categories'})

    # Pass the category array, urls array, and width string, along with the
    # arguments passed in to this function, on to Flask in order to render the
    # top bar and the rest of the content.
    return flask.render_template(template_url, cats=categories, **kwargs)


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
SEARCH_FIELDS = [
    'item_id', 'cat_title', 'item_title', 'textbook_title', 'item_price',
    'user_id', 'item_timestamp'
]


def generate_search_table(attrs, query):
    """
    Arguments:
        attrs: A map of fields to values that make up conditions on the fields.
               For example, {'cat_id':1} will only return results for which the
               category id is 1.

        query: The query we want to filter our results by.  If '', no
               filtering happens.
    """

    fields = SEARCH_FIELDS

    if query:
        # Also add cat_id, textbook_author and textbook_isbn to the end so
        # that we can use those fields to query by.
        fields += ['textbook_author', 'textbook_isbn']

    result = table_fetch(
        """
            marketplace_items NATURAL LEFT JOIN
            marketplace_textbooks NATURAL JOIN
            marketplace_categories
        """,
        fields=fields,
        attrs=attrs)

    if query:
        # Filter by query.
        result = search_datalist(result, query)

    # Format the data, parsing the timestamps, converting the ids to actual
    # information, and adding links
    for item in result:
        if not item['item_title']:
            item['item_title'] = item['textbook_title']
        item['item_timestamp'] = item['item_timestamp'].strftime('%m/%d/%y')
        user_id = item['user_id']
        item['user_url'] = flask.url_for(
            'directory_search.view_user', user_id=user_id)
        item['user_name'] = get_name_and_email(user_id)['full_name']
        item['url'] = flask.url_for('.view_item', item_id=item['item_id'])

    return result


def search_datalist(datalist, query):
    """
    Searches in datalist to create a new datalist,
    sorted first by relevance and then by date created.
    """
    query_tokens = tokenize_query(query)
    perfect_matches = []
    imperfect_matches = []
    perfect_score = len(query_tokens)

    # ISBNs instantly make listings a perfect match
    query_isbns = [token for token in query_tokens if validate_isbn(token)]

    for listing in datalist:
        item_tokens = []
        if listing['cat_title'] == 'Textbooks':
            # if it's a textbook, include the author's name and the
            # book title in the item tokens
            item_tokens = tokenize_query(listing['textbook_title'])
            item_tokens += tokenize_query(listing['textbook_author'])

            # does the isbn match any of the query's isbns?
            is_isbn_match = any(isbn == listing['textbook_isbn']
                                for isbn in query_isbns)
        else:
            # only include the item title
            item_tokens = tokenize_query(listing['item_title'])
            is_isbn_match = False

        score = get_matches(query_tokens, item_tokens)

        if score > 0:
            listing['score'] = score

            if is_isbn_match or score == perfect_score:
                perfect_matches.append(listing)
            else:
                imperfect_matches.append(listing)

    # if we have any perfect matches, don't include the imperfect ones
    return sorted(
        perfect_matches or imperfect_matches,
        key=lambda item: (item['score'], item['item_timestamp']))


def get_matches(l1, l2):
    """
    Returns the number of matches between list 1 and list 2.
    """
    if len(l1) > len(l2):
        l1, l2 = l2, l1

    l2 = set(l2)
    return sum(1 for x in l1 if x in l2)


def tokenize_query(query):
    """
    Turns a string with a query into a list of tokens that represent the query.
    """
    # Validate ISBNs before we remove hyphens.
    tokens = []
    query_tokens = []
    for token in query.split():
        (tokens if validate_isbn(token) else query_tokens).append(token)

    # Remove punctuation.
    query_tokens = re.sub(PUNCTUATION, ' ', ' '.join(query_tokens)).split()

    # If any of the words in query are in our SKIP_WORDS, don't add them
    # to tokens.
    for token in query_tokens:
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
        return total % 10 == 0

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
def table_fetch(tables, one=False, fields=None, attrs={}):
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
    s = 'SELECT ' + ('*' if fields is None else ', '.join(fields))
    s += ' FROM ' + tables
    if attrs:
        s += ' WHERE ' + ' AND '.join([key + ' = %s' for key in attrs])

    # Execute the query
    with flask.g.pymysql_db.cursor() as cursor:
        cursor.execute(s, list(attrs.values()))
        result = cursor.fetchone() if one else cursor.fetchall()

    # If only one field requested, unwrap each row
    if fields and len(fields) == 1:
        field, = fields
        if one:
            result = result and result[field]  # avoid unwrapping None
        else:
            result = [row[field] for row in result]

    return result


#############
# SELL PAGE #
#############
def validate_edition(edition):
    return re.match(EDITION, edition, re.IGNORECASE) is not None


def validate_price(price):
    return re.match(PRICE, price) is not None


def validate_image(image):
    if re.match(IMGUR_IMAGE, image, re.IGNORECASE):
        return image
    post_match = re.match(IMGUR_POST, image, re.IGNORECASE)
    if post_match:
        return f'https://i.imgur.com/{post_match.group(1)}.png'
    return None


def create_new_listing(item):
    """
    Inserts into the database!

    Arguments:
        item: a dict with the item's fields
    Returns:
        the item_id, or -1 if it fails
    """
    item_id = -1
    query = """
        INSERT INTO marketplace_items (
            user_id, cat_id, item_title, item_condition, item_details,
            item_price, textbook_id, textbook_edition, textbook_isbn
        )
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
    """
    with flask.g.pymysql_db.cursor() as cursor:
        cursor.execute(query,
                       (item['user_id'], item['cat_id'], item.get('item_title')
                        or None, item['item_condition'], item['item_details']
                        or None, item['item_price'], item.get('textbook_id')
                        or None, item.get('textbook_edition') or None,
                        item.get('textbook_isbn') or None))
        item_id = cursor.lastrowid

    if item_id == -1:
        return -1

    query = 'INSERT INTO marketplace_images (item_id, img_link) VALUES (%s, %s)'
    with flask.g.pymysql_db.cursor() as cursor:
        for image in item['images']:
            cursor.execute(query, (item_id, image))
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
        The id of the new textbook
    """
    # check if the textbook exists
    query = """
        SELECT textbook_id
        FROM marketplace_textbooks
        WHERE textbook_title = %s AND textbook_author = %s
    """
    with flask.g.pymysql_db.cursor() as cursor:
        cursor.execute(query, (title, author))
        result = cursor.fetchone()
        if result:
            # the textbook already exists
            return result['textbook_id']

    query = """
        INSERT INTO marketplace_textbooks (textbook_title, textbook_author)
        VALUES (%s, %s)
    """
    with flask.g.pymysql_db.cursor() as cursor:
        cursor.execute(query, (title, author))
        return cursor.lastrowid


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
    return table_fetch(
        'marketplace_categories',
        one=True,
        fields=['cat_title'],
        attrs={'cat_id': cat_id})
