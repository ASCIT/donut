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
