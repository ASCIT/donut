import flask
import json

from donut.modules.marketplace import blueprint, helpers
from donut.modules.core.helpers import get_name_and_email
from donut.auth_utils import get_user_id

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

ALLOWED_SELL_STATES = set(('new', 'edit'))
SELL_FIELDS = ('textbook_id', 'item_id', 'cat_id', 'user_id', 'item_title',
               'item_details', 'item_condition', 'item_price', 'item_active',
               'textbook_edition', 'textbook_isbn')
CONDITIONS = ('New', 'Very Good', 'Good', 'Acceptable', 'Poor')


@blueprint.route('/marketplace')
def marketplace():
    """Display marketplace page."""

    return helpers.render_with_top_marketplace_bar(
        'marketplace.html', cat_id=0)
    # cat_id = 0 indicates that the select object should be set to 'all
    # categories', which is the default


@blueprint.route('/marketplace/search')
def query():
    """Displays all results for the query in category category_id, which can be
       'all' if no category is selected."""

    category_id = flask.request.args.get('cat')
    if category_id is None:
        flask.abort(404)
    query = flask.request.args.get('q', '')

    # Create a dict of the passed in attributes which are filterable
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
        # only pass in the cat_id to get_marketplace_items_list_data if it's not
        # 'all', because cat_id (and everything in attrs) goes into a WHERE
        # clause, and not specifying is the same as selecting all.

    items = helpers.generate_search_table(attrs, query)

    return helpers.render_with_top_marketplace_bar(
        'search.html', items=items, cat_id=category_id)


@blueprint.route('/marketplace/view_item/<int:item_id>')
def view_item(item_id):
    """View additional details about item <item_id>"""

    item = helpers.table_fetch(
        """
            marketplace_items NATURAL LEFT JOIN
            marketplace_textbooks NATURAL JOIN
            marketplace_categories
        """,
        one=True,
        fields=VIEW_FIELDS,
        attrs={'item_id': item_id})

    # make sure the item_id is a valid item, i.e. data is nonempty
    if item is None:
        flask.abort(404)

    # Display textbook edition
    edition = item['textbook_edition']
    if edition:
        item['textbook_edition'] = helpers.process_edition(edition)

    # grab the stored image links
    image_links = helpers.get_image_links(item_id)

    # notify if the item is inactive
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
        # they're not logged in, kick them out
        flask.flash('Login required to access that page.')
        flask.session['next'] = flask.url_for('.manage')
        return helpers.render_with_top_marketplace_bar('requires_login.html')

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
        # they're not logged in, kick them out
        flask.flash('Login required to access that page.')
        flask.session['next'] = flask.url_for('.sell')
        return helpers.render_with_top_marketplace_bar('requires_login.html')

    # Extract item id
    item_id = helpers.try_int(flask.request.args.get('item_id'))

    # STATES
    # ------
    # blank: defaults to new
    # new:   making a new listing
    # edit:  editing an old listing

    state = flask.request.args.get('state', 'new')
    if state not in ALLOWED_SELL_STATES:
        flask.flash('Invalid state')
        return flask.redirect(flask.url_for('.sell'))

    saving = flask.request.method == 'POST'
    editing = state == 'edit'
    if saving:
        form = flask.request.form
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
            # no data? the item_id must be wrong
            flask.flash('Invalid item')
            return flask.redirect(flask.url_for('.marketplace'))

        item['images'] = helpers.get_image_links(item_id)
    else:
        item = {'images': []}

    # make sure the current user is the one who posted the item
    if editing and not helpers.can_manage(item_id):
        flask.flash('You do not have permission to edit this item')
        return flask.redirect(flask.url_for('.marketplace'))

    if saving:
        errors = []
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
            if not (edition is None or helpers.validate_edition(edition)):
                errors.append('Invalid textbook edition')
            isbn = item['textbook_isbn']
            if isbn is not None:
                if helpers.validate_isbn(isbn):
                    item['textbook_isbn'] = isbn.replace('-', '')
                else:
                    errors.append('Invalid textbook ISBN')
        elif not item['item_title']:
            errors.append('Missing item title')
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
