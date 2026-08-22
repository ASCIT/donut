import flask

from donut import auth_utils

from . import blueprint, helpers


def check_admin():
    if not auth_utils.check_login():
        return False
    return auth_utils.is_admin()


@blueprint.route('/db_admin')
def index():
    if not check_admin():
        return flask.abort(403)
    tables = helpers.get_tables()
    return flask.render_template('db_admin/index.html', tables=tables)


@blueprint.route('/db_admin/table/<table>')
def browse(table):
    if not check_admin():
        return flask.abort(403)
    helpers.validate_table(table)
    try:
        page = max(1, int(flask.request.args.get('page', 1)))
    except ValueError:
        page = 1
    query = flask.request.args.get('q') or None
    rows, total = helpers.fetch_rows(table, page, query)
    columns = helpers.visible_columns(table)
    pk = helpers.get_primary_key(table)

    def row_pk(row):
        return helpers.encode_pk({c: row[c] for c in pk})

    pages = max(1, -(-total // helpers.ROWS_PER_PAGE))
    return flask.render_template(
        'db_admin/browse.html',
        table=table,
        columns=columns,
        rows=rows,
        row_pk=row_pk,
        read_only=helpers.is_read_only(table),
        page=page,
        pages=pages,
        total=total,
        query=query or '')


@blueprint.route('/db_admin/table/<table>/new', methods=['GET', 'POST'])
def new_row(table):
    if not check_admin():
        return flask.abort(403)
    helpers.validate_table(table)
    if helpers.is_read_only(table):
        return flask.abort(403)
    columns = helpers.visible_columns(table)
    if flask.request.method == 'GET':
        return flask.render_template(
            'db_admin/edit.html', table=table, columns=columns, row=None)

    data = helpers.build_changes(table, flask.request.form)
    try:
        helpers.insert_row(table, data)
    except Exception:
        flask.flash('Failed to insert row (check values and required fields).')
        return flask.redirect(
            flask.url_for('db_admin.new_row', table=table))
    return flask.redirect(flask.url_for('db_admin.browse', table=table))


@blueprint.route('/db_admin/table/<table>/edit/<pk>')
def edit_row(table, pk):
    if not check_admin():
        return flask.abort(403)
    helpers.validate_table(table)
    if helpers.is_read_only(table):
        return flask.abort(403)
    pk_dict = helpers.decode_pk(table, pk)
    row = helpers.fetch_row(table, pk_dict)
    if row is None:
        return flask.abort(404)
    columns = helpers.visible_columns(table)
    return flask.render_template(
        'db_admin/edit.html', table=table, columns=columns, row=row, pk=pk)


@blueprint.route('/db_admin/table/<table>/edit/<pk>', methods=['POST'])
def update_row(table, pk):
    if not check_admin():
        return flask.abort(403)
    helpers.validate_table(table)
    if helpers.is_read_only(table):
        return flask.abort(403)
    pk_dict = helpers.decode_pk(table, pk)
    old_row = helpers.fetch_row(table, pk_dict)
    if old_row is None:
        return flask.abort(404)
    data = helpers.build_changes(table, flask.request.form, old_row)
    helpers.update_row(table, pk_dict, data)
    return flask.redirect(flask.url_for('db_admin.browse', table=table))


@blueprint.route('/db_admin/table/<table>/delete/<pk>', methods=['POST'])
def delete_row(table, pk):
    if not check_admin():
        return flask.abort(403)
    helpers.validate_table(table)
    if helpers.is_read_only(table):
        return flask.abort(403)
    pk_dict = helpers.decode_pk(table, pk)
    helpers.delete_row(table, pk_dict)
    return flask.redirect(flask.url_for('db_admin.browse', table=table))


@blueprint.route('/db_admin/logs')
def logs():
    if not check_admin():
        return flask.abort(403)
    entries = helpers.get_audit_logs()
    return flask.render_template('db_admin/logs.html', entries=entries)
