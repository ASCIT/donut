class Department:
    def __init__(self, abbreviation, name):
        self.abbreviation = abbreviation
        self.name = name
        self.courses = []

    def __repr__(self):
        return self.abbreviation + ' ' + self.name

class Section:
    def __init__(self):
        self.number = 0
        self.instructor = ''
        self.times = []
        self.locations = []
        self.grades = ''
        self.courseNumber = ''

    def __repr__(self):
        return self.courseNumber + ' ' + self.number

class Course:
    def __init__(self):
        self.name = ''
        self.title = ''
        self.units = ''
        self.description = ''
        self.sections = []
        self.primaryDepartment = ''
        self.key = ''

    def __repr__(self):
        return self.department + ' ' + self.number


