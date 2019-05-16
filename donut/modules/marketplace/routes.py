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

    # grab the stored image links
    image_links = helpers.table_fetch(
        'marketplace_images', fields=['img_link'], attrs={'item_id': item_id})

    # TODO: use permissions
    can_edit = 'username' in flask.session and \
        get_user_id(flask.session['username']) == item['user_id']

    # notify if the item is inactive
    if not item['item_active']:
        flask.flash('The listing for this item is no longer active!')

    return helpers.render_with_top_marketplace_bar(
        'view_item.html',
        item_id=item_id,
        item=item,
        image_links=image_links,
        user=get_name_and_email(item['user_id']),
        can_edit=can_edit)


@blueprint.route('/marketplace/manage', methods=['GET', 'POST'])
def manage():
    if 'username' not in flask.session:
        # they're not logged in, kick them out
        flask.flash('Login required to access that page.')
        flask.session['next'] = flask.url_for('.manage')
        return helpers.render_with_top_marketplace_bar('requires_login.html')

    if flask.request.method == 'POST':
        if 'item' not in flask.request.form:
            flask.flash('Invalid request')
        else:
            item = flask.request.form['item']
            # archive, unarchive, delete
            if flask.request.form['state'] == 'archive':
                result = helpers.manage_set_active_status(item, 0)
                if result == False:
                    flask.flash('You do not own that item.')

            elif flask.request.form['state'] == 'unarchive':
                result = helpers.manage_set_active_status(item, 1)
                if result == False:
                    flask.flash('You do not own that item.')

            elif flask.request.form['state'] == 'delete':
                result = helpers.manage_delete_item(item)
                if result == False:
                    flask.flash('You do not own that item.')

    return helpers.display_managed_items()


@blueprint.route('/marketplace/manage_confirm', methods=['GET'])
def manage_confirm():
    if 'username' not in flask.session:
        # they're not logged in, kick them out
        flask.flash('Login required to access that page.')
        flask.session['next'] = flask.url_for('.manage')
        return helpers.render_with_top_marketplace_bar('requires_login.html')

    if 'state' in flask.request.args:
        if 'item' not in flask.request.args:
            flask.flash('Invalid URL')

        else:
            item = flask.request.args['item']

            # archive, unarchive, delete
            if flask.request.args['state'] == 'archive':
                return helpers.manage_display_confirmation(
                    action='archive', item_id=item)

            elif flask.request.args['state'] == 'unarchive':
                return helpers.manage_display_confirmation(
                    action='unarchive', item_id=item)

            elif flask.request.args['state'] == 'delete':
                return helpers.manage_display_confirmation(
                    action='delete', item_id=item)

    return helpers.display_managed_items()


@blueprint.route('/marketplace/sell', methods=['GET', 'POST'])
def sell():
    username = flask.session.get('username')
    if username is None:
        # they're not logged in, kick them out
        flask.flash('Login required to access that page.')
        flask.session['next'] = flask.url_for('.sell')
        return helpers.render_with_top_marketplace_bar('requires_login.html')

    # Extract item id
    item_id = flask.request.args.get('item_id')
    if item_id is not None:
        try:
            item_id = int(item_id)
        except ValueError:
            flask.flash('Invalid item')
            return flask.redirect(flask.url_for('.sell'))

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
        textbook_id = form.get('textbook_id')
        item = {
            'cat_id': int(form.get('cat')),
            'textbook_id': textbook_id and int(textbook_id),
            'textbook_title': form['textbook_title'],
            'textbook_author': form['textbook_author'],
            'textbook_edition': form['textbook_edition'],
            'textbook_isbn': form['textbook_isbn'],
            'condition': form['condition'],
            'price': form['price'],
            'details': form['details'],
            'images': [image for image in form.getlist('images') if image]
        }
    elif editing:
        item = helpers.table_fetch(
            'marketplace_items',
            one=True,
            fields=SELL_FIELDS,
            attrs={'item_id': item_id})
        if item is None:
            # no data? the item_id must be wrong
            flask.flash('Invalid item')
            return flask.redirect(flask.url_for('.sell'))

        # make sure the current user is the one who posted the item
        # TODO: use permissions
        if item['user_id'] != get_user_id(username):
            if flask.request.referrer is None:
                # there's no previous page? that's weird, just go home
                return flask.redirect(flask.url_for('home'))
            else:
                flask.flash('You do not have permission to edit this item.')
                # go back to the previous page
                return flask.redirect(flask.request.referrer)

        item['images'] = helpers.table_fetch(
            'marketplace_images',
            fields=['img_link'],
            attrs={'item_id': item_id})
    else:
        item = {'images': []}

    if saving:
        errors = []
        cat_title = helpers.table_fetch(
            'marketplace_categories',
            one=True,
            fields=['cat_title'],
            attrs={'cat_id': item['cat_id']})
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
            isbn = item['isbn']
            if isbn and not helpers.validate_isbn(isbn):
                errors.append('Invalid textbook ISBN')
        elif not item['item_title']:
            errors.append('Missing item title')
        price = item['price']
        if not (price and helpers.validate_price(price)):
            errors.append('Invalid price')
        images = item['images']
        for i in range(len(images)):
            image = validate_image(images[i])
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
                item_id = helpers.create_new_listing(item)
                flask.flash('Posted!')
            return flask.redirect(flask.url_for('.view', item_id=item_id))

    # Otherwise, they have not submitted anything, so render the form
    item['images'] += [''] * (MAX_IMAGES - len(item['images']))

    categories = helpers.table_fetch(
        'marketplace_categories', fields=['cat_id', 'cat_title'])
    textbooks_cat, = (cat['cat_id'] for cat in categories if cat['cat_title'] == 'Textbooks')
    textbooks = helpers.table_fetch('marketplace_textbooks')
    return helpers.render_with_top_marketplace_bar(
        'sell.html',
        state=state,
        item_id=item_id,
        item=item,
        MAX_IMAGES=MAX_IMAGES,
        categories=categories,
        textbooks=textbooks,
        textbooks_cat=textbooks_cat,
        conditions=CONDITIONS)
