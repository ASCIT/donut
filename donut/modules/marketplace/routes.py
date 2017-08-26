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

    #datalist = helpers.generate_table_data(fields=fields, attrs={"cat_id": category_id})

    #headers = helpers.process_category_headers(fields)
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
    if flask.request.method == 'GET':
        # you can only GET the main category select page, from the topbar
        # so render and return it
        return helpers.render_with_top_marketplace_bar('sell_cat.html')

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
        page = flask.request.form["page"]

    if not page in [1, 10, 2, 3, 4]:
        flask.flash('Invalid page')


    # STATES
    # ------
    # blank: defaults to new
    # new:   making a new listing
    # edit:  editing an old listing

    state = "new" # if state isn't in request.args, it's new
    if "state" in flask.request.args:
        # but if it's there, get it
        state = flask.request.args["state"]

    if not state in ["new", "edit"]:
        flask.flash('Invalid state')


    # prev_page is used for the back button
    prev_page = None
    if "prev_page" in flask.request.form:
        prev_page = flask.request.form["prev_page"]
        if not prev_page in [1, 10, 2, 3, 4]:
            flask.flash('Invalid page')


    # cat_id
    cat_id = None
    if "cat_id" in flask.request.form:
        cat_id = flask.request.form["cat_id"]
        if cat_id not in helpers.get_table_list_data("marketplace_categories",
                ["cat_id"]):
            flask.flash('Invalid category')
    else:
        if page > 1:
            flask.flash('Category must be selected')

    if "action" in flask.request.form:
        if flask.request.form["action"] == "add_textbook":
            # only called on the textbook_select page; page 10
            if page != 10:
                flask.flash('Invalid action')

    if page == 1:
        return helpers.render_with_top_marketplace_bar('sell_cat.html')
    if page == 10:
        return helpers.render_with_top_marketplace_bar('sell.html')



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