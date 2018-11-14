import flask
import pymysql.cursors

from donut.auth_utils import get_user_id

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


def get_year_courses():
    """
    Returns {'number', name', 'units'[3], 'instructor', 'terms'} structs
    for all courses in the most recent FA, WI, and SP terms.
    """
    # Find most recent year for each term that has courses
    term_years = {}
    for term_year in get_terms():
        term = term_year['term']
        if term not in term_years: term_years[term] = term_year['year']
    query = """
        SELECT
            course_id,
            CONCAT(department, ' ', course_number) AS number,
            name,
            units_lecture, units_lab, units_homework
        FROM courses
        WHERE year = %s AND term = %s
    """
    instructor_query = """
        SELECT DISTINCT instructor
        FROM sections NATURAL JOIN instructors
        WHERE course_id = %s
    """
    courses = {}  # mapping of course numbers to course structs
    with flask.g.pymysql_db.cursor() as cursor:
        for term, year in term_years.items():
            cursor.execute(query, (year, term))
            for course in cursor.fetchall():
                number = course['number']
                cursor.execute(instructor_query, course['course_id'])
                instructors = cursor.fetchall()
                if len(instructors) == 1:
                    instructor = instructors[0]['instructor']
                else:
                    instructor = None
                matching_course = courses.get(number)
                if matching_course:
                    matching_course['terms'].append(term)
                    matching_course['ids'].append(course['course_id'])
                    if instructor != matching_course['instructor']:
                        matching_course['instructor'] = None
                else:
                    courses[number] = {
                        # Separate course id for each term
                        'ids': [course['course_id']],
                        'number':
                        number,
                        'name':
                        course['name'],
                        'units': [
                            course['units_lecture'], course['units_lab'],
                            course['units_homework']
                        ],
                        'instructor':
                        instructor,
                        'terms': [term]
                    }
    return sorted(courses.values(), key=lambda course: course['number'])


def add_planner_course(username, course_id, year):
    user_id = get_user_id(username)
    query = 'INSERT INTO planner_courses (user_id, course_id, year) VALUES (%s, %s, %s)'
    with flask.g.pymysql_db.cursor() as cursor:
        cursor.execute(query, (user_id, course_id, year))


def drop_planner_course(username, course_id, year):
    user_id = get_user_id(username)
    query = """
        DELETE FROM planner_courses
        WHERE user_id = %s AND course_id = %s AND year = %s
    """
    with flask.g.pymysql_db.cursor() as cursor:
        cursor.execute(query, (user_id, course_id, year))


def get_user_planner_courses(username):
    query = """
        SELECT
            course_id,
            CONCAT(department, ' ', course_number) AS number,
            term,
            units,
            planner_year
        FROM users NATURAL JOIN planner_courses NATURAL JOIN courses
        WHERE username = %s
        ORDER BY units DESC, number
    """
    with flask.g.pymysql_db.cursor() as cursor:
        cursor.execute(query, username)
        courses = cursor.fetchall()
    return [{
        'ids': [course['course_id']],
        'number': course['number'],
        'units': course['units'],
        'terms': [course['term']],
        'year': course['planner_year']
    } for course in courses]
