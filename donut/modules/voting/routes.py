import flask

from . import blueprint, helpers


@blueprint.route('/1/surveys')
def list_surveys():
    return flask.render_template('list_surveys.html')


@blueprint.route('/1/surveys/<access_key>/take')
def take_survey(access_key):
    survey_id = helpers.get_survey_id(access_key)
    if not survey_id:
        flask.flash('Invalid access key or survey has closed')
        return list_surveys()
    questions_json = helpers.get_questions_json(survey_id)
    return flask.render_template('take.html', questions_json=questions_json)
