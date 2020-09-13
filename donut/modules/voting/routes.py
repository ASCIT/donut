from datetime import date, datetime
import json
import flask

from . import blueprint, helpers
from .permissions import Permissions
from donut.auth_utils import check_permission
from donut.modules.core.helpers import get_member_data


@blueprint.route('/1/surveys')
def list_surveys():
    username = flask.session.get('username')
    user_id = helpers.get_user_id(username)
    has_surveys_perm = check_permission(username, Permissions.SURVEYS)
    active_surveys = helpers.get_visible_surveys(user_id)
    closed_surveys = helpers.get_closed_surveys(user_id)
    return flask.render_template(
        'list_surveys.html',
        has_surveys_perm=has_surveys_perm,
        active_surveys=active_surveys,
        closed_surveys=closed_surveys)


@blueprint.route('/1/surveys/<access_key>/take')
def take_survey(access_key):
    survey = helpers.get_survey_data(access_key)
    restrict_message = helpers.restrict_take_access(survey)
    if restrict_message:
        if restrict_message == helpers.ALREADY_COMPLETED:
            return flask.redirect(
                flask.url_for(
                    'voting.show_my_response', access_key=access_key))
        else:
            flask.flash(restrict_message)
            return list_surveys()

    questions_json = helpers.get_questions_json(survey['survey_id'], True)
    user_id = helpers.get_user_id(flask.session['username'])
    is_owner = survey['creator'] == user_id
    return flask.render_template(
        'take.html',
        access_key=access_key,
        **survey,
        is_owner=is_owner,
        NO=helpers.NO,
        question_types=helpers.get_question_types(),
        questions_json=questions_json)


@blueprint.route('/1/surveys/make')
def make_survey_form():
    if not check_permission(
            flask.session.get('username'), Permissions.SURVEYS):
        flask.abort(403)

    return flask.render_template(
        'survey_params.html', groups=helpers.get_groups())


@blueprint.route('/1/survey', methods=['POST'])
def make_survey():
    return helpers.process_params_request(False)


@blueprint.route('/1/surveys/mine')
def my_surveys():
    if 'username' not in flask.session:
        return flask.render_template('manage.html', logged_in=False)
    if not check_permission(flask.session['username'], Permissions.SURVEYS):
        flask.abort(403)

    user_id = helpers.get_user_id(flask.session['username'])
    my_surveys = helpers.get_my_surveys(user_id)
    return flask.render_template(
        'manage.html', logged_in=True, my_surveys=my_surveys)


@blueprint.route('/1/surveys/<access_key>/questions', methods=['GET'])
def edit_questions(access_key):
    survey = helpers.get_survey_data(access_key)
    restrict_message = helpers.restrict_edit_access(survey, False)
    if restrict_message:
        flask.flash(restrict_message)
        return list_surveys()

    survey_id = survey['survey_id']
    questions_json = helpers.get_questions_json(survey_id, False)
    return flask.render_template(
        'edit.html',
        question_types=helpers.get_question_types(),
        questions_json=questions_json,
        access_key=access_key,
        survey=survey,
        opened=survey['start_time'] <= datetime.now(),
        some_responses=helpers.some_responses_for_survey(survey_id),
        NO=helpers.NO)


@blueprint.route('/1/surveys/<access_key>', methods=['GET'])
def edit_params(access_key):
    survey = helpers.get_survey_data(access_key)
    restrict_message = helpers.restrict_edit_access(survey, False)
    if restrict_message:
        flask.flash(restrict_message)
        return list_surveys()

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
    restrict_message = helpers.restrict_edit_access(survey, False)
    if restrict_message:
        flask.flash(restrict_message)
        return list_surveys()

    survey_id = survey['survey_id']
    return helpers.process_params_request(True, survey_id, access_key)


@blueprint.route('/1/surveys/<access_key>/questions', methods=['POST'])
def save_questions(access_key):
    survey = helpers.get_survey_data(access_key)
    restrict_message = helpers.restrict_edit_access(survey, False)
    if restrict_message:
        flask.flash(restrict_message)
        return list_surveys()

    questions = flask.request.get_json(force=True)
    helpers.set_questions(survey['survey_id'], questions)
    return flask.jsonify({'success': True})


@blueprint.route('/1/surveys/<access_key>/close')
def close_survey(access_key):
    survey = helpers.get_survey_data(access_key)
    restrict_message = helpers.restrict_edit_access(survey, False)
    if restrict_message:
        return flask.jsonify({'success': False, 'message': restrict_message})
    if survey['start_time'] > datetime.now():
        return flask.jsonify({
            'success': False,
            'message': 'Survey has not opened yet'
        })

    helpers.close_survey(survey['survey_id'])
    return flask.jsonify({'success': True})


@blueprint.route('/1/surveys/<access_key>', methods=['DELETE'])
def delete_survey(access_key):
    survey = helpers.get_survey_data(access_key)
    restrict_message = helpers.restrict_edit_access(survey, True)
    if restrict_message:
        return flask.jsonify({'success': False, 'message': restrict_message})

    helpers.delete_survey(survey['survey_id'])
    return flask.jsonify({'success': True})


