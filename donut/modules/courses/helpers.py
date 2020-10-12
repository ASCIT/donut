import flask
import pymysql.cursors
from pymysql.constants import ER
from pymysql.err import IntegrityError

from donut.auth_utils import get_user_id

TERMS = {'FA': 1, 'WI': 2, 'SP': 3}
TERM_NAMES = {v: k for k, v in TERMS.items()}


def try_int(x):
    """
    Converts a float to an int if it is already an integral value.
    Makes the JSON a little smaller.
    """
    as_int = int(x)
    return as_int if as_int == x else x


def get_terms():
    """
    Returns {'year', 'term'} structs for each year with courses,
    sorted from most to least recent.
    """
    query = """
        SELECT DISTINCT year, term FROM courses
        ORDER BY year DESC, (term + 1) % 3 DESC
    """
    with flask.g.pymysql_db.cursor() as cursor:
        cursor.execute(query)
        return cursor.fetchall()


def get_year_courses():
    """
    Returns {'ids'[], number', name', 'units'[3], 'instructor', 'terms'[]}
    structs for all courses in the most recent FA, WI, and SP terms.
    'ids' and 'terms' link the ids of different terms of the same course.
    """
    # Find most recent year for each term that has courses
    term_years = {}
    for term_year in get_terms():
        term = term_year['term']
        if term not in term_years:
            term_years[term] = term_year['year']
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
                instructor = instructors[0]['instructor'] \
                    if len(instructors) == 1 else None
                matching_course = courses.get(number)
                if matching_course:
                    matching_course['terms'].append(term)
                    matching_course['ids'].append(course['course_id'])
                    if instructor != matching_course['instructor']:
                        matching_course['instructor'] = None
                else:
                    units = (course['units_lecture'], course['units_lab'],
                             course['units_homework'])
                    courses[number] = {
                        # Separate course id for each term
                        'ids': [course['course_id']],
                        'number': number,
                        'name': course['name'],
                        'units': tuple(map(try_int, units)),
                        'instructor': instructor,
                        'terms': [term]
                    }
    return sorted(
        courses.values(), key=lambda course: course['number'].lower())


def add_planner_course(username, course_id, year):
    """
    Adds a certain course to a certain user's planner for a given year.
    Year 1 is frosh year, year 2 is smore year, etc.
    """
    user_id = get_user_id(username)
    query = 'INSERT INTO planner_courses (user_id, course_id, planner_year) VALUES (%s, %s, %s)'
    with flask.g.pymysql_db.cursor() as cursor:
        cursor.execute(query, (user_id, course_id, year))


def drop_planner_course(username, course_id, year):
    """
    Removes a certain course from a certain user's planner for a given year.
    Year 1 is frosh year, year 2 is smore year, etc.
    """
    user_id = get_user_id(username)
    query = """
        DELETE FROM planner_courses
        WHERE user_id = %s AND course_id = %s AND planner_year = %s
    """
    with flask.g.pymysql_db.cursor() as cursor:
        cursor.execute(query, (user_id, course_id, year))


def add_planner_placeholder(username, year, term, course, units):
    """
    Adds a placedholder course to a user's planner for a given term.
    Year 1 is frosh year, year 2 is smore year, etc.
    Term 1 is FA, 2 is WI, and 3 is SP.
    """
    user_id = get_user_id(username)
    query = """
        INSERT INTO planner_placeholders
            (user_id, planner_year, term, course_name, course_units)
        VALUES (%s, %s, %s, %s, %s)
    """
    with flask.g.pymysql_db.cursor() as cursor:
        cursor.execute(query, (user_id, year, term, course, units))
        return cursor.lastrowid


def drop_planner_placeholder(username, placeholder_id):
    """
    Removes the placeholder with the given ID from the user's planner.
    Returns whether successful (i.e. the given placeholder did belong to the user).
    """
    user_id = get_user_id(username)
    query = """
        DELETE FROM planner_placeholders
        WHERE placeholder_id = %s AND user_id = %s
    """
    with flask.g.pymysql_db.cursor() as cursor:
        cursor.execute(query, (placeholder_id, user_id))
        return cursor.rowcount > 0


def get_user_planner_courses(username):
    """
    Returns {'ids'[1], 'number', 'units', 'terms'[1], 'year'} structs
    for each course on a certain user's planner.
    Unlike in get_planner_courses(), the unit counts are already summed.
    """
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
        'ids': (course['course_id'], ),
        'number': course['number'],
        'units': try_int(course['units']),
        'terms': (course['term'], ),
        'year': course['planner_year']
    } for course in courses]


