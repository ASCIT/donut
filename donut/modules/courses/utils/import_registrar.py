#!/usr/bin/env python

# Example command: ./import_registrar.py donut_courses_FA2018-19_180515.txt 2018 FA

import csv
import re
import sys
from donut.pymysql_connection import make_db

TERMS = {'FA': 1, 'WI': 2, 'SP': 3}
COURSE_MATCH = r'^(?P<dept>[A-Za-z/]+) *0*(?P<number>[0-9]+[A-Z]*)$'

db = make_db('dev')

_, filename, year, term = sys.argv
term = TERMS[term]
courses = {}  # map of course numbers to courses data
instructors = set()
grades_types = set()
sections = {}  # map of (course number, section) to section data
with open(filename) as f:
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
            section_key = (course, section)
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
    query = """
        INSERT INTO courses (
            year, term,
            department, course_number,
            name,
            units_lecture, units_lab, units_homework
        ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
        ON DUPLICATE KEY UPDATE course_id = course_id
    """
    for course in courses.values():
        cursor.execute(
            query, (year, term, course['department'], course['course_number'],
                    course['name'], course['units_lecture'],
                    course['units_lab'], course['units_homework']))

    instructor_ids = {}
    for instructor in instructors:
        cursor.execute(
            'SELECT instructor_id FROM instructors WHERE instructor = %s LIMIT 1',
            instructor)
        instructor_id = cursor.fetchone()
        if instructor_id:
            instructor_ids[instructor] = instructor_id['instructor_id']
        else:
            cursor.execute('INSERT INTO instructors (instructor) VALUES (%s)',
                           instructor)
            instructor_ids[instructor] = cursor.lastrowid

    grades_types_ids = {}
    for grades_type in grades_types:
        cursor.execute(
            'SELECT grades_type_id FROM grades_types WHERE grades_type = %s',
            grades_type)
        grades_type_id = cursor.fetchone()
        if grades_type_id:
            grades_types_ids[grades_type] = grades_type_id['grades_type_id']
        else:
            cursor.execute(
                'INSERT INTO grades_types (grades_type) VALUES (%s)',
                grades_type)
            grades_types_ids[grades_type] = cursor.lastrowid

    query = """
        INSERT INTO sections (
            course_id,
            section_number,
            instructor_id, grades_type_id,
            times, locations
        ) VALUES (
            (SELECT course_id FROM courses WHERE year = %s AND term = %s AND department = %s AND course_number = %s LIMIT 1),
            %s,
            %s, %s,
            %s, %s
        ) ON DUPLICATE KEY UPDATE section_id = section_id
    """
    for section in sections.values():
        course = courses[section['course']]
        cursor.execute(
            query,
            (year, term, course['department'], course['course_number'],
             section['section_number'], instructor_ids[section['instructor']],
             grades_types_ids[section['grades_type']], section['times'],
             section['locations']))
