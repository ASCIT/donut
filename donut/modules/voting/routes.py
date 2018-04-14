from datetime import date, datetime, timedelta
import flask

from . import blueprint, helpers


@blueprint.route('/1/surveys')
def list_surveys():
    user_id = helpers.get_user_id(flask.session.get('username'))
    active_surveys = helpers.get_public_surveys(user_id)
    return flask.render_template(
        'list_surveys.html', active_surveys=active_surveys)


@blueprint.route('/1/surveys/<access_key>/take')
def take_survey(access_key):
    survey = helpers.get_survey_data(access_key)
    if not survey:
        flask.flash('Invalid access key')
        return list_surveys()
    now = datetime.now()
    if not (survey['start_time'] <= now <= survey['end_time']):
        flask.flash('Survey is not currently accepting responses')
        return list_surveys()

    questions_json = helpers.get_questions_json(survey['survey_id'])
    return flask.render_template(
        'take.html',
        question_types=helpers.get_question_types(),
        questions_json=questions_json)


@blueprint.route('/1/surveys/make')
def make_survey_form():
    tomorrow = date.today() + timedelta(days=1)
    one_week_later = tomorrow + timedelta(weeks=1)
    return flask.render_template(
        'survey_params.html',
        groups=helpers.get_groups(),
        start_date=tomorrow,
        start_hour=12,
        start_minute='00',
        end_date=one_week_later,
        end_hour=12,
        end_minute='00')


@blueprint.route('/1/survey', methods=['POST'])
def make_survey():
    return helpers.process_params_request()


def restrict_edit(survey):
    if not survey:
        flask.flash('Invalid access key')
        return list_surveys()
    user_id = helpers.get_user_id(flask.session.get('username', ''))
    if user_id != survey['creator']:
        flask.flash('You are not the creator of this survey')
        return list_surveys()
    now = datetime.now()
    if now > survey['end_time']:
        flask.flash('Cannot modify a survey after it has closed')
        return list_surveys()


@blueprint.route('/1/surveys/mine')
def my_surveys():
    if 'username' not in flask.session:
        return flask.render_template('manage.html', logged_in=False)

    user_id = helpers.get_user_id(flask.session['username'])
    my_surveys = helpers.get_my_surveys(user_id)
    return flask.render_template(
        'manage.html', logged_in=True, my_surveys=my_surveys)


@blueprint.route('/1/surveys/<access_key>/questions', methods=['GET'])
def edit_questions(access_key):
    survey = helpers.get_survey_data(access_key)
    restricted = restrict_edit(survey)
    if restricted: return restricted

    questions_json = helpers.get_questions_json(survey['survey_id'])
    return flask.render_template(
        'edit.html',
        question_types=helpers.get_question_types(),
        questions_json=questions_json,
        access_key=access_key,
        survey=survey)


@blueprint.route('/1/surveys/<access_key>', methods=['GET'])
def edit_params(access_key):
    survey = helpers.get_survey_data(access_key)
    restricted = restrict_edit(survey)
    if restricted: return restricted

    survey_params = helpers.get_survey_params(survey['survey_id'])
    start_time = survey_params['start_time']
    end_time = survey_params['end_time']
    return flask.render_template(
        'survey_params.html',
        editing=True,
        access_key=access_key,
        groups=helpers.get_groups(),
        start_date=start_time.strftime(helpers.YYYY_MM_DD),
        start_hour=start_time.strftime('%-I'),
        start_minute=start_time.strftime('%M'),
        start_period='P' if start_time.hour >= 12 else 'A',
        end_date=end_time.strftime(helpers.YYYY_MM_DD),
        end_hour=end_time.strftime('%-I'),
        end_minute=end_time.strftime('%M'),
        end_period='P' if end_time.hour >= 12 else 'A',
        **survey_params)


@blueprint.route('/1/surveys/<access_key>', methods=['POST'])
def save_params(access_key):
    survey = helpers.get_survey_data(access_key)
    restricted = restrict_edit(survey)
    if restricted: return restricted

    return helpers.process_params_request(
        survey['survey_id'], access_key=access_key)


@blueprint.route('/1/surveys/<access_key>/questions', methods=['POST'])
def save_questions(access_key):
    survey = helpers.get_survey_data(access_key)
    restricted = restrict_edit(survey)
    if restricted: return restricted

    questions = flask.request.get_json(force=True)
    helpers.set_questions(survey['survey_id'], questions)
    return flask.jsonify({'success': True})


@blueprint.route('/1/surveys/<access_key>', methods=['DELETE'])
def delete_survey(access_key):
    survey = helpers.get_survey_data(access_key)
    if not survey:
        return flask.jsonify({
            'success': False,
            'message': 'Invalid access key'
        })
    user_id = helpers.get_user_id(flask.session.get('username', ''))
    if user_id != survey['creator']:
        return flask.jsonify({
            'success':
            False,
            'message':
            'You are not the creator of this survey'
        })

    helpers.delete_survey(survey['survey_id'])
    return flask.jsonify({'success': True})
