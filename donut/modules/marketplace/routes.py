import flask
import json

from donut.modules.marketplace import blueprint, helpers

@blueprint.route('/marketplace')
def marketplace():
    """Display marketplace page."""

    return helpers.render_with_top_marketplace_bar('marketplace.html', cat_id=0)
    # cat_id = 0 indicates that the select object should be set to "all
    # categories", which is the default


@blueprint.route('/marketplace/view')
def category():
    """Display all results in that category, with no query."""

    category_id = flask.request.args["cat"]

    fields = []
    if helpers.get_category_name_from_id(category_id) == "Textbooks":
        fields = ["textbook_title", "textbook_author", "textbook_edition", "item_price", "user_id", "item_timestamp"]
    else:
        fields = ["item_title", "item_price", "user_id", "item_timestamp"]

    (datalist, headers, links) = helpers.generate_search_table(fields=fields, attrs={"cat_id": category_id})

    return helpers.render_with_top_marketplace_bar('search.html', datalist=datalist, cat_id=category_id, headers=headers, links=links)


@blueprint.route('/marketplace/search')
def query():
    """Displays all results for the query in category category_id, which can be
       'all' if no category is selected."""

    category_id = flask.request.args["cat"]
    query = flask.request.args["q"]

    fields = ["cat_id", "item_title", "textbook_title", "item_price", "user_id", "item_timestamp"]
    # Create a dict of the passed in attributes which are filterable
    filterable_attrs = ["item_id", "cat_id", "user_id", "item_title",
            "item_details", "item_images", "item_condition",
            "item_price", "item_timestamp", "item_active",
            "textbook_id", "textbook_isbn", "textbook_edition", "textbook_title"]
    attrs = { tup:flask.request.args[tup]
            for tup in flask.request.args if tup in filterable_attrs }
    if category_id == "all":
        category_id = 0
    else:
        attrs["cat_id"] = category_id
        # only pass in the cat_id to get_marketplace_items_list_data if it's not
        # "all", because cat_id (and everything in attrs) goes into a WHERE
        # clause, and not specifying is the same as selecting all.

    # now, the category id had better be a number
    try:
        cat_id_num = int(category_id)
        (datalist, headers, links) = helpers.generate_search_table(fields=fields, attrs=attrs)

        return helpers.render_with_top_marketplace_bar('search.html', datalist=datalist, cat_id=cat_id_num, headers=headers, links=links)

    except ValueError:
        # not a number? something's wrong
        return flask.render_template('404.html')