def get_user_planner_placeholders(username):
    query = """
        SELECT placeholder_id, planner_year, term, course_name, course_units
        FROM planner_placeholders NATURAL JOIN users
        WHERE username = %s
        ORDER BY course_units DESC, course_name
    """
    with flask.g.pymysql_db.cursor() as cursor:
        cursor.execute(query, username)
        placeholders = cursor.fetchall()
    return [{
        'id': placeholder['placeholder_id'],
        'year': placeholder['planner_year'],
        'term': placeholder['term'],
        'course': placeholder['course_name'],
        'units': try_int(placeholder['course_units'])
    } for placeholder in placeholders]


def get_scheduler_courses(year, term):
    """
    Returns {'id', 'number', 'name', 'units'[3], 'sections'[]} structs for each
    course in a certain term of a certain year.
    'sections' is a list of {'number', 'instructor', 'grades', 'times'} structs.
    """
    query = """
        SELECT
            course_id,
            CONCAT(department, ' ', course_number) AS number,
            name,
            units_lecture, units_lab, units_homework,
            section_number,
            instructor,
            grades_type,
            times,
            locations
        FROM
            courses
            NATURAL JOIN sections
            NATURAL JOIN instructors
            NATURAL JOIN grades_types
        WHERE year = %s AND term = %s
    """
    with flask.g.pymysql_db.cursor() as cursor:
        cursor.execute(query, (year, term))
        sections = cursor.fetchall()
    course_sections = {}
    for section in sections:
        course_id = section['course_id']
        course = course_sections.get(course_id)
        if course:
            sections = course['sections']
        else:
            sections = []
            units = (section['units_lecture'], section['units_lab'],
                     section['units_homework'])
            course_sections[course_id] = {
                'id': course_id,
                'number': section['number'],
                'name': section['name'],
                'units': tuple(map(try_int, units)),
                'sections': sections
            }
        sections.append({
            'number': section['section_number'],
            'instructor': section['instructor'],
            'grades': section['grades_type'],
            'times': section['times'],
            'locations': section['locations']
        })
    courses = course_sections.values()
    for course in courses:
        course['sections'].sort(key=lambda section: section['number'])
    return sorted(courses, key=lambda course: course['number'].lower())


def add_scheduler_section(username, course, section):
    """
    Adds a certain section number of a certain course
    to a certain user's schedule for the course's term.
    """
    user_id = get_user_id(username)
    query = """
        INSERT INTO scheduler_sections (user_id, course_id, section_number)
        VALUES (%s, %s, %s)
    """
    with flask.g.pymysql_db.cursor() as cursor:
        cursor.execute(query, (user_id, course, section))


def drop_scheduler_section(username, course, section):
    """
    Removes a certain section number of a certain course
    from a certain user's schedule for the course's term.
    """
    user_id = get_user_id(username)
    query = """
        DELETE FROM scheduler_sections
        WHERE user_id = %s AND course_id = %s AND section_number = %s
    """
    with flask.g.pymysql_db.cursor() as cursor:
        cursor.execute(query, (user_id, course, section))


def get_user_scheduler_sections(username, year, term):
    """
    Returns {'id' (course_id), 'section' (section_number)} structs for each
    section on a certain user's schedule for a certain term of a certain year.
    """
    query = """
        SELECT course_id, section_number
        FROM
            users
            NATURAL JOIN scheduler_sections
            NATURAL JOIN courses
        WHERE username = %s AND year = %s AND term = %s
    """
    with flask.g.pymysql_db.cursor() as cursor:
        cursor.execute(query, (username, year, term))
        sections = cursor.fetchall()
    return [{
        'id': section['course_id'],
        'section': section['section_number']
    } for section in sections]

is_duplicate_error = lambda e: \
    isinstance(e, IntegrityError) and e.args[0] == ER.DUP_ENTRY


def get_notes(username, course):
    user_id = get_user_id(username)
    query = "SELECT notes FROM scheduler_notes WHERE user_id=%s AND course_id=%s"
    with flask.g.pymysql_db.cursor() as cursor:
        cursor.execute(query, (user_id, course))
        res = cursor.fetchone()
        if res:
            return res['notes']
        else:
            return None


def edit_notes(username, course, notes):
    if len(notes) == 0:
        delete_notes(username, course)
        return
    user_id = get_user_id(username)
    query = """
    INSERT INTO scheduler_notes (user_id, course_id, notes) VALUES (%s, %s, %s)
    ON DUPLICATE KEY UPDATE notes = VALUES(notes)
    """
    with flask.g.pymysql_db.cursor() as cursor:
        cursor.execute(query, (user_id, course, notes))


def delete_notes(username, course):
    user_id = get_user_id(username)
    query = "DELETE FROM scheduler_notes WHERE user_id=%s AND course_id=%s"
    with flask.g.pymysql_db.cursor() as cursor:
        cursor.execute(query, (user_id, course))
