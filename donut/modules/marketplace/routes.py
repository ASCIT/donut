import flask
import json

from donut.modules.marketplace import blueprint, helpers
from donut.modules.core.helpers import get_name_and_email
from donut.auth_utils import get_user_id, check_permission
from donut.resources import Permissions


@blueprint.route('/marketplace')
def marketplace():
    """Display marketplace page."""

    return helpers.render_with_top_marketplace_bar(
        'marketplace.html', cat_id=0)
    # cat_id = 0 indicates that the select object should be set to 'all
    # categories', which is the default


@blueprint.route('/marketplace/view')
def category():
    """Display all results in that category, with no query."""

    if 'cat' not in flask.request.args:
        return flask.render_template('404.html'), 404

    category_id = flask.request.args['cat']

    fields = []
    if helpers.get_category_name_from_id(category_id) == 'Textbooks':
        fields = [
            'textbook_title', 'textbook_author', 'textbook_edition',
            'item_price', 'user_id', 'item_timestamp'
        ]
    else:
        fields = ['item_title', 'item_price', 'user_id', 'item_timestamp']

    (datalist, headers, links) = helpers.generate_search_table(
        fields=fields, attrs={'cat_id': category_id})

    return helpers.render_with_top_marketplace_bar(
        'search.html',
        datalist=datalist,
        cat_id=category_id,
        headers=headers,
        links=links)


@blueprint.route('/marketplace/search')
def query():
    """Displays all results for the query in category category_id, which can be
       'all' if no category is selected."""

    if 'cat' not in flask.request.args or 'q' not in flask.request.args:
        return flask.render_template('404.html'), 404

    category_id = flask.request.args['cat']
    query = flask.request.args['q']

    fields = [
        'cat_id', 'item_title', 'textbook_title', 'item_price', 'user_id',
        'item_timestamp'
    ]
    # Create a dict of the passed in attributes which are filterable
    filterable_attrs = [
        'item_id', 'cat_id', 'user_id', 'item_title', 'item_details',
        'item_images', 'item_condition', 'item_price', 'item_timestamp',
        'item_active', 'textbook_id', 'textbook_isbn', 'textbook_edition',
        'textbook_title'
    ]
    attrs = {
        tup: flask.request.args[tup]
        for tup in flask.request.args if tup in filterable_attrs
    }
    if category_id == 'all':
        category_id = 0
    else:
        attrs['cat_id'] = category_id
        # only pass in the cat_id to get_marketplace_items_list_data if it's not
        # 'all', because cat_id (and everything in attrs) goes into a WHERE
        # clause, and not specifying is the same as selecting all.

    # now, the category id had better be a number
    try:
        cat_id_num = int(category_id)
        (datalist, headers, links) = helpers.generate_search_table(
            fields=fields, attrs=attrs, query=query)

        return helpers.render_with_top_marketplace_bar(
            'search.html',
            datalist=datalist,
            cat_id=cat_id_num,
            headers=headers,
            links=links)

    except ValueError:
        # not a number? something's wrong
        return flask.render_template('404.html'), 404


@blueprint.route('/marketplace/view_item')
def view_item():
    """View additional details about item <item_id>, passed through flask.request.args."""

    if 'item_id' not in flask.request.args:
        return flask.render_template('404.html'), 404

    # make sure item_id is a number
    item_id = None
    try:
        item_id = int(flask.request.args['item_id'])
    except ValueError:
        return flask.render_template('404.html'), 404

    stored = {}
    stored_fields = [
        'textbook_id', 'item_id', 'cat_id', 'user_id', 'item_title',
        'item_details', 'item_condition', 'item_price', 'item_timestamp',
        'item_active', 'textbook_edition', 'textbook_isbn', 'textbook_title',
        'textbook_author'
    ]
    data = helpers.get_table_list_data(
        'marketplace_items NATURAL LEFT JOIN marketplace_textbooks',
        stored_fields, {'item_id': item_id})

    # make sure the item_id is a valid item, i.e. data is nonempty
    if len(data) == 0:
        return flask.render_template('404.html'), 404

    # 2d list to the first list inside it
    data = data[0]

    for i in range(len(data)):
        stored[stored_fields[i]] = data[i]

    # cat_title from cat_id
    cat_id_map = {
        sublist[0]: sublist[1]
        for sublist in helpers.get_table_list_data('marketplace_categories',
                                                   ['cat_id', 'cat_title'])
    }
    cat_title = cat_id_map[stored['cat_id']]

    # full_name and email from user_id
    (stored['full_name'],
     stored['email']) = get_name_and_email(stored['user_id'])

    # if any field is None, replace it with '' to display more cleanly
    for field in stored:
        if stored[field] == None:
            stored[field] = ''

    has_edit_privs = False
    if 'username' in flask.session:
        current_user_id = get_user_id(flask.session['username'])
        if stored['user_id'] == current_user_id or check_permission(
                Permissions.ADMIN):
            has_edit_privs = True

    return helpers.render_with_top_marketplace_bar(
        'view_item.html',
        stored=stored,
        cat_title=cat_title,
        has_edit_privs=has_edit_privs)