@blueprint.route('/1/surveys/<access_key>/submit', methods=['POST'])
def submit(access_key):
    def error(message):
        return flask.jsonify({'success': False, 'message': message})

    survey = helpers.get_survey_data(access_key)
    restrict_message = helpers.restrict_take_access(survey)
    if restrict_message: return error(restrict_message)
    responses = flask.request.get_json(force=True)['responses']
    expected_question_ids = helpers.get_question_ids(survey['survey_id'])
    if [response['question']
            for response in responses] != expected_question_ids:
        return error('Survey questions have changed')

    question_types = helpers.get_question_types()
    response_jsons = []
    for response in responses:
        question_id = response['question']
        value = response['response']
        type_id = helpers.get_question_type(question_id)
        if type_id == question_types['Dropdown']:
            if type(value) != int:
                return error('Invalid response to dropdown')
            if helpers.invalid_choice_id(question_id, value):
                return error('Invalid choice for dropdown')
            response_json = value
        elif type_id == question_types['Elected position']:
            if type(value) != list:
                return error('Invalid response to elected position')
            response_json = []
            ranked_set = set()
            ranked_count = 0
            for rank in value:
                if type(rank) != list:
                    return error('Invalid response to elected position')
                rank_json = []
                for candidate in rank:
                    if candidate is None:  # No
                        rank_json.append(None)
                        continue

                    if type(candidate) != dict:
                        return error('Invalid response to elected position')
                    choice_id = candidate.get('choice_id')
                    if choice_id is None:
                        user_id = candidate.get('user_id')
                        if user_id is None or not get_member_data(
                                user_id, ['user_id']):
                            return error('Invalid choice for elected position')
                        rank_json.append(-user_id)
                    else:
                        if helpers.invalid_choice_id(question_id, choice_id):
                            return error('Invalid choice for elected position')
                        rank_json.append(choice_id)
                response_json.append(rank_json)
                ranked_set |= set(map(helpers.get_name, rank_json))
                ranked_count += len(rank)
                if len(ranked_set) < ranked_count:
                    return error('Candidate ranked twice for elected position')
        elif type_id == question_types['Checkboxes']:
            if type(value) != list:
                return error('Invalid response to checkboxes')
            response_json = []
            for chosen in value:
                if type(chosen) != int:
                    return error('Invalid response to checkboxes')
                if helpers.invalid_choice_id(question_id, chosen):
                    return error('Invalid choice for checkboxes')
                response_json.append(chosen)
        else:  # input field
            if type(value) != str: return error('Invalid text response')
            response_json = value
        response_jsons.append(json.dumps(response_json, separators=(',', ':')))
    helpers.set_responses(expected_question_ids, response_jsons)
    return flask.jsonify({'success': True})


@blueprint.route('/1/surveys/<access_key>/results')
def show_results(access_key):
    survey = helpers.get_survey_data(access_key)
    if not survey:
        flask.flash('Invalid access key')
        return list_surveys()
    user_id = helpers.get_user_id(flask.session.get('username'))
    now = datetime.now()
    creator_allowed = user_id == survey['creator'] and survey['end_time'] < now
    if not (creator_allowed or survey['results_shown']):
        flask.flash('You are not permitted to see the results at this time')
        return list_surveys()

    results = helpers.get_results(survey['survey_id'])
    return flask.render_template(
        'results.html',
        access_key=access_key,
        **survey,
        question_types=helpers.get_question_types(),
        results=results)


@blueprint.route('/1/surveys/<access_key>/release')
def release_results(access_key):
    if not check_permission(
            flask.session.get('username'), Permissions.SURVEYS):
        flask.abort(403)

    survey = helpers.get_survey_data(access_key)
    if not survey:
        flask.flash('Invalid access key')
        return list_surveys()
    user_id = helpers.get_user_id(flask.session.get('username'))
    if user_id != survey['creator']:
        flask.flash('You are not the creator of this survey')
        return list_surveys()
    if datetime.now() < survey['end_time']:
        flask.flash('Survey has not yet finished')
        return list_surveys()

    helpers.update_survey_params(survey['survey_id'], {'results_shown': True})
    return flask.redirect(
        flask.url_for('voting.show_results', access_key=access_key))


@blueprint.route('/1/surveys/<access_key>/my-response')
def show_my_response(access_key):
    username = flask.session.get('username')
    if not username:
        flask.flash('Must be logged in to see response')
        return list_surveys()
    survey = helpers.get_survey_data(access_key)
    if not survey:
        flask.flash('Invalid access key')
        return list_surveys()
    questions = helpers.get_responses(survey['survey_id'],
                                      helpers.get_user_id(username))
    some_response = False
    for question in questions:
        responses = question['responses']
        if responses:
            some_response = True
            question['response'], = responses
        else:
            question['response'] = None
    if not some_response:
        flask.flash('You have not responded to this survey')
        return list_surveys()

    return flask.render_template(
        'my-response.html',
        **survey,
        question_types=helpers.get_question_types(),
        questions=questions)
