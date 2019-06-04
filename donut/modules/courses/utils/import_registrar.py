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

COURSE_MATCH = r'^(?P<dept>[A-Za-z/]+) *0*(?P<number>[0-9]+[A-Z]*)$'

db = make_db('dev')

parser = argparse.ArgumentParser()
parser.add_argument(
    'file',
    help='Path to registrar file, e.g. donut_courses_WI2018-19_181113.txt')
parser.add_argument(
    'year', type=int, help='Year of the term to import (e.g. 2019)')
parser.add_argument('term', choices=TERMS, help='Term to import (e.g. WI)')
args = parser.parse_args()

year = args.year
term = TERMS[args.term]
courses = {}  # map of course numbers to courses data
instructors = set()
grades_types = set()
sections = {}  # map of (course number, section) to section data
with open(args.file) as f:
    tsv_reader = csv.reader(f, delimiter='\t')
    headers = None
    for row in tsv_reader:
        if not headers:
            headers = row
            continue

        row_data = dict(zip(headers, row))
        course = row_data['Course Number']
        if course not in courses:
            try:
                match = re.search(COURSE_MATCH, course)
                dept = match.group('dept')
                number = match.group('number').lower()
                units = row_data['Units']
                if units == '+': units = '0-0-0'
                lecture, lab, homework = map(float, units.split('-'))
                courses[course] = {
                    'department': dept,
                    'course_number': number,
                    'name': row_data['Course Name'],
                    'units_lecture': lecture,
                    'units_lab': lab,
                    'units_homework': homework
                }
            except e:
                print('Error parsing course:', row_data, file=sys.stderr)
                print(e, file=sys.stderr)
        try:
            instructor = row_data['Instructor']
            instructors.add(instructor)
            grades_type = row_data['Grades']
            grades_types.add(grades_type)
            section = int(row_data['Section Number'])
            times = row_data['Times']
            locations = row_data['Locations'].strip()
            section_key = course, section
            section_data = sections.get(section_key)
            if section_data:
                section_data['times'] += '\n' + times
                section_data['locations'] += '\n' + locations
            else:
                sections[section_key] = {
                    'course': course,
                    'section_number': section,
                    'instructor': instructor,
                    'grades_type': grades_type,
                    'times': times,
                    'locations': locations
                }
        except e:
            print('Error parsing section:', row_data, file=sys.stderr)
            print(e, file=sys.stderr)

with db.cursor() as cursor:
    course_ids = {}
    query = """
        INSERT INTO courses (
            year, term,
            department, course_number,
            name,
            units_lecture, units_lab, units_homework
        ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
        ON DUPLICATE KEY UPDATE course_id = course_id
    """
    for number, course in courses.items():
        cursor.execute(
            query, (year, term, course['department'], course['course_number'],
                    course['name'], course['units_lecture'],
                    course['units_lab'], course['units_homework']))
        if cursor.lastrowid:  # 0 if no insert occured
            course_ids[number] = cursor.lastrowid

    def add_possibilities(name, values):
        ids = {}
        for value in values:
            cursor.execute('SELECT ' + name + '_id AS id FROM ' + name +
                           's WHERE ' + name + ' = %s LIMIT 1', value)
            value_id = cursor.fetchone()
            if value_id:
                ids[value] = value_id['id']
            else:
                cursor.execute(
                    'INSERT INTO ' + name + 's (' + name + ') VALUES (%s)',
                    value)
                ids[value] = cursor.lastrowid
        return ids

    instructor_ids = add_possibilities('instructor', instructors)
    grades_types_ids = add_possibilities('grades_type', grades_types)

    query = """
        INSERT INTO sections (
            course_id,
            section_number,
            instructor_id, grades_type_id,
            times, locations
        ) VALUES (
            %s,
            %s,
            %s, %s,
            %s, %s
        ) ON DUPLICATE KEY UPDATE section_number = section_number
    """
    for section in sections.values():
        course_id = course_ids.get(section['course'])
        if not course_id: continue

        cursor.execute(query, (course_id, section['section_number'],
                               instructor_ids[section['instructor']],
                               grades_types_ids[section['grades_type']],
                               section['times'], section['locations']))
