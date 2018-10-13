import flask

from donut.modules.courses import blueprint, helpers


@blueprint.route('/planner')
def planner():
    return flask.render_template('planner.html')


@blueprint.route('/scheduler')
def scheduler():
    return flask.render_template(
        'scheduler.html', TERMS=helpers.TERM_NAMES, terms=helpers.get_terms())
