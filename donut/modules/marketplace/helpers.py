import flask
import re

from donut.modules.core.helpers import get_member_data, get_name_and_email
from donut.auth_utils import get_user_id, check_permission

# taken from donut-legacy, which was apparently taken from a CS11
# C++ assignment by dkong
SKIP_WORDS = set(
    ('a', 'all', 'am', 'an', 'and', 'are', 'as', 'at', 'be', 'been', 'but',
     'by', 'did', 'do', 'for', 'from', 'had', 'has', 'have', 'he', 'her',
     'hers', 'him', 'his', 'i', 'if', 'in', 'into', 'is', 'it', 'its', 'me',
     'my', 'not', 'of', 'on', 'or', 'so', 'that', 'the', 'their', 'them',
     'they', 'this', 'to', 'up', 'us', 'was', 'we', 'what', 'who', 'why',
     'will', 'with', 'you', 'your'))

PUNCTUATION = r'[,.\-_!;:/\\]'
EDITION = r'^(\d+|international)$'
ISBN_10 = r'^\d{9}[x\d]$'
ISBN_13 = r'^\d{13}$'
IMGUR_IMAGE = r'^https?://i\.imgur\.com/[a-z\d]+\.(jpg|png|gif)'
IMGUR_POST = r'^https?://imgur\.com/([a-z\d]+)$'
"""
Matches prices of the form ****.**, ****, and .**
examples:
first capture group:
123.98
123
second capture group:
0.98
.98
"""
PRICE = r'^([1-9]\d*(\.\d{2})?|0?\.\d{2})$'

ALL_CATEGORY = 'all'
SEARCH_FIELDS = ('item_id', 'cat_title', 'item_title', 'textbook_title',
                 'item_price', 'user_id', 'item_timestamp')
MANAGE_FIELDS = ('item_id', 'item_title', 'textbook_title', 'item_price',
                 'item_timestamp', 'cat_title', 'item_active')


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
    # Get category titles
    categories = table_fetch('marketplace_categories')
    categories.insert(0,
                      {'cat_id': ALL_CATEGORY,
                       'cat_title': 'All categories'})

    # Pass the category array, urls array, and width string, along with the
    # arguments passed in to this function, on to Flask in order to render the
    # top bar and the rest of the content.
    return flask.render_template(template_url, cats=categories, **kwargs)


def can_manage(item):
    """
    Returns whether the currently logged-in user can manage a given item.
    Item may be {'user_id': int} or an item_id.
    """

    username = flask.session.get('username')
    if not username:
        # Must be logged in to manage
        return False

    user_id = table_fetch(
        'marketplace_items',
        one=True,
        fields=('user_id', ),
        attrs={'item_id': item}) if type(item) == int else item['user_id']
    return get_user_id(username) == user_id or check_permission(username, None)


###############
# MANAGE PAGE #
###############


def set_active_status(item_id, is_active):
    """
    Sets the is_active status of item <item> to <is_active>.
    """
    query = 'UPDATE marketplace_items SET item_active = %s WHERE item_id = %s'
    with flask.g.pymysql_db.cursor() as cursor:
        cursor.execute(query, (is_active, item_id))


def get_my_items():
    """
    Generates the table of items managed by the current user.
    """

    return table_fetch(
        """
            marketplace_items NATURAL LEFT JOIN
            marketplace_textbooks NATURAL JOIN
            marketplace_categories
        """,
        fields=MANAGE_FIELDS,
        attrs={'user_id': get_user_id(flask.session['username'])})


###############
# SEARCH PAGE #
###############


