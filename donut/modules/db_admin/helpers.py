import flask
import json

DATABASE = 'donut'
AUDIT_TABLE = 'db_admin_audit_log'
ROWS_PER_PAGE = 50

# Columns that must never be displayed or edited through the explorer.
HIDDEN_COLUMNS = {('users', 'password_hash')}

# Tables that may only be viewed, never modified.
READ_ONLY_TABLES = {AUDIT_TABLE}


def get_tables():
    """Return a list of all tables in the donut database with row estimates."""
    with flask.g.pymysql_db.cursor() as cursor:
        cursor.execute(
            """
            SELECT table_name, table_rows
            FROM information_schema.tables
            WHERE table_schema = %s
            ORDER BY table_name
            """, (DATABASE, ))
        return [{
            'name': row['table_name'] if 'table_name' in row else row['TABLE_NAME'],
            'rows': row['table_rows'] if 'table_rows' in row else row['TABLE_ROWS'],
            'read_only': (row['table_name'] if 'table_name' in row else row['TABLE_NAME'])
            in READ_ONLY_TABLES
        } for row in cursor.fetchall()]


def validate_table(table):
    """Raise NotFound unless the given name is an actual table."""
    with flask.g.pymysql_db.cursor() as cursor:
        cursor.execute(
            """
            SELECT 1 FROM information_schema.tables
            WHERE table_schema = %s AND table_name = %s
            """, (DATABASE, table))
        if cursor.fetchone() is None:
            flask.abort(404)


def is_read_only(table):
    return table in READ_ONLY_TABLES


def get_columns(table):
    """Return metadata for each column of the given table."""
    with flask.g.pymysql_db.cursor() as cursor:
        cursor.execute(
            """
            SELECT column_name, column_type, is_nullable, column_default,
                   column_key, extra
            FROM information_schema.columns
            WHERE table_schema = %s AND table_name = %s
            ORDER BY ordinal_position
            """, (DATABASE, table))
        columns = []
        for col in cursor.fetchall():
            name = col['column_name']
            columns.append({
                'name': name,
                'type': col['column_type'],
                'nullable': col['is_nullable'] == 'YES',
                'default': col['column_default'],
                'primary_key': col['column_key'] == 'PRI',
                'auto_increment': 'auto_increment' in (col['extra'] or ''),
                'hidden': (table, name) in HIDDEN_COLUMNS
            })
        return columns


def get_primary_key(table):
    """Return the list of primary key column names for the table."""
    columns = [col['name'] for col in get_columns(table) if col['primary_key']]
    if not columns:
        raise ValueError(f'Table {table} has no primary key and cannot be edited')
    return columns


def visible_columns(table):
    return [c for c in get_columns(table) if not c['hidden']]


def fetch_rows(table, page=1, query=None):
    """Fetch one page of rows, optionally filtered by a search string.

    The search matches any column containing the query as a substring.
    Returns (rows, total_count).
    """
    columns = visible_columns(table)
    select_cols = ', '.join(f'`{c["name"]}`' for c in columns)
    order = ', '.join(f'`{c}`' for c in get_primary_key(table))

    where = ''
    args = []
    if query:
        like = f'%{query}%'
        conditions = ' OR '.join(f'`{c["name"]}` LIKE %s' for c in columns)
        where = f'WHERE {conditions}'
        args = [like] * len(columns)

    with flask.g.pymysql_db.cursor() as cursor:
        cursor.execute(
            f'SELECT COUNT(*) AS count FROM `{table}` {where}', args)
        total = cursor.fetchone()['count']

        offset = (page - 1) * ROWS_PER_PAGE
        cursor.execute(
            f'SELECT {select_cols} FROM `{table}` {where} '
            f'ORDER BY {order} LIMIT %s OFFSET %s',
            args + [ROWS_PER_PAGE, offset])
        rows = cursor.fetchall()
    return rows, total


def encode_pk(pk_dict):
    """Encode primary key values as a URL-safe path segment."""
    return json.dumps(list(pk_dict.values()))


def decode_pk(table, encoded):
    """Decode a primary key path segment into {column: value}."""
    pk = get_primary_key(table)
    values = json.loads(encoded)
    if not isinstance(values, list) or len(values) != len(pk):
        flask.abort(404)
    return dict(zip(pk, values))


# Column types that cannot hold an empty string.
NON_STRING_TYPES = (
    'tinyint', 'smallint', 'mediumint', 'int', 'bigint', 'decimal',
    'float', 'double', 'bit', 'bool', 'boolean', 'date', 'datetime',
    'timestamp', 'time', 'year')


def fetch_row(table, pk_dict):
    """Fetch a single row by primary key, hiding protected columns."""
    columns = [c['name'] for c in visible_columns(table)]
    select_cols = ', '.join(f'`{c}`' for c in columns)
    where = ' AND '.join(f'`{c}` = %s' for c in pk_dict)
    with flask.g.pymysql_db.cursor() as cursor:
        cursor.execute(
            f'SELECT {select_cols} FROM `{table}` WHERE {where}',
            list(pk_dict.values()))
        return cursor.fetchone()


def build_changes(table, form, old_row=None):
    """Build submitted values from a form, skipping hidden columns.

    When old_row is provided, unchanged fields are omitted so the audit log
    records only real changes.
    """
    values = {}
    for col in visible_columns(table):
        value = form.get(f'col_{col["name"]}')
        if value is None:
            continue
        if value == '':
            if col['nullable']:
                value = None
            elif col['auto_increment'] or col['default'] is not None or \
                    col['type'].lower().startswith(NON_STRING_TYPES):
                # Let the database apply its default (inserts), or leave
                # the existing value untouched (updates).
                if old_row is None:
                    continue
                # On updates, an omitted field means "keep current value".
                continue
        if old_row is not None and str(old_row[col['name']]) == str(value):
            continue
        values[col['name']] = value
    return values


