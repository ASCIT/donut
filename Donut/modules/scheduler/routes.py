import flask

from Donut.modules.scheduler import blueprint, helpers
import pdb

@blueprint.route('/')
def home():
  courses = [
  ]
  course_info = helpers.get_course_info()
  keys = course_info.keys()
  courses_d = course_info.fetchall()
  for course in courses_d:
      course_dict = dict(zip(keys, course))
      course_dict['sections'] = []
      section_info = helpers.get_section_info(course_dict['course_id'])
      cols = section_info.keys()
      sections = section_info.fetchall()
      for section in sections:
          section_d = dict(zip(cols, section))
          section_d['times'] = section_d['times'].replace(';', '<br>')
          course_dict['sections'].append(section_d)
      course_dict['n_sections'] = len(sections)
      courses.append(course_dict)

  pdb.set_trace()
  return flask.render_template('scheduler.html', courses=courses, course_info=course_info)