def generate_search_table(attrs, query):
    """
    Arguments:
        attrs: A map of fields to values that make up conditions on the fields.
               For example, {'cat_id': 1} will only return results for which the
               category id is 1.

        query: The query string used to filter the results, or '' for no filtering.
    """

    fields = SEARCH_FIELDS

    if query:
        # Also add cat_id, textbook_author and textbook_isbn to the end so
        # that we can use those fields to query by
        fields += ('textbook_author', 'textbook_isbn')

    result = table_fetch(
        """
            marketplace_items NATURAL LEFT JOIN
            marketplace_textbooks NATURAL JOIN
            marketplace_categories
        """,
        fields=fields,
        attrs=attrs)

    if query:
        # Filter by query
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
        item['url'] = flask.url_for(
            'marketplace.view_item', item_id=item['item_id'])

    return result


def search_datalist(items, query):
    """
    Searches in items to create a new list of items,
    sorted first by relevance and then by date created.
    The query is split into words and ISBNs and each item is scored
    based on how many words are in its title and whether it matches an ISBN.
    """
    query_tokens = tokenize_query(query)
    perfect_matches = []
    imperfect_matches = []
    perfect_score = len(query_tokens)

    # ISBNs instantly make listings a perfect match
    query_isbns = [token for token in query_tokens if validate_isbn(token)]

    for item in items:
        if item['cat_title'] == 'Textbooks':
            # If it's a textbook, include the author's name and the
            # book title in the item tokens
            item_tokens = tokenize_query(item['textbook_title'])
            item_tokens.extend(tokenize_query(item['textbook_author']))

            # Does the isbn match any of the query's isbns?
            is_isbn_match = any(isbn == item['textbook_isbn']
                                for isbn in query_isbns)
        else:
            # Only include the item title
            item_tokens = tokenize_query(item['item_title'])
            is_isbn_match = False

        score = perfect_score if is_isbn_match else \
            get_matches(query_tokens, item_tokens)

        # Store the item's score and add it to the list of (im)perfect matches
        if score:
            item['score'] = score

            (perfect_matches if score == perfect_score else imperfect_matches) \
                .append(item)

    # If we have any perfect matches, don't include the imperfect ones.
    # The sort by highest-scoring and newest first.
    items = sorted(
        perfect_matches or imperfect_matches,
        key=lambda item: (item['score'], item['item_timestamp']),
        reverse=True)
    for item in items:
        del item['score']
    return items


def get_matches(l1, l2):
    """
    Returns the number of items in both list 1 and list 2.
    """
    if len(l1) > len(l2):
        l1, l2 = l2, l1

    l2 = set(l2)
    return sum(1 for x in l1 if x in l2)


def tokenize_query(query):
    """
    Turns a string with a query into a list of tokens that represent the query.
    """
    # Validate ISBNs before we remove hyphens
    tokens = []
    query_tokens = []
    for token in query.split():
        (tokens if validate_isbn(token) else query_tokens).append(token)

    # Remove punctuation
    query_tokens = re.sub(PUNCTUATION, ' ', ' '.join(query_tokens)).split()

    # If any of the words in query are in our SKIP_WORDS,
    # don't add them to tokens
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
    # Hyphens are annoying but there should never be one at start or end,
    # nor should there be two in a row
    if isbn[0] == '-' or isbn[-1] == '-' or '--' in isbn:
        return False

    # Now that we've done that we can remove them
    isbn = isbn.replace('-', '')

    if re.match(ISBN_10, isbn, re.IGNORECASE):
        # Check the check digit
        total = 0
        for i, char in enumerate(isbn):
            digit = 10 if char.lower() == 'x' else int(char)  # x has value 10
            weight = 10 - i
            total += digit * weight
        return total % 11 == 0

    if re.match(ISBN_13, isbn, re.IGNORECASE):
        # Check the check digit
        total = 0
        for i, char in enumerate(isbn):
            weight = 3 if i % 2 else 1
            digit = int(char)
            total += digit * weight
        return total % 10 == 0

    return False


