import pickle
from parserDefinitions import Department, Course, Section
import urllib
import re
import subprocess
import os.path

baseUrl = "http://catalog.caltech.edu/courses/listing/"

# removes tags and line breaks
def cleanDescription(description):
    findEnters = re.split("\\n", description)
    newDesc = ''.join(findEnters)
    findTags = re.split("<.*?>", newDesc)
    newDesc = ''.join(findTags)
    return newDesc

def updateCourse(name, description, listOfCourses, department):
    # find name in course
    extractedName = re.split("\. *", name)
    nameOfCourse = ''
    try:
        nameOfCourse = extractedName[1]
    except IndexError:
        print "No name of course found"
    extractedName = extractedName[0]
    extractedName = ''.join(re.split(" +", extractedName)).lower()
    # for courses with ab/abc:
    checkABC = re.split("a[bc]+$", extractedName)
    if len(checkABC) > 1:
        extractedName = checkABC[0] + "a"
    # for courses with multiple departments, only include description
    # of the course from the correct department
    if not extractedName[0:len(department.abbreviation)] == (department.abbreviation).lower():
        print extractedName + " found in " + department.abbreviation + " but ignored"
        return None
    for course in listOfCourses:
        # remove leading 0s:
        courseName = ''.join(re.split("([a-zA-z])0+", course.__repr__()))
        courseName = ''.join(re.split(" 0+", courseName.lower()))
        courseName = ''.join(re.split(" +", courseName))
        courseName = re.split("\.", courseName)[0]
        if courseName == extractedName: # or len(re.split("(?:^|/)" + courseName + "(?:$|/)", extractedName)) > 1:
            if course.title == '':
                course.title = nameOfCourse
            elif course.title != nameOfCourse:
                print "course " + course.__repr__() + " already had title:"
                print "\t " + course.title
                print " but has another:"
                print "\t " + nameOfCourse
            if course.description == '':
                course.description = description
                # print course
                if course.description == '':
                    print course.__repr__() + " error"
                    print description
            elif course.description != description:
                print "Course " + course.__repr__() + " previously had description:"
                print "\t" + course.description
                print "but another as:"
                print "\t" + description
                return None


def getDesc(department, listOfCourses):
    if not os.path.exists((department.abbreviation).lower() + ".html"):
        subprocess.call(["wget", "-q", "-O", (department.abbreviation).lower() + ".html", \
            baseUrl + (department.abbreviation).lower() + ".html"])
    f = open((department.abbreviation).lower() + ".html")
    # find course name and number
    # it could be better to use HTMLParser, but this should work
    # list of all descriptions
    reformattedF = ''.join(re.split("<span +class=\"text83\"> *</span>", f.read())) # first get rid of useless <span></span> tags
    courseDescs = re.split("<p +class=\"course\">", reformattedF)
    for i in xrange(1,len(courseDescs)):
        # find course in courses, then update description
        try:
            title = re.split("<span +class=\"text84\">", courseDescs[i])[1]
        except IndexError:
            print "<p class=\"course\"> found, but no title:"
            print courseDescs[i][:100]
            continue
        # remove end of title
        title = re.split("</span>", title)[0]
        desc = re.split("<span +class=\"text83\">", courseDescs[i])
        if len(desc) == 1:
            print "could not find <span class=\"text83\">"
            print "\t" + desc[0]
        else:
            desc = re.split("</p>", ''.join(desc[1:len(desc)]))
            updateCourse(title, cleanDescription(''.join(desc[0:(len(desc)-1)])), listOfCourses, department)

# time array is a list of times
# with the format day, start time, end time]
# this converts the list into a dictionary of times
# with each key being the days of the week
# and the next two values being start and end times
def convertTimes(timeArray):
    time_dict = {'M':[], 'T':[], 'W':[], 'R':[], 'F':[]}
    for time in timeArray:
        time_dict[time[0]] = [time[1], time[2]]
    return time_dict


