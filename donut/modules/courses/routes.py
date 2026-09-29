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


@blueprint.route('/now')
def now():
    # Rendered statically with no database access; the client fetches
    # pre-filtered rows from now_courses() exactly once. This keeps page
    # views cheap.
    return flask.render_template('now.html')


@blueprint.route('/1/now')
def now_courses():
    data = helpers.get_now_rows()
    if data['year'] is None:
        response = flask.jsonify({
            'year': None,
            'term': None,
            'term_label': 'No terms available',
            'rows': []
        })
    else:
        response = flask.jsonify({
            'year':
            data['year'],
            'term':
            data['term'],
            'term_label':
            '{} {}'.format(
                helpers.TERM_NAMES.get(data['term'], ''), data['year']),
            'rows':
            data['rows']
        })
    # The filtered result depends on the current time, so it must not be
    # cached by browsers/CDNs. The underlying schedule query is cached
    # server-side instead (see helpers.get_cached_scheduler_courses).
    response.headers['Cache-Control'] = 'no-store'
    return response


@blueprint.route('/1/campus_events')
def campus_events():
    # Fail-soft: feed outages still return 200 with an empty list. Grouping
    # depends on the current time, so this response is not browser-cached;
    # the upstream feeds are cached server-side instead.
    response = flask.jsonify({'rows': helpers.get_event_rows()})
    response.headers['Cache-Control'] = 'no-store'
    return response


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
    except Exception as e:
        if helpers.is_duplicate_error(e):
            flask.current_app.logger.warning(f'Duplicate planner entry: {e}')
            return flask.jsonify({
                'success':
                False,
                'message':
                'Cannot add a class twice in the same term'
            })
        else:
            raise e
    return flask.jsonify({'success': True})


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


@blueprint.route('/1/planner/<int:year>/<int:term>/placeholder', \
    methods=('POST', ))
def planner_add_placeholder(year, term):
    username = flask.session.get('username')
    if not username:
        return flask.jsonify({
            'success': False,
            'message': 'Must be logged in to save'
        })
    form = flask.request.form
    course = form.get('course')
    units = form.get('units')
    if not (course and units):
        return flask.jsonify({
            'success': False,
            'message': 'Missing course or units'
        })
    try:
        units = float(units)
    except ValueError:
        return flask.jsonify({
            'success': False,
            'message': 'Invalid number of units'
        })

    placeholder_id = \
        helpers.add_planner_placeholder(username, year, term, course, units)
    return flask.jsonify({'success': True, 'id': placeholder_id})


@blueprint.route('/1/planner/placeholder/<int:id>', methods=('DELETE', ))
def planner_drop_placeholder(id):
    username = flask.session.get('username')
    if not username:
        return flask.jsonify({
            'success': False,
            'message': 'Must be logged in to save'
        })
    if not helpers.drop_planner_placeholder(username, id):
        return flask.jsonify({
            'success': False,
            'message': 'Invalid placeholder'
        })

    return flask.jsonify({'success': True})


@blueprint.route('/1/planner/courses/mine')
def planner_mine():
    username = flask.session.get('username')
    if username:
        courses = helpers.get_user_planner_courses(username)
        placeholders = helpers.get_user_planner_placeholders(username)
    else:
        courses = ()
        placeholders = ()
    return flask.jsonify({'courses': courses, 'placeholders': placeholders})


@blueprint.route('/1/scheduler/courses/<int:year>/<int:term>')
def scheduler_courses(year, term):
    return flask.jsonify(helpers.get_scheduler_courses(year, term))


@blueprint.route('/1/scheduler/course/<int:course>/section/<int:section>/add')
def scheduler_add_section(course, section):
    username = flask.session.get('username')
    if not username:
        return flask.jsonify({
            'success': False,
            'message': 'Must be logged in to save'
        })

    try:
        helpers.add_scheduler_section(username, course, section)
    except Exception as e:
        if helpers.is_duplicate_error(e):
            flask.current_app.logger.warning(f'Duplicate scheduler entry: {e}')
            return flask.jsonify({
                'success': False,
                'message': 'Cannot add a section twice'
            })
        else:
            raise e
    return flask.jsonify({'success': True})


@blueprint.route('/1/scheduler/course/<int:course>/section/<int:section>/drop')
def scheduler_drop_section(course, section):
    username = flask.session.get('username')
    if not username:
        return flask.jsonify({
            'success': False,
            'message': 'Must be logged in to save'
        })

    helpers.drop_scheduler_section(username, course, section)
    return flask.jsonify({'success': True})


@blueprint.route('/1/scheduler/sections/<int:year>/<int:term>/mine')
def scheduler_mine(year, term):
    username = flask.session.get('username')
    if not username: return flask.jsonify(())

    return flask.jsonify(
        helpers.get_user_scheduler_sections(username, year, term))


@blueprint.route('/1/scheduler/edit_notes', methods=['POST'])
def edit_notes():
    username = flask.session.get('username')
    if not username:
        return flask.jsonify({
            'success': False,
            'message': 'Must be logged in to save'
        })

    data = flask.request.get_json(force=True)
    course = data.get('course')
    section = data.get('section')
    notes = data.get('notes')
    if notes:
        helpers.edit_notes(username, course, section, notes)
    else:
        helpers.delete_notes(username, course, section)
    return flask.jsonify({'success': True})


@blueprint.route('/1/scheduler/notes/<int:course>/section/<int:section>')
def get_notes(course, section):
    username = flask.session.get('username')
    if not username: return flask.jsonify(None)

    return flask.jsonify(helpers.get_notes(username, course, section))
