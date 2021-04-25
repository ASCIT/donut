import flask
import json

from donut.modules.marketplace import blueprint, helpers
from donut.modules.core.helpers import get_name_and_email
from donut.auth_utils import get_user_id, is_caltech_user, login_redirect
from donut.validation_utils import (validate_exists, validate_length)

MAX_IMAGES = 5

SEARCH_ATTRS = set(
    ('item_id', 'cat_id', 'user_id', 'item_title', 'item_details',
     'item_images', 'item_condition', 'item_price', 'item_timestamp',
     'item_active', 'textbook_id', 'textbook_isbn', 'textbook_edition',
     'textbook_title'))

VIEW_FIELDS = ('textbook_id', 'cat_title', 'user_id', 'item_title',
               'item_details', 'item_condition', 'item_price',
               'item_timestamp', 'item_active', 'textbook_edition',
               'textbook_isbn', 'textbook_title', 'textbook_author')

ALLOWED_SELL_STATES = ('new', 'edit')
SELL_FIELDS = ('textbook_id', 'item_id', 'cat_id', 'user_id', 'item_title',
               'item_details', 'item_condition', 'item_price', 'item_active',
               'textbook_edition', 'textbook_isbn')
CONDITIONS = ('New', 'Very Good', 'Good', 'Acceptable', 'Poor')


@blueprint.route('/marketplace')
def marketplace():
    """Display marketplace page."""

    return helpers.render_with_top_marketplace_bar(
        'marketplace.html', cat_id=0)
    # cat_id = 0 makes the category selection default to 'all categories'


@blueprint.route('/marketplace/search')
def query():
    """Displays all results for the query in category category_id, which can be
       'all' if no category is selected."""

    if not is_caltech_user():
        return login_redirect()

    category_id = flask.request.args.get('cat')
    if category_id is None:
        flask.abort(404)
    query = flask.request.args.get('q', '')

    # Create a dict of the passed-in attributes which are filterable
    attrs = {
        attr: value
        for attr, value in flask.request.args.items() if attr in SEARCH_ATTRS
    }
    attrs['item_active'] = True
    if category_id != helpers.ALL_CATEGORY:
        try:
            attrs['cat_id'] = int(category_id)
        except ValueError:
            flask.abort(404)
        # Pass in the cat_id to generate_search_table() if it's not 'all'

    items = helpers.generate_search_table(attrs, query)
    return helpers.render_with_top_marketplace_bar(
        'search.html', items=items, cat_id=category_id)


@blueprint.route('/marketplace/view_item/<int:item_id>')
def view_item(item_id):
    """View additional details about item <item_id>"""

    if not is_caltech_user():
        return login_redirect()

    item = helpers.table_fetch(
        """
            marketplace_items NATURAL LEFT JOIN
            marketplace_textbooks NATURAL JOIN
            marketplace_categories
        """,
        one=True,
        fields=VIEW_FIELDS,
        attrs={'item_id': item_id})

    # Make sure the item_id is a valid item, i.e. data is nonempty
    if item is None:
        flask.abort(404)

    # Display textbook edition
    edition = item['textbook_edition']
    if edition:
        item['textbook_edition'] = helpers.process_edition(edition)

    # Grab the stored image links
    image_links = helpers.get_image_links(item_id)

    # Notify if the item is inactive
    if not item['item_active']:
        flask.flash('This item has been archived!')

    return helpers.render_with_top_marketplace_bar(
        'view_item.html',
        item_id=item_id,
        item=item,
        image_links=image_links,
        user=get_name_and_email(item['user_id']),
        can_edit=helpers.can_manage(item))


@blueprint.route('/marketplace/manage')
def manage():
    if 'username' not in flask.session:
        # They're not logged in, kick them out
        return login_redirect()

    return helpers.render_with_top_marketplace_bar(
        'manage_items.html', items=helpers.get_my_items())


@blueprint.route('/marketplace/archive/<int:item_id>')
def archive(item_id):
    if not helpers.can_manage(item_id):
        flask.flash('You do not have permission to archive this item.')
        return flask.redirect(flask.url_for('.marketplace'))

    helpers.set_active_status(item_id, False)
    return flask.redirect(flask.url_for('.manage'))


@blueprint.route('/marketplace/unarchive/<int:item_id>')
def unarchive(item_id):
    if not helpers.can_manage(item_id):
        flask.flash('You do not have permission to unarchive this item.')
        return flask.redirect(flask.url_for('.marketplace'))

    helpers.set_active_status(item_id, True)
    return flask.redirect(flask.url_for('.manage'))


