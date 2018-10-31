import flask

from donut.modules.courses import blueprint, helpers

YEARS = {1: 'Freshman', 2: 'Sophomore', 3: 'Junior', 4: 'Senior'}


@blueprint.route('/planner')
def planner():
    return flask.render_template(
        'planner.html', TERMS=helpers.TERM_NAMES, YEARS=YEARS)


@blueprint.route('/scheduler')
def scheduler():
    return flask.render_template(
        'scheduler.html', TERMS=helpers.TERM_NAMES, terms=helpers.get_terms())


@blueprint.route('/1/planner/courses')
def planner_courses():
    return flask.jsonify(helpers.get_year_courses())


@blueprint.route('/1/planner/course/<int:course_id>/add/<int:year>')
def planner_add_course(course_id, year):
    username = flask.session.get('username')
    if not username:
        return flask.jsonify({
            'success': False,
            'message': 'Must be logged in'
        })

    helpers.add_planner_course(username, course_id, year)
    return flask.jsonify({'success': True})


@blueprint.route('/1/planner/courses/mine')
def planner_mine():
    username = flask.session.get('username')
    if not username: return flask.jsonify([])

    return flask.jsonify(helpers.get_user_planner_courses(username))