def insert_row(table, data):
    """Insert a new row and record it in the audit log. Returns the new pk."""
    if is_read_only(table):
        raise PermissionError(f'Table {table} is read-only')
    cols = ', '.join(f'`{c}`' for c in data)
    placeholders = ', '.join(['%s'] * len(data))
    conn = flask.g.pymysql_db
    try:
        conn.begin()
        with conn.cursor() as cursor:
            cursor.execute(
                f'INSERT INTO `{table}` ({cols}) VALUES ({placeholders})',
                list(data.values()))
            pk = [
                c['name'] for c in get_columns(table) if c['primary_key']]
            auto_incremented = [
                c['name'] for c in get_columns(table)
                if c['auto_increment'] and c['primary_key']]
            if len(auto_incremented) == 1:
                pk_dict = {auto_incremented[0]: cursor.lastrowid}
            else:
                pk_dict = {c: data[c] for c in pk if c in data}
            new_row = None
            if set(pk_dict) == set(pk):
                new_row = fetch_row_in_conn(conn, table, pk_dict)
            full_data = new_row if new_row is not None else dict(data)
            write_audit_log(conn, 'insert', table, pk, None, full_data)
        conn.commit()
        return pk_dict
    except Exception:
        conn.rollback()
        raise


def update_row(table, pk_dict, data):
    """Update a row by primary key, logging before/after state."""
    if is_read_only(table):
        raise PermissionError(f'Table {table} is read-only')
    if not data:
        return
    old_row = fetch_full_row(table, pk_dict)
    if old_row is None:
        flask.abort(404)
    set_clause = ', '.join(f'`{c}` = %s' for c in data)
    where = ' AND '.join(f'`{c}` = %s' for c in pk_dict)
    conn = flask.g.pymysql_db
    try:
        conn.begin()
        with conn.cursor() as cursor:
            cursor.execute(
                f'UPDATE `{table}` SET {set_clause} WHERE {where}',
                list(data.values()) + list(pk_dict.values()))
            write_audit_log(
                conn, 'update', table, list(pk_dict.keys()), old_row, data)
        conn.commit()
    except Exception:
        conn.rollback()
        raise


def delete_row(table, pk_dict):
    """Delete a row by primary key, logging its previous state."""
    if is_read_only(table):
        raise PermissionError(f'Table {table} is read-only')
    old_row = fetch_full_row(table, pk_dict)
    if old_row is None:
        flask.abort(404)
    where = ' AND '.join(f'`{c}` = %s' for c in pk_dict)
    conn = flask.g.pymysql_db
    try:
        conn.begin()
        with conn.cursor() as cursor:
            cursor.execute(
                f'DELETE FROM `{table}` WHERE {where}',
                list(pk_dict.values()))
            write_audit_log(
                conn, 'delete', table, list(pk_dict.keys()), old_row, None)
        conn.commit()
    except Exception:
        conn.rollback()
        raise


def fetch_full_row(table, pk_dict):
    """Fetch a row including hidden columns, for audit purposes only."""
    where = ' AND '.join(f'`{c}` = %s' for c in pk_dict)
    with flask.g.pymysql_db.cursor() as cursor:
        cursor.execute(
            f'SELECT * FROM `{table}` WHERE {where}', list(pk_dict.values()))
        return cursor.fetchone()


def fetch_row_in_conn(conn, table, pk_dict):
    """Fetch a full row using an existing connection inside a transaction."""
    where = ' AND '.join(f'`{c}` = %s' for c in pk_dict)
    with conn.cursor() as cursor:
        cursor.execute(
            f'SELECT * FROM `{table}` WHERE {where}', list(pk_dict.values()))
        return cursor.fetchone()


def write_audit_log(conn, action, table, pk_columns, old_row, new_data):
    """Record a mutation in db_admin_audit_log.

    pk_columns: names of the primary key columns
    old_row: full row before the change (None for inserts)
    new_data: full row after the change, or just the changed fields for
              updates (None for deletes)
    """
    from donut import auth_utils
    username = flask.session.get('username')
    user_id = auth_utils.get_user_id(username) if username else 0
    pk_values = [
        old_row[c] for c in pk_columns
    ] if old_row else [new_data.get(c) for c in pk_columns]

    def to_json(data):
        if data is None:
            return None
        return json.dumps({k: str(v) for k, v in data.items()}, default=str)

    with conn.cursor() as cursor:
        cursor.execute(
            f"""
            INSERT INTO `{AUDIT_TABLE}`
                (user_id, request_time, action, table_name, row_pk,
                 old_data, new_data)
            VALUES (%s, NOW(), %s, %s, %s, %s, %s)
            """, (
                user_id, action, table,
                json.dumps([str(v) for v in pk_values]),
                to_json(old_row), to_json(new_data)))


def get_audit_logs(limit=200):
    """Return recent audit log entries with usernames."""
    with flask.g.pymysql_db.cursor() as cursor:
        cursor.execute(
            f"""
            SELECT l.log_id, l.request_time, l.action, l.table_name,
                   l.row_pk, l.old_data, l.new_data,
                   u.username
            FROM `{AUDIT_TABLE}` l
            LEFT JOIN users u USING (user_id)
            ORDER BY l.log_id DESC
            LIMIT %s
            """, (limit, ))
        return cursor.fetchall()
