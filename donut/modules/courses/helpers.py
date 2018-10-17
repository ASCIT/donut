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
                    if instructor != matching_course['instructor']:
                        matching_course['instructor'] = None
                else:
                    courses[number] = {
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
