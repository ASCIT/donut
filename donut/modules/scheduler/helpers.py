import flask
import sqlalchemy


def get_course_info(course_id=None):
    if (course_id is None):
        query = sqlalchemy.text("""
        SELECT * FROM courses
        """)
        result = flask.g.db.execute(query)
        return result
    else:
        query = sqlalchemy.text("""
        SELECT * FROM courses
            WHERE course_id = :course_id
        """)
        result = flask.g.db.execute(query, course_id=course_id)

        return result

def get_section_info(course_id):
    query = sqlalchemy.text("""
    SELECT * FROM course_sections
        WHERE course_id = :course_id
    """)
    result = flask.g.db.execute(query, course_id=course_id)
    return result