@blueprint.route('/marketplace/sell', methods=['GET', 'POST'])
def sell():
    print(flask.session)
    print(flask.request.form)

    # if the data or the page in general has errors, we don't let the user continue to the next page
    hasErrors = False
    # PAGES
    # -----
    # 1:  Select a category (default first page)
    # 10: Select a textbook (special, appears between pages 1 and 2 if the category is 'Textbooks')
    # 2:  Input information about the listing
    # 3:  Confirm that info is correct
    # 4:  Add data to database, show success message

    page = 1 # default is first page; category select page
    if "page" in flask.request.form:
        # but if we pass it in, get it
        page = int(flask.request.form["page"])

    if not page in [1, 10, 2, 3, 4]:
        flask.flash('Invalid page')
        hasErrors = True


    # STATES
    # ------
    # blank: defaults to new
    # new:   making a new listing
    # edit:  editing an old listing

    state = 'new' # if state isn't in request.args, it's new
    if "state" in flask.request.args:
        # but if it's there, get it
        state = flask.request.args["state"]

    if not state in ["new", "edit"]:
        flask.flash('Invalid state')
        hasErrors = True

    item_id = None
    stored = {}
    storedFields = ["textbook_id", "item_id", "cat_id", "user_id", "item_title", "item_details", "item_condition", "item_price", "item_timestamp", "item_active", "textbook_edition", "textbook_isbn", "textbook_title", "textbook_author"]
    for field in storedFields:
        stored[field] = ""

    if state == 'edit':
        if 'item_id' not in flask.request.args:
            flask.flash('Invalid item')
            hasErrors = True
        else:
            item_id = int(flask.request.args['item_id'])
            data = helpers.get_table_list_data(['marketplace_items', 'marketplace_textbooks'], storedFields, {'item_id': item_id}, "NATURAL LEFT JOIN")[0]
            for i in range(len(data)):
                stored[storedFields[i]] = data[i]

    # prev_page is used for the back button
    prev_page = None
    if "prev_page" in flask.request.form:
        prev_page = int(flask.request.form["prev_page"])
        if not prev_page in [1, 10, 2, 3, 4]:
            flask.flash('Invalid page')
            hasErrors = True

    # category_id is used to specify which category is active
    # get_table_list_data always returns a list of lists
    # turn the resulting 2d list into a map from cat_id to cat_title
    cat_id_map = {sublist[0]: sublist[1] for sublist in helpers.get_table_list_data("marketplace_categories", ["cat_id", "cat_title"])}
    cat_title = None
    if "cat_id" in flask.request.form:
        # flask.request.form should override the database if the user selects a new category
        stored["cat_id"] = int(flask.request.form["cat_id"])
        if stored["cat_id"] not in cat_id_map:
            flask.flash('Invalid category')
            hasErrors = True
        else:
            # get the category title from the id using the map
            cat_title = cat_id_map[stored["cat_id"]]

    # if we're past page 1, we need category to be selected
    if page > 1 and stored["cat_id"] == None:
            flask.flash('Category must be selected')
            hasErrors = True

    # action is used if we need to perform an action on the server-side
    if "action" in flask.request.form:
        if flask.request.form["action"] == "add-textbook":
            # only called on the textbook_select page; page 10
            if page != 10:
                flask.flash('Invalid action')
                hasErrors = True
            else:
                textbook_title = flask.request.form["textbook_title"]
                textbook_author = flask.request.form["textbook_author"]
                if textbook_title == "" or textbook_author == "":
                    flask.flash("Textbook title and textbook author can't be blank")
                    hasErrors = True
                elif not helpers.add_textbook(textbook_title, textbook_author):
                    # add_textbook returns false if it fails
                    flask.flash('Textbook already exists!')
                    hasErrors = True

    if hasErrors:
        # there's an error, so we can't change the page like the (continue or back) button would've done
        page = prev_page
    else:
        # nothing's wrong, so increment the page
        # if the category is textbooks, insert a page between pages 1 and 2
        if prev_page != None and cat_title == "Textbooks":
            # if the user was on page 1 and hit continue, or on page 2 and hit back, send them to 10 instead
            if (page == 2 and prev_page == 1) or (page == 1 and prev_page == 2):
                page = 10
        pass


    if page == 1:
        # generate the hidden values
        hidden = helpers.generate_hidden_form_elements(['cat_id'])
        hidden.append(['prev_page', page])

        return helpers.render_with_top_marketplace_bar('sell/sell_1.html', page=page, state=state, category_id=stored['cat_id'], hidden=hidden)

    elif page == 10:
        # get a list of textbooks to select from
        textbooks = helpers.get_table_list_data("marketplace_textbooks", ["textbook_id", "textbook_title", "textbook_author"])
        textbook_id = flask.request.form.get("textbook_id", None)

        # generate the hidden values
        hidden = helpers.generate_hidden_form_elements(['item_title', 'textbook_id'])
        hidden.append(['prev_page', page])

        return helpers.render_with_top_marketplace_bar('sell/sell_10.html', page=page, state=state, textbooks=textbooks, old_textbook_id=textbook_id, hidden=hidden)

    elif page == 2:
        validation_errors = [] # TODO: validation

        # get correct stored values
        for field in storedFields:
            if field == "textbook_id" and cat_title == "Textbooks":
                # we also want to put textbook_title and textbook_author in stored,
                # but they won't be in request.form
                # so we get them here
                textbook_id = flask.request.form["textbook_id"]
                textbook_info = helpers.get_table_list_data("marketplace_textbooks", ["textbook_title", "textbook_author"], {"textbook_id": textbook_id})
                (stored["textbook_title"], stored["textbook_author"]) = textbook_info[0]
            if field in flask.request.form:
                stored[field] = flask.request.form[field]

        # generate the hidden values
        hidden = []
        if cat_title == 'Textbooks':
            # we need to pass textbook_id, but almost nothing else
            hidden = helpers.generate_hidden_form_elements(['textbook_edition', 'textbook_isbn', 'item_title', 'item_condition', 'item_price', 'item_details'])
        else:
            hidden = helpers.generate_hidden_form_elements(['textbook_id', 'textbook_edition', 'textbook_isbn', 'item_title', 'item_condition', 'item_price', 'item_details'])
        hidden.append(['prev_page', page])

        return helpers.render_with_top_marketplace_bar('sell/sell_2.html', page=page, state=state, cat_title=cat_title, stored=stored, errors=validation_errors, hidden=hidden)

    elif page == 3:

        for field in storedFields:
            if field == "textbook_id" and cat_title == "Textbooks":
                # we also want to put textbook_title and textbook_author in stored,
                # but they won't be in request.form
                # so we get them here
                textbook_id = flask.request.form["textbook_id"]
                textbook_info = helpers.get_table_list_data("marketplace_textbooks", ["textbook_title", "textbook_author"], {"textbook_id": textbook_id})
                (stored["textbook_title"], stored["textbook_author"]) = textbook_info[0]
            if field in flask.request.form:
                stored[field] = flask.request.form[field]

        # generate the hidden values
        hidden = []
        if cat_title == 'Textbooks':
            hidden = helpers.generate_hidden_form_elements(['item_title'])
        else:
            hidden = helpers.generate_hidden_form_elements(['textbook_id', 'textbook_edition', 'textbook_isbn'])
        hidden.append(['prev_page', page])
        return helpers.render_with_top_marketplace_bar('sell/sell_3.html', page=page, state=state, cat_title=cat_title, stored=stored, hidden=hidden)

    elif page == 4:
        for field in storedFields:
            if field == "textbook_id" and cat_title == "Textbooks":
                # we also want to put textbook_title and textbook_author in stored,
                # but they won't be in request.form
                # so we get them here
                textbook_id = flask.request.form["textbook_id"]
                textbook_info = helpers.get_table_list_data("marketplace_textbooks", ["textbook_title", "textbook_author"], {"textbook_id": textbook_id})
                # get_table_list_data returns a list of lists, so grab the inner list using [0]
                (stored["textbook_title"], stored["textbook_author"]) = textbook_info[0]
            if field in flask.request.form:
                stored[field] = flask.request.form[field]

        stored["user_id"] = 1 # TODO: once logins and that sort of stuff works, get the actual user id
        # if we are creating a new item listing, insert it into the database.
        # otherwise, if we are editing an item that already exists, we need
        # to update the listing.
        stored["cat_title"] = cat_title
        if (state == "new"):
            result = helpers.createNewListing(stored)
        else:
            result = helpers.updateCurrentListing(item_id, stored);


        return helpers.render_with_top_marketplace_bar('sell/sell_4.html', result=result)



@blueprint.route('/1/marketplace_items')
def get_marketplace_items_list():
    """GET /1/marketplace_items/"""

    # Create a dict of the passed in attributes which are filterable
    filterable_attrs = ["item_id", "cat_id", "user_id", "item_title",
            "item_details", "item_images", "item_condition",
            "item_price", "item_timestamp", "item_active",
            "textbook_id", "textbook_isbn", "textbook_edition"]
    attrs = { tup:flask.request.args[tup]
            for tup in flask.request.args if tup in filterable_attrs }
    # Get the fields to return if they were passed in
    fields = None
    if "fields" in flask.request.args:
        fields = [f.strip() for f in flask.request.args["fields"].split(',')]

    return json.dumps(helpers.get_marketplace_items_list_data(fields=fields, attrs=attrs))
