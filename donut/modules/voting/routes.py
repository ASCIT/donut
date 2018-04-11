from datetime import date, datetime, timedelta
import flask

from . import blueprint, helpers
from donut.validation_utils import (validate_date, validate_exists,
                                    validate_in, validate_int)

AM_OR_PM = set(['A', 'P'])
YYYY_MM_DD = '%Y-%m-%d'


@blueprint.route('/1/surveys')
def list_surveys():
    return flask.render_template('list_surveys.html')


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
    form = flask.request.form

    def creation_error(message):
        flask.flash(message)
        return flask.render_template(
            'survey_params.html',
            groups=helpers.get_groups(),
            title=form.get('title'),
            description=form.get('description'),
            start_date=form.get('start_date'),
            start_hour=form.get('start_hour'),
            start_minute=form.get('start_minute'),
            start_period=form.get('start_period'),
            end_date=form.get('end_date'),
            end_hour=form.get('end_hour'),
            end_minute=form.get('end_minute'),
            end_period=form.get('end_period'),
            auth='auth' in form,
            public='public' in form,
            group_id=form.get('group'))

    if 'username' not in flask.session:
        return creation_error('Not logged in')

    validations = [
        validate_exists(form, 'title'),
        validate_exists(form, 'description'),
        validate_exists(form, 'start_date')
        and validate_date(form['start_date']),
        validate_exists(form, 'start_hour')
        and validate_int(form['start_hour'], 1, 12),
        validate_exists(form, 'start_minute')
        and validate_int(form['start_minute'], 0, 59),
        validate_exists(form, 'start_period')
        and validate_in(form['start_period'], AM_OR_PM),
        validate_exists(form, 'end_date') and validate_date(form['end_date']),
        validate_exists(form, 'end_hour')
        and validate_int(form['end_hour'], 1, 12),
        validate_exists(form, 'end_minute')
        and validate_int(form['end_minute'], 0, 59),
        validate_exists(form, 'end_period')
        and validate_in(form['end_period'], AM_OR_PM),
        validate_exists(form, 'group')
        and (not form['group'] or validate_int(form['group']))
    ]
    if not all(validations):
        #Should only happen if a malicious request is sent,
        #so error message is not important
        return creation_error('Invalid form data')

    start_day = datetime.strptime(form['start_date'], YYYY_MM_DD)
    start_hour = int(form['start_hour']) % 12
    if form['start_period'] == 'P': start_hour += 12
    start_minute = int(form['start_minute'])
    start = datetime(start_day.year, start_day.month, start_day.day,
                     start_hour, start_minute)
    end_day = datetime.strptime(form['end_date'], YYYY_MM_DD)
    end_hour = int(form['end_hour']) % 12
    if form['end_period'] == 'P': end_hour += 12
    end_minute = int(form['end_minute'])
    end = datetime(end_day.year, end_day.month, end_day.day, end_hour,
                   end_minute)
    if start >= end:
        return creation_error('Start must be before end')

    group = form['group']
    group = int(group) if group else None

    access_key = helpers.make_survey(
        username=flask.session['username'],
        title=form['title'].strip(),
        description=form['description'].strip() or None,
        start=start,
        end=end,
        auth='auth' in form,
        public='public' in form,
        group_id=group)
    return flask.redirect(
        flask.url_for('voting.edit_questions', access_key=access_key))


@blueprint.route('/1/surveys/<access_key>/questions', methods=['GET'])
def edit_questions(access_key):
    survey = helpers.get_survey_data(access_key)
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

    questions_json = helpers.get_questions_json(survey['survey_id'])
    return flask.render_template(
        'edit.html',
        question_types=helpers.get_question_types(),
        questions_json=questions_json)