@blueprint.route('/marketplace/sell', methods=['GET', 'POST'])
def sell():
    username = flask.session.get('username')
    if username is None:
        # They're not logged in, kick them out
        return login_redirect()

    # Extract item id
    item_id = helpers.try_int(flask.request.args.get('item_id'))

    # STATES
    # ------
    # new (default): making a new listing
    # edit: editing an old listing

    state = flask.request.args.get('state', 'new')
    if state not in ALLOWED_SELL_STATES:
        flask.flash('Invalid state')
        return flask.redirect(flask.url_for('.sell'))

    saving = flask.request.method == 'POST'
    editing = state == 'edit'
    if saving:
        form = flask.request.form
        validations = [
            validate_exists(form, 'textbook_title') and
            validate_length(form['textbook_title'], 0, 191),
            validate_exists(form, 'textbook_author') and
            validate_length(form['textbook_author'], 0, 191),
            validate_exists(form, 'item_title') and
            validate_length(form['item_title'], 0, 255),
            validate_exists(form, 'item_condition') and
            validate_length(form['item_condition'], 0, 20),
        ]
        if not all(validations):
            flask.flash('Invalid form data')
            return flask.redirect(flask.url_for('.sell'))
        item = {
            'cat_id': helpers.try_int(form.get('cat')),
            'textbook_id': helpers.try_int(form.get('textbook_id')),
            'textbook_title': form.get('textbook_title'),
            'textbook_author': form.get('textbook_author'),
            'textbook_edition': form.get('textbook_edition'),
            'textbook_isbn': form.get('textbook_isbn'),
            'item_title': form.get('item_title'),
            'item_condition': form.get('item_condition'),
            'item_price': form.get('item_price'),
            'item_details': form.get('item_details'),
            'images': [image for image in form.getlist('images') if image]
        }
    elif editing:
        item = helpers.table_fetch(
            'marketplace_items',
            one=True,
            fields=SELL_FIELDS,
            attrs={'item_id': item_id})
        if not item:
            # No data? the item_id must be wrong
            flask.flash('Invalid item')
            return flask.redirect(flask.url_for('.marketplace'))

        item['images'] = helpers.get_image_links(item_id)
    else:
        item = {'images': []}

    # Make sure the current user is the one who posted the item
    if editing and not helpers.can_manage(item_id):
        flask.flash('You do not have permission to edit this item')
        return flask.redirect(flask.url_for('.marketplace'))

    # This route is used for both GET and POST;
    # only try to create/update the item if this is a POST
    if saving:
        errors = []  # collect all validation errors
        cat_title = helpers.get_category_name_from_id(item['cat_id'])
        if not cat_title:
            errors.append('Invalid category')
        is_textbook = cat_title == 'Textbooks'
        if is_textbook:
            textbook_id = item['textbook_id']
            if textbook_id:
                textbook = helpers.table_fetch(
                    'marketplace_textbooks',
                    one=True,
                    attrs={'textbook_id': textbook_id})
                if not textbook:
                    errors.append('Invalid textbook')
            else:
                if not item['textbook_title']:
                    errors.append('Missing textbook title')
                if not item['textbook_author']:
                    errors.append('Missing textbook author')
            edition = item['textbook_edition']
            if edition and not helpers.validate_edition(edition):
                errors.append('Invalid textbook edition')
            isbn = item['textbook_isbn']
            if isbn:
                if helpers.validate_isbn(isbn):
                    item['textbook_isbn'] = isbn.replace('-', '')
                else:
                    errors.append('Invalid textbook ISBN')
            item['item_title'] = None
        else:
            if not item['item_title']:
                errors.append('Missing item title')
            item['textbook_id'] = None
            item['textbook_edition'] = None
            item['textbook_isbn'] = None
        if not item['item_condition']:
            errors.append('Missing condition')
        price = item['item_price']
        if not (price and helpers.validate_price(price)):
            errors.append('Invalid price')
        images = item['images']
        for i, image in enumerate(images):
            image = helpers.validate_image(image)
            if image:
                images[i] = image
            else:
                errors.append('Invalid image')

        if errors:
            # Display all errors and don't submit
            for error in errors:
                flask.flash(error)
        else:
            if is_textbook and not textbook_id:
                item['textbook_id'] = helpers.add_textbook(
                    item['textbook_title'], item['textbook_author'])
            if editing:
                helpers.update_current_listing(item_id, item)
                flask.flash('Updated!')
            else:
                item['user_id'] = get_user_id(username)
                item_id = helpers.create_new_listing(item)
                flask.flash('Posted!')
            return flask.redirect(flask.url_for('.view_item', item_id=item_id))

    # Otherwise, they have not submitted anything, so render the form
    item['images'] += [''] * (MAX_IMAGES - len(item['images']))

    categories = helpers.table_fetch('marketplace_categories')
    textbooks_cat, = (cat['cat_id'] for cat in categories
                      if cat['cat_title'] == 'Textbooks')
    textbooks = helpers.table_fetch('marketplace_textbooks')
    return helpers.render_with_top_marketplace_bar(
        'sell.html',
        state=state,
        item_id=item_id,
        item=item,
        MAX_IMAGES=MAX_IMAGES,
        imgur_id=flask.current_app.config['IMGUR_API']['id'],
        categories=categories,
        textbooks=textbooks,
        textbooks_cat=textbooks_cat,
        conditions=CONDITIONS)
