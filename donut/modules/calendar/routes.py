import flask
from donut import auth_utils
from donut.modules.calendar import helpers
from donut.modules.calendar import blueprint
import datetime

last_update_time = datetime.datetime(year=1970, month=1, day=1)


@blueprint.route('/calendar')
def calendar():
    if not auth_utils.is_caltech_user():
        return auth_utils.login_redirect()

    return flask.render_template(
        'calendar.html', permissions=helpers.get_permission())


@blueprint.route('/calendar/add_events')
def add_events():
    if 'username' not in flask.session:
        return auth_utils.login_redirect()

    return flask.render_template(
        'add_events.html', permissions=helpers.get_permission())


@blueprint.route('/calendar/share_cal')
def share_cal():
    if 'username' not in flask.session:
        return auth_utils.login_redirect()

    return flask.render_template(
        'share_cal.html', permissions=helpers.get_permission())


@blueprint.route('/calendar/search')
def calendar_search():
    if not auth_utils.is_caltech_user():
        return auth_utils.login_redirect()

    return flask.render_template(
        'calendar_search.html', permissions=helpers.get_permission())


@blueprint.route('/calendar/sync')
def sync():
    if not auth_utils.is_caltech_user():
        return auth_utils.login_redirect()

    res = helpers.sync_data(all_data=True)
    error_message = helpers.check_if_error(res)
    if error_message:
        flask.flash(error_message)
    global last_update_time
    last_update_time = datetime.datetime.now()
    return flask.render_template(
        'calendar.html', permissions=helpers.get_permission())


@blueprint.route('/1/calendar_all_events', methods=['POST'])
def get_all_events():
    if not auth_utils.is_caltech_user():
        return auth_utils.login_redirect()

    res = helpers.sync_data(all_data=True)
    error_message = helpers.check_if_error(res)
    if error_message:
        return flask.jsonify({'err': error_message})
    return flask.jsonify({'events': res})


@blueprint.route('/1/calendar_all_events_backup', methods=['POST'])
def get_all_events_backup():
    if not auth_utils.is_caltech_user():
        return auth_utils.login_redirect()

    res = helpers.get_events_backup(all_data=True)
    error_message = helpers.check_if_error(res)
    if error_message:
        return flask.jsonify({'err': error_message})
    return flask.jsonify({
        'events':
        res,
        'permissions':
        helpers.get_permission(),
        'last_update_time':
        last_update_time.strftime("%Y-%m-%dT%H:%M:%SZ")
    })


@blueprint.route('/1/calendar_events', methods=['POST'])
def get_events():
    if not auth_utils.is_caltech_user():
        return auth_utils.login_redirect()

    res = helpers.sync_data(1, flask.request.form['year'], 12,
                            flask.request.form['year'])
    error_message = helpers.check_if_error(res)
    if error_message:
        return flask.jsonify({'err': error_message})
    return flask.jsonify({'events': res})


@blueprint.route('/1/calendar_events_backup', methods=['POST'])
def get_events_backup():
    if not auth_utils.is_caltech_user():
        return auth_utils.login_redirect()

    res = helpers.get_events_backup(1, flask.request.form['year'], 12,
                                    flask.request.form['year'])
    error_message = helpers.check_if_error(res)
    if error_message:
        return flask.jsonify({'err': error_message})
    return flask.jsonify({
        'events':
        res,
        'last_update_time':
        last_update_time.strftime("%Y-%m-%dT%H:%M:%SZ")
    })


@blueprint.route('/calendar/share_cal', methods=['POST'])
def calendar_share_cal():
    if 'username' not in flask.session:
        return auth_utils.login_redirect()

    fields = ['email', 'tag', 'access_level']
    for field in fields:
        if None == flask.request.form.get(field):
            flask.flash('Please fill in all required fields (marked with *)',
                        'error')
            return flask.redirect(flask.url_for('calendar.calendar'))
    e = helpers.share_calendar(
        flask.request.form.getlist('tag'),
        flask.request.form.get('email'),
        flask.request.form.get('access_level'))

    if e:
        flask.flash('Error when sharing calendars:' + e +
                    " ; if the error persists, contact dev team", 'error')
    else:
        flask.flash('Success! Please check your gmail')
    return flask.redirect(flask.url_for('calendar.calendar'))


@blueprint.route('/1/calendar/delete_event', methods=['POST'])
def calendar_delete():
    if 'username' not in flask.session:
        return auth_utils.login_redirect()

    return flask.jsonify({
        'deleted':
        helpers.delete(flask.request.form['id'], flask.request.form['tag'])
    })


@blueprint.route('/calendar/add_events/<int:update>', methods=['POST'])
def calendar_add_events(update=0):
    if 'username' not in flask.session:
        return auth_utils.login_redirect()

    fields = [
        'name', 'description', 'start_date', 'start_hour', 'start_minute',
        'end_hour', 'end_minute', 'end_date', 'tag'
    ]
    for field in fields:
        if None == flask.request.form.get(field):
            flask.flash('Please fill in all required fields (marked with *)',
                        'error')
            return flask.redirect(flask.url_for('calendar.calendar'))
    start_date = flask.request.form.get('start_date')
    start_hour = flask.request.form.get('start_hour')
    start_time = flask.request.form.get('start_minute')
    end_date = flask.request.form.get('end_date')
    end_hour = flask.request.form.get('end_hour')
    end_time = flask.request.form.get('end_minute')

    start_year, start_month, start_day = map(int, start_date.split('-'))
    end_year, end_month, end_day = map(int, end_date.split('-'))

    begin_datetime = datetime.datetime(start_year, start_month, start_day,
                                       int(start_hour), int(start_time))
    end_datetime = datetime.datetime(end_year, end_month, end_day,
                                     int(end_hour), int(end_time))
    if begin_datetime > end_datetime:
        flask.flash('Invalid times', 'error')
        return flask.redirect(flask.url_for('calendar.calendar'))

    start_time = start_date + 'T' + start_hour + ":" + start_time + ":00"
    end_time = end_date + 'T' + end_hour + ":" + end_time + ":00"

    e = helpers.add_event(
        flask.request.form.get('name'),
        flask.request.form.get('description'),
        flask.request.form.getlist('tag'), start_time, end_time, update,
        flask.request.form.get('location'), flask.request.form.get('eventId'))
    if e:
        flask.flash('Error when adding events: ' + str(e) +
                    ' ; If this error persists, contact devteam', 'error')

    return flask.redirect(flask.url_for('calendar.calendar'))
