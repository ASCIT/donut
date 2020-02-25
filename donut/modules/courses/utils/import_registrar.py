#!/usr/bin/env python
"""
Imports the Registrar's Office's exports of courses for a given term.
Never removes courses/sections and will not overwrite existing ones.
Expects file to be a TSV value with the following columns:
"Course Number"
"Course Name"
"Department"
"Instructor"
"Grades"
"Units"
"Section Number"
"Times"
"Locations"

Example row:
"CS 001"	"Introduction to Computer Programming"	"CS"	"Vanier, M"	"PASS-FAIL"	"3-4-2"	"01"	"MWF 14:00 - 14:55"	"Institute Auditorium BCK"

Note that there is a separate row for each time of each section of each course.
The insertion into our database is straightforward, with a few exceptions:
- We separate the course number into department and number
- Leading zeros are removed from the course number and it is lowercased
- If the units value is "+", we change it to "0-0-0"
- Units are split into lecture, lab, and homework units
  (note we use float since some courses have fractional units)
- Remove whitespace from locations (IDK why some are " YHC")
- Append locations and times from separate rows for the same section
- Make lists of all grades types (e.g. "PASS-FAIL") and instructors
  (e.g. "Vanier, M") and add to grades_types and instructors tables
"""

import argparse
import csv
import re
import sys
from donut.pymysql_connection import make_db
from donut.modules.courses.helpers import TERMS

COURSE_MATCH = r'(?P<dept>[A-Za-z/]+) *0*(?P<number>[0-9]+[A-Z]*)'


def parse_file(file, courses, sections, instructors, grades_types):
    with open(file) as f:
        for row in csv.DictReader(f, delimiter='\t'):
            try:
                course = row['Course Number']
                course_sections = sections.setdefault(course, {})
                if not course_sections:
                    course_match = re.fullmatch(COURSE_MATCH, course)
                    if course_match is None:
                        raise Exception('Failed to parse course number')
                    units = row['Units']
                    if units == '+':
                        units = '0-0-0'
                    lecture, lab, homework = map(float, units.split('-'))
                    courses[course] = {
                        'department': course_match.group('dept'),
                        'course_number': course_match.group('number').lower(),
                        'name': row['Course Name'],
                        'units_lecture': lecture,
                        'units_lab': lab,
                        'units_homework': homework
                    }

                instructor = row['Instructor']
                instructors.add(instructor)
                grades_type = row['Grades']
                grades_types.add(grades_type)
                section = int(row['Section Number'])
                times = row['Times']
                locations = row['Locations'].strip()
                section_data = course_sections.get(section)
                if section_data:
                    if instructor != section_data['instructor']:
                        raise Exception('Section instructor changed')
                    if grades_type != section_data['grades_type']:
                        raise Exception('Grades type changed')

                    section_data['times'] += '\n' + times
                    section_data['locations'] += '\n' + locations
                else:
                    course_sections[section] = {
                        'course': course,
                        'section_number': section,
                        'instructor': instructor,
                        'grades_type': grades_type,
                        'times': times,
                        'locations': locations
                    }
            except e:
                print('Error parsing row:', row, file=sys.stderr)
                print(e, file=sys.stderr)
                raise e


def add_courses(year, term, courses, cursor):
    insert_course_query = """
        INSERT INTO courses (
            year, term,
            department, course_number,
            name,
            units_lecture, units_lab, units_homework
        ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
        ON DUPLICATE KEY UPDATE
            name = VALUES(name),
            units_lecture = VALUES(units_lecture),
            units_lab = VALUES(units_lab),
            units_homework = VALUES(units_homework)
    """
    get_course_query = """
        SELECT course_id FROM courses
        WHERE year = %s AND term = %s AND department = %s AND course_number = %s
    """
    course_ids = {}
    for number, course in courses.items():
        course_key = year, term, course['department'], course['course_number']
        cursor.execute(insert_course_query, course_key +
                       (course['name'], course['units_lecture'],
                        course['units_lab'], course['units_homework']))
        course_id = cursor.lastrowid
        if course_id:
            course_ids[number] = course_id
            print('New course:', number)
        else:
            cursor.execute(get_course_query, course_key)
            course_ids[number] = cursor.fetchone()['course_id']
            print('Updated course:', number)
    return course_ids


def add_possibilities(name, values, cursor):
    get_query = 'SELECT ' + name + '_id AS id FROM ' + name + 's WHERE ' + name + ' = %s'
    add_query = 'INSERT INTO ' + name + 's (' + name + ') VALUES (%s)'
    ids = {}
    for value in values:
        cursor.execute(get_query, value)
        value_id = cursor.fetchone()
        if value_id:
            ids[value] = value_id['id']
        else:
            cursor.execute(add_query, value)
            ids[value] = cursor.lastrowid
    return ids


def add_sections(sections, course_ids, instructors, grades_types, cursor):
    query = """
        INSERT INTO sections (
            course_id, section_number,
            instructor_id, grades_type_id,
            times, locations
        ) VALUES (
            %s, %s,
            %s, %s,
            %s, %s
        ) ON DUPLICATE KEY UPDATE
            instructor_id = VALUES(instructor_id),
            grades_type_id = VALUES(grades_type_id),
            times = VALUES(times),
            locations = VALUES(locations)
    """
    for course_sections in sections.values():
        for section in course_sections.values():
            cursor.execute(query, (course_ids[section['course']],
                                   section['section_number'],
                                   instructors[section['instructor']],
                                   grades_types[section['grades_type']],
                                   section['times'], section['locations']))


def remove_courses(year, term, course_ids, cursor):
    query = 'DELETE FROM courses WHERE year = %s AND term = %s'
    params = (year, term)
    if course_ids:
        query += ' AND course_id NOT IN (' + ', '.join(
            '%s' for course in course_ids) + ')'
        params += tuple(course_ids.values())
    cursor.execute(query, params)
    removed = cursor.rowcount
    if removed:
        print('Removed', removed, 'course' + ('s' if removed > 1 else ''))


def remove_sections(course_ids, sections, cursor):
    removed = 0
    for course, course_sections in sections.items():
        query = """DELETE FROM sections WHERE course_id = %s
            AND section_number NOT IN (""" + \
            ', '.join('%s' for section in course_sections) + ')'
        cursor.execute(query, (course_ids[course], ) + tuple(course_sections))
        removed += cursor.rowcount
    if removed:
        print('Removed', removed, 'section' + ('s' if removed > 1 else ''))


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument(
        '-e', '--env', default='dev', help='Database to update (default dev)')
    parser.add_argument(
        'file',
        help='Path to registrar file, e.g. donut_courses_WI2018-19_181113.txt')
    parser.add_argument(
        'year', type=int, help='Year of the term to import (e.g. 2019)')
    parser.add_argument('term', choices=TERMS, help='Term to import (e.g. WI)')
    args = parser.parse_args()

    courses = {}  # map of course numbers to courses data
    sections = {}  # map of course numbers to section numbers to section data
    instructors = set()
    grades_types = set()
    parse_file(args.file, courses, sections, instructors, grades_types)

    db = make_db(args.env)
    year = args.year
    term = TERMS[args.term]
    try:
        db.begin()
        with db.cursor() as cursor:
            course_ids = add_courses(year, term, courses, cursor)
            instructors = add_possibilities('instructor', instructors, cursor)
            grades_types = add_possibilities('grades_type', grades_types,
                                             cursor)
            add_sections(sections, course_ids, instructors, grades_types,
                         cursor)
            remove_courses(year, term, course_ids, cursor)
            remove_sections(course_ids, sections, cursor)
        db.commit()
    finally:
        db.close()
