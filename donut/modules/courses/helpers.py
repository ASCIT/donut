import flask
import pymysql.cursors

TERMS = {'FA': 1, 'WI': 2, 'SP': 3}
TERM_NAMES = {v: k for k, v in TERMS.items()}


def get_terms():
    """
    Returns {'year', 'term'} structs for each year with courses,
    sorted from most to least recent.
    """
    query = 'SELECT DISTINCT year, term FROM courses'

    with flask.g.pymysql_db.cursor() as cursor:
        cursor.execute(query)
        return sorted(
            cursor.fetchall(),
            key=lambda term: (term['year'], term['term']),
            reverse=True)