def process_edition(edition):
    """
    Turns a string with an edition in it into a processed string.
    Turns '1' into '1st', '2017' into '2017', and 'International'
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
            # It's probably an edition, not a year

            # If the tens digit is 1, it's always 'th'
            if (edition // 10) % 10 == 1:
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
        one:    Whether to look for a single result (instead of all matching results).
        fields: The fields to return. If None, then all fields are returned.
        attrs:  The attributes of the members to filter for.
    Returns:
        result: The fields and corresponding values of members with desired
                attributes. A dict if one == True, a list of dicts if one == False.
    """
    s = 'SELECT ' + ', '.join(fields or ('*', ))
    s += ' FROM ' + tables
    if attrs:
        s += ' WHERE ' + ' AND '.join(key + ' = %s' for key in attrs)

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
    """Returns whether a string is a valid edition"""
    return re.match(EDITION, edition, re.IGNORECASE) is not None


def validate_price(price):
    """Returns whether a string is a valid price"""
    return re.match(PRICE, price) is not None


def validate_image(image):
    """Validates an Imgur image URL and normalizes it"""
    if re.match(IMGUR_IMAGE, image, re.IGNORECASE):
        return image

    # If URL is to a post rather than an image, convert it
    post_match = re.match(IMGUR_POST, image, re.IGNORECASE)
    if post_match:
        return f'https://i.imgur.com/{post_match.group(1)}.png'

    return None


def insert_images(item_id, item):
    """Add all of item's image links to marketplace_images"""
    query = 'INSERT INTO marketplace_images (item_id, img_link) VALUES (%s, %s)'
    with flask.g.pymysql_db.cursor() as cursor:
        for image in item['images']:
            cursor.execute(query, (item_id, image))


def create_new_listing(item):
    """
    Inserts an item into the database!
    Returns the inserted row's item_id
    """
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

    insert_images(item_id, item)
    return item_id


def update_current_listing(item_id, item):
    """
    Modifies the fields of an item in the database!

    Arguments:
        item_id: the id of the item to update
        item: a dict with the item's fields
    """
    query = """
        UPDATE marketplace_items
        SET cat_id = %s, item_title = %s, item_condition = %s,
            item_details = %s, item_price = %s, textbook_id = %s,
            textbook_edition = %s, textbook_isbn = %s
        WHERE item_id = %s
    """
    with flask.g.pymysql_db.cursor() as cursor:
        cursor.execute(query,
                       (item['cat_id'], item.get('item_title') or None,
                        item['item_condition'], item['item_details'] or None,
                        item['item_price'], item.get('textbook_id') or None,
                        item.get('textbook_edition') or None,
                        item.get('textbook_isbn') or None, item_id))

    # clean the database of all items that used to be affiliated with <item_id>
    query = 'DELETE FROM marketplace_images WHERE item_id = %s'
    with flask.g.pymysql_db.cursor() as cursor:
        cursor.execute(query, item_id)

    insert_images(item_id, item)


def add_textbook(title, author):
    """
    Adds a textbook to the database, with the given title and author.
    Returns the id of the new textbook.
    """
    # Check if the textbook already exists
    query = """
        SELECT textbook_id
        FROM marketplace_textbooks
        WHERE textbook_title = %s AND textbook_author = %s
    """
    with flask.g.pymysql_db.cursor() as cursor:
        cursor.execute(query, (title, author))
        result = cursor.fetchone()
        if result:
            # Reused the existing textbook
            return result['textbook_id']

    # Insert the textbook
    query = """
        INSERT INTO marketplace_textbooks (textbook_title, textbook_author)
        VALUES (%s, %s)
    """
    with flask.g.pymysql_db.cursor() as cursor:
        cursor.execute(query, (title, author))
        return cursor.lastrowid


#####################
# HELPFUL FUNCTIONS #
#####################
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
        fields=('cat_title', ),
        attrs={'cat_id': cat_id})


def get_image_links(item_id):
    """Returns the URLs of all the images for the item with the given item_id"""
    return table_fetch(
        'marketplace_images',
        fields=('img_link', ),
        attrs={'item_id': item_id})


def try_int(x):
    """Converts the input to an int, or returns None if conversion fails"""
    if x is None:
        return x

    try:
        return int(x)
    except ValueError:
        return None
