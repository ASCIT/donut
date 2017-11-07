
# Revision history:
#   8-24-2014: New file to parse schedule in tsv format obtained
#              from registrar - Rahul Bachal

import urllib
import re
import pickle
from HTMLParser import HTMLParser
import os
import sys
from parserDefinitions import Department, Course, Section

# Parses the course schedule file in tsv format from
# the registar

f = open('departments.txt')

lines = f.readlines()

f.close()

departments = {}

for line in lines:
    departmentData = line.split('(')
    departmentName = departmentData[0].strip(' )\n')
    departmentAbbr = departmentData[1].strip(' )\n')
    
    departments[departmentAbbr] = Department(departmentAbbr, departmentName)



f = open(sys.argv[1], 'rU')

lines = f.readlines()

f.close()


section = None
course = None
courses = []
sections = []

for i in range(1, len(lines)):
    courseData = lines[i].split("\t")
    courseData[-1] = courseData[-1].strip('"\n')

    for j in xrange(0, len(courseData)):
        courseData[j] = courseData[j].strip(' "')
    
    if course is None or course.key != courseData[0]:
        if course != None:
            course.sections += [section]
            sections += [section]
            departments[course.primaryDepartment].courses += [course]
            courses += [course]
            
        course = Course()
        course.name = courseData[1]
        course.title = courseData[1]
        course.primaryDepartment = courseData[2]
        course.units = courseData[5]
        course.key = courseData[0]

        courseNumber = course.key.split()

        if len(courseNumber) != 2:
            r = re.compile("([a-zA-Z]+)([0-9A-Z]+)")
            m = r.match(course.key)
            course.department = m.group(1)
            course.number = m.group(2)
        else:
            course.department = courseNumber[0]
            course.number = courseNumber[1]
        
        section = None

    if section is None or section.number != courseData[6]:        
        if section != None:
            course.sections += [section]
            sections += [section]

        section = Section()
        section.number = courseData[6]
        section.instructor = courseData[3]
        section.times += [courseData[7]]
        section.locations += [courseData[8]]
        section.grades = courseData[4]
        section.courseNumber = courseData[0]    
    else:
        section.times += [courseData[7]]
        section.locations += [courseData[8]]

course.sections += [section]
sections += [section]
departments[course.department].courses += [course]
courses += [course]

f = open('courses.bin', 'wb')
pickle.dump((departments, courses), f)
f.close()