@blueprint.route('/marketplace/manage', methods=['GET'])
def manage():
    if 'username' not in flask.session:
        # they're not logged in, kick them out
        flask.session['next'] = flask.url_for('.manage')
        return helpers.render_with_top_marketplace_bar('requires_login.html')

    if 'state' in flask.request.args:
        has_edit_privs = False
        current_user_id = get_user_id(flask.session['username'])
        #if stored['user_id'] == current_user_id or check_permission( Permissions.ADMIN):
        # has_edit_privs = True

        # archive, unarchive, delete
        if flask.request.args['state'] == 'archive':
            if 'item' not in flask.request.args:
                return flask.render_template('404.html'), 404
            item = flask.request.args['item']
            helpers.manage_set_active_status(item, 0)
            return helpers.display_managed_items()

        elif flask.request.args['state'] == 'unarchive':
            if 'item' not in flask.request.args:
                return flask.render_template('404.html'), 404
            item = flask.request.args['item']
            helpers.manage_set_active_status(item, 1)
            return helpers.display_managed_items()

        elif flask.request.args['state'] == 'delete':
            pass

        else:
            return flask.render_template('404.html'), 404

    else:
        return helpers.display_managed_items()


@blueprint.route('/marketplace/sell', methods=['GET', 'POST'])
def sell():
    if 'username' not in flask.session:
        # they're not logged in, kick them out
        flask.session['next'] = flask.url_for('.sell')
        return helpers.render_with_top_marketplace_bar('requires_login.html')

    from donut.modules.marketplace.constants import Page

    # if the data or the page in general has errors, we don't let the user continue to the next page
    has_errors = False
    # PAGES
    # -----
    # Page.CATEGORY:     Select a category (default first page)
    # Page.TEXTBOOK:     Select a textbook (special, appears between pages 1 and 2 if the category is 'Textbooks')
    # Page.INFORMATION:  Input information about the listing
    # Page.CONFIRMATION: Confirm that info is correct
    # Page.SUBMIT:       Add data to database, show success message

    page = Page.CATEGORY  # default is first page; category select page
    if 'page' in flask.request.form:
        # but if we pass it in, get it
        page = Page.__members__[flask.request.form['page']]

    if not page in Page:
        flask.flash('Invalid page')
        has_errors = True

    # STATES
    # ------
    # blank: defaults to new
    # new:   making a new listing
    # edit:  editing an old listing

    state = 'new'  # if state isn't in request.args, it's new
    if 'state' in flask.request.args:
        # but if it's there, get it
        state = flask.request.args['state']

    if not state in ['new', 'edit']:
        flask.flash('Invalid state')
        has_errors = True

    item_id = None
    stored = {}
    stored_fields = [
        'textbook_id', 'item_id', 'cat_id', 'user_id', 'item_title',
        'item_details', 'item_condition', 'item_price', 'item_timestamp',
        'item_active', 'textbook_edition', 'textbook_isbn', 'textbook_title',
        'textbook_author'
    ]
    for field in stored_fields:
        stored[field] = ''

    if state == 'edit':
        if 'item_id' not in flask.request.args:
            flask.flash('Invalid item')
            has_errors = True
        else:
            item_id = int(flask.request.args['item_id'])
            data = helpers.get_table_list_data(
                'marketplace_items NATURAL LEFT JOIN marketplace_textbooks',
                stored_fields, {'item_id': item_id})

            if len(data) == 0:
                # no data? the item_id must be wrong
                flask.flash('Invalid item')
                has_errors = True

            else:
                # unwrap 2d array
                data = data[0]
                for i in range(len(data)):
                    stored[stored_fields[i]] = data[i]

            # make sure the current user is the one who posted the item
            current_user_id = get_user_id(flask.session['username'])
            if stored['user_id'] != current_user_id and not check_permission(
                    Permissions.ADMIN):
                if flask.request.referrer == None:
                    # there's no previous page? that's weird, just go home
                    return flask.redirect(flask.url_for('home'))
                else:
                    flask.flash(
                        'You do not have permission to edit this item.')
                    return flask.redirect(
                        flask.request.referrer)  # go back to the previous page

    # prev_page is used for the back button
    prev_page = page
    if 'prev_page' in flask.request.form:
        # make sure flask.request.form['prev_page'] is an int, and that it's a valid page to go to (i.e. in the enum)
        try:
            prev_page = Page(int(flask.request.form['prev_page']))
        except ValueError:
            flask.flash('Invalid page')
            has_errors = True

    # category_id is used to specify which category is active
    # get_table_list_data always returns a list of lists
    # turn the resulting 2d list into a map from cat_id to cat_title
    cat_id_map = {
        sublist[0]: sublist[1]
        for sublist in helpers.get_table_list_data('marketplace_categories',
                                                   ['cat_id', 'cat_title'])
    }
    cat_title = None
    if 'cat_id' in flask.request.form:
        # flask.request.form should override the database if the user selects a new category
        stored['cat_id'] = int(flask.request.form['cat_id'])
        if stored['cat_id'] not in cat_id_map:
            flask.flash('Invalid category')
            has_errors = True
        else:
            # get the category title from the id using the map
            cat_title = cat_id_map[stored['cat_id']]

    # if we're past page 1, we need category to be selected
    if page != Page.CATEGORY and stored['cat_id'] == None:
        flask.flash('Category must be selected')
        has_errors = True

    # action is used if we need to perform an action on the server-side
    if 'action' in flask.request.form:
        if flask.request.form['action'] == 'add-textbook':
            # only called on the textbook select page
            if page != Page.TEXTBOOK:
                flask.flash('Invalid action')
                has_errors = True
            else:
                textbook_title = flask.request.form['textbook_title']
                textbook_author = flask.request.form['textbook_author']
                if textbook_title == '' or textbook_author == '':
                    flask.flash(
                        'Textbook title and textbook author can\'t be blank.')
                    has_errors = True
                elif not helpers.add_textbook(textbook_title, textbook_author):
                    # add_textbook returns false if it fails
                    flask.flash('Textbook already exists!')
                    has_errors = True

    if has_errors:
        # there's an error, so we can't change the page like the (continue or back) button would've done
        page = prev_page
    else:
        # nothing's wrong, so increment the page
        # if the category is textbooks, insert a page between INFO and CATEGORY pages
        if prev_page != None and cat_title == 'Textbooks':
            # if the user was on page 1 and hit continue, or on page 2 and hit back, send them to 10 instead
            if (page == Page.INFORMATION and prev_page == Page.CATEGORY) or (
                    page == Page.CATEGORY and prev_page == Page.INFORMATION):
                page = Page.TEXTBOOK

    if page in [Page.INFORMATION, Page.CONFIRMATION, Page.SUBMIT
                ] and cat_title == 'Textbooks':
        if 'textbook_id' not in flask.request.form or flask.request.form['textbook_id'] == '':
            flask.flash('You need to select a textbook.')
            # go back to the textbook select page
            page = Page.TEXTBOOK
        else:
            # make sure that the textbook_id is valid
            textbook_result = helpers.get_table_list_data(
                'marketplace_textbooks',
                attrs={'textbook_id': flask.request.form['textbook_id']})
            if len(textbook_result) == 0:
                flask.flash('Invalid textbook.')
                page = Page.TEXTBOOK

    # don't allow the user to continue if any data is malformed or essential data is missing
    errors = []
    if page in [Page.CONFIRMATION, Page.SUBMIT]:
        errors += helpers.validate_data()
        if len(errors) != 0:
            page = Page.INFORMATION  # the data was inputted on the INFORMATION page

    if page == Page.CATEGORY:
        # generate the hidden values
        hidden = helpers.generate_hidden_form_elements(['cat_id'])
        hidden.append(['prev_page', page.value])

        return helpers.render_with_top_marketplace_bar(
            'sell/sell_1.html',
            page=page,
            state=state,
            category_id=stored['cat_id'],
            hidden=hidden,
            page_map=Page.__members__)

    elif page == Page.TEXTBOOK:
        # get a list of textbooks to select from
        textbooks = helpers.get_table_list_data('marketplace_textbooks', [
            'textbook_id', 'textbook_title', 'textbook_author'
        ])
        textbook_id = flask.request.form.get('textbook_id', None)

        # generate the hidden values
        hidden = helpers.generate_hidden_form_elements(
            ['item_title', 'textbook_id'])
        hidden.append(['prev_page', page.value])

        return helpers.render_with_top_marketplace_bar(
            'sell/sell_10.html',
            page=page,
            state=state,
            textbooks=textbooks,
            old_textbook_id=textbook_id,
            hidden=hidden)

    elif page == Page.INFORMATION:
        # get correct stored values
        for field in stored_fields:
            if field == 'textbook_id' and cat_title == 'Textbooks':
                # we also want to put textbook_title and textbook_author in stored,
                # but they won't be in request.form
                # so we get them here
                textbook_id = flask.request.form['textbook_id']
                textbook_info = helpers.get_table_list_data(
                    'marketplace_textbooks',
                    ['textbook_title',
                     'textbook_author'], {'textbook_id': textbook_id})
                (stored['textbook_title'],
                 stored['textbook_author']) = textbook_info[0]
            if field in flask.request.form:
                stored[field] = flask.request.form[field]

        # generate the hidden values
        hidden = []
        if cat_title == 'Textbooks':
            # we need to pass textbook_id, but almost nothing else
            hidden = helpers.generate_hidden_form_elements([
                'textbook_edition', 'textbook_isbn', 'item_title',
                'item_condition', 'item_price', 'item_details'
            ])
        else:
            hidden = helpers.generate_hidden_form_elements([
                'textbook_id', 'textbook_edition', 'textbook_isbn',
                'item_title', 'item_condition', 'item_price', 'item_details'
            ])
        hidden.append(['prev_page', page.value])

        return helpers.render_with_top_marketplace_bar(
            'sell/sell_2.html',
            page=page,
            state=state,
            cat_title=cat_title,
            stored=stored,
            errors=errors,
            hidden=hidden)

    elif page == Page.CONFIRMATION:

        for field in stored_fields:
            if field == 'textbook_id' and cat_title == 'Textbooks':
                # we also want to put textbook_title and textbook_author in stored,
                # but they won't be in request.form
                # so we get them here
                textbook_id = flask.request.form['textbook_id']
                textbook_info = helpers.get_table_list_data(
                    'marketplace_textbooks',
                    ['textbook_title',
                     'textbook_author'], {'textbook_id': textbook_id})
                (stored['textbook_title'],
                 stored['textbook_author']) = textbook_info[0]
            if field in flask.request.form:
                stored[field] = flask.request.form[field]

        # generate the hidden values
        hidden = []
        if cat_title == 'Textbooks':
            hidden = helpers.generate_hidden_form_elements(['item_title'])
        else:
            hidden = helpers.generate_hidden_form_elements(
                ['textbook_id', 'textbook_edition', 'textbook_isbn'])
        hidden.append(['prev_page', page.value])
        return helpers.render_with_top_marketplace_bar(
            'sell/sell_3.html',
            page=page,
            state=state,
            cat_title=cat_title,
            stored=stored,
            hidden=hidden)

    elif page == Page.SUBMIT:
        for field in stored_fields:
            if field == 'textbook_id' and cat_title == 'Textbooks':
                # we also want to put textbook_title and textbook_author in stored,
                # but they won't be in request.form
                # so we get them here
                textbook_id = flask.request.form['textbook_id']
                textbook_info = helpers.get_table_list_data(
                    'marketplace_textbooks',
                    ['textbook_title',
                     'textbook_author'], {'textbook_id': textbook_id})
                # get_table_list_data returns a list of lists, so grab the inner list using [0]
                (stored['textbook_title'],
                 stored['textbook_author']) = textbook_info[0]
            if field in flask.request.form:
                stored[field] = flask.request.form[field]

        stored['user_id'] = get_user_id(flask.session['username'])

        # if we are creating a new item listing, insert it into the database.
        # otherwise, if we are editing an item that already exists, we need
        # to update the listing.
        stored['cat_title'] = cat_title
        if (state == 'new'):
            result = helpers.create_new_listing(stored)
        else:
            result = helpers.update_current_listing(item_id, stored)

        return helpers.render_with_top_marketplace_bar(
            'sell/sell_4.html', result=result)