if __name__ == '__main__':
    f = open('courses.bin')
    departments, courses = pickle.load(f)
    f.close()

    # clean up duplicates in course list
    removeArray = []
    for index in range(len(courses)):
        for i in range(index):
            if courses[index].__repr__() == courses[i].__repr__() and not index == i:
                removeArray.append(index)
    removeArray = list(set(removeArray))
    removeArray.sort(reverse=True)
    for i in removeArray:
        courses.pop(i)
    for depart in departments:
        getDesc(departments[depart], courses)

    count = 0
    for course in courses:
        if course.description == '':
            print course
            count += 1
    print str(count) + " missing out of " + str(len(courses))
    newfile = open("courses-with-descriptions.bin", "wb")
    pickle.dump((departments, courses), newfile)
    newfile.close()
    #
    # writing courses out to sql file
    #
    sqlFile = open("insert_courses.sql", "w")

    sqlFile.write("CREATE TEMP TABLE tempCourses (department VARCHAR(30) NOT NULL, course_no VARCHAR(10) NOT NULL, section_no VARCHAR(3) NOT NULL, name VARCHAR(150) NOT NULL, instructor VARCHAR(60), times VARCHAR(100), locations VARCHAR(100), grades VARCHAR(25), units VARCHAR(10) NOT NULL, description TEXT, UNIQUE (department, course_no, section_no) );\n")
    sqlFile.write("INSERT INTO tempCourses VALUES\n")
    
    section_id = 1
    
    for i in xrange(len(courses)):
        for j in xrange(len(courses[i].sections)):
            section = courses[i].sections[j]
            sqlFile.write("\t('%s', '%s', '%s', '%s', '%s', '%s', '%s', '%s', '%s', '%s')" %
                (courses[i].department, 
                 courses[i].number,
                 section.number,
                 courses[i].title.replace("'", "''"),
                 section.instructor.replace("'", "''"),
                 ';'.join(section.times),
                 ';'.join(section.locations),
                 section.grades,
                 courses[i].units,
                 courses[i].description.replace("'", "''")))

            if i != len(courses)-1 or j != len(courses[i].sections)-1:
                sqlFile.write(',\n')
            else:
                sqlFile.write(';\n\n')

            section_id += 1
    
    sqlFile.write("-- Delete old courses and sections that are not in new courses\n\n")

    # Create temporary view to join courses and sections
    sqlFile.write("CREATE VIEW old_courses_intersect AS \n\
    SELECT scheduler.courses.course_id, scheduler.courses.department, scheduler.courses.course_no, scheduler.courses.name, scheduler.courses.description, scheduler.courses.units, scheduler.course_sections.section_id, scheduler.course_sections.section_no, scheduler.course_sections.instructor, scheduler.course_sections.times, scheduler.course_sections.locations, scheduler.course_sections.grades \n\
    FROM scheduler.courses NATURAL JOIN scheduler.course_sections;\n\n")

    # Delete sections that are not in new courses
    sqlFile.write("DELETE FROM scheduler.course_sections \n\
    WHERE section_id IN \n\t\
    (SELECT section_id \n\t\
    FROM old_courses_intersect \n\t\
    WHERE NOT EXISTS \n\t\t\
    (SELECT 1 FROM tempCourses \n\t\t\
    WHERE tempCourses.course_no = old_courses_intersect.course_no \n\t\t\
    AND tempCourses.department = old_courses_intersect.department \n\t\t\
    AND tempCourses.section_no = old_courses_intersect.section_no) );\n\n")

    # Delete courses that are not in new courses
    sqlFile.write("DELETE FROM scheduler.courses \n\
    WHERE NOT EXISTS \n\t\
    (SELECT 1 FROM tempCourses \n\t\
    WHERE tempCourses.course_no = scheduler.courses.course_no \n\t\
    AND tempCourses.department = scheduler.courses.department);\n\n")
    
    sqlFile.write("-- Insert new courses and sections that are not in old courses\n\n")

    # Insert new courses
    sqlFile.write("INSERT INTO scheduler.courses (department, course_no, name, description, units) \n\
    SELECT DISTINCT department, course_no, name, description, units \n\
    FROM tempCourses WHERE NOT EXISTS \n\t\
    (SELECT 1 FROM scheduler.courses \n\t\
    WHERE tempCourses.course_no = scheduler.courses.course_no \n\t\
    AND tempCourses.department = scheduler.courses.department);\n\n")

    # Insert new sections
    sqlFile.write("INSERT INTO scheduler.course_sections (course_id, section_no, instructor, times, locations, grades) \n\
    SELECT scheduler.courses.course_id, tempCourses.section_no, tempCourses.instructor, tempCourses.times, tempCourses.locations, tempCourses.grades \n\
    FROM tempCourses LEFT OUTER JOIN old_courses_intersect \n\
    ON tempCourses.department = old_courses_intersect.department \n\
    AND tempCourses.course_no = old_courses_intersect.course_no \n\
    AND tempCourses.section_no = old_courses_intersect.section_no INNER JOIN scheduler.courses \n\
    ON tempCourses.course_no = scheduler.courses.course_no \n\
    AND tempCourses.department = scheduler.courses.department \n\
    WHERE old_courses_intersect.course_id IS NULL;\n\n")
    
    sqlFile.write("-- Update courses and sections\n\n")

    # Update sections with new data
    sqlFile.write("UPDATE scheduler.course_sections \n\
    SET instructor = tempCourses.instructor, times = tempCourses.times, locations = tempCourses.locations, grades = tempCourses.grades \n\
    FROM tempCourses, old_courses_intersect \n\
    WHERE tempCourses.course_no = old_courses_intersect.course_no \n\
    AND tempCourses.department = old_courses_intersect.department \n\
    AND tempCourses.section_no = scheduler.course_sections.section_no \n\
    AND old_courses_intersect.course_id = scheduler.course_sections.course_id;\n\n")

    # Update courses with new data
    sqlFile.write("UPDATE scheduler.courses \n\
    SET name = tempCourses.name, description = tempCourses.description, units = tempCourses.units \n\
    FROM tempCourses \n\
    WHERE tempCourses.department = scheduler.courses.department \n\
    AND tempCourses.course_no = scheduler.courses.course_no;\n\n")

    # Drop temporary view
    sqlFile.write("DROP VIEW old_courses_intersect;")

    sqlFile.close()
    # readSQL = open('insert_courses.sql', 'r')
    # writeString = readSQL.read()
    # writeString = 'NULL'.join(re.split("\'\'", readSQL.read()))
    # writeString2 = '('.join(re.split("\(0", writeString))
    # readSQL.close()
    # newSQL = open('insert_courses_actual.sql', 'w')
    # newSQL.write(writeString)
    # newSQL.close()
