import flask
import pymysql

from donut.modules.courses import blueprint, helpers

YEARS = {1: 'Freshman', 2: 'Sophomore', 3: 'Junior', 4: 'Senior'}
WEEK_DAYS = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday']
SCHEDULER_START_HOUR = 8  # 8 AM
SCHEDULER_END_HOUR = 23  # 11 PM
SCHEDULER_HOUR_HEIGHT = 50  # px


@blueprint.route('/planner')
def planner():
    return flask.render_template(
        'planner.html', TERMS=helpers.TERM_NAMES, YEARS=YEARS)


@blueprint.route('/scheduler')
def scheduler():
    return flask.render_template(
        'scheduler.html',
        TERMS=helpers.TERM_NAMES,
        WEEK_DAYS=WEEK_DAYS,
        START_HOUR=SCHEDULER_START_HOUR,
        END_HOUR=SCHEDULER_END_HOUR,
        HOUR_HEIGHT=SCHEDULER_HOUR_HEIGHT,
        terms=helpers.get_terms())


@blueprint.route('/1/planner/courses')
def planner_courses():
    return flask.jsonify(helpers.get_year_courses())


@blueprint.route('/1/planner/course/<int:course_id>/add/<int:year>')
def planner_add_course(course_id, year):
    username = flask.session.get('username')
    if not username:
        return flask.jsonify({
            'success': False,
            'message': 'Must be logged in to save'
        })

    try:
        helpers.add_planner_course(username, course_id, year)
        return flask.jsonify({'success': True})
    except pymysql.err.IntegrityError:
        return flask.jsonify({
            'success': False,
            'message': 'Cannot schedule class twice in a term'
        })


@blueprint.route('/1/planner/course/<int:course_id>/drop/<int:year>')
def planner_drop_course(course_id, year):
    username = flask.session.get('username')
    if not username:
        return flask.jsonify({
            'success': False,
            'message': 'Must be logged in to save'
        })

    helpers.drop_planner_course(username, course_id, year)
    return flask.jsonify({'success': True})


@blueprint.route('/1/planner/courses/mine')
def planner_mine():
    username = flask.session.get('username')
    if not username: return flask.jsonify([])

    return flask.jsonify(helpers.get_user_planner_courses(username))


@blueprint.route('/1/scheduler/courses/<int:term>/<int:year>')
def scheduler_courses(term, year):
    return flask.jsonify(helpers.get_scheduler_courses(term, year))
