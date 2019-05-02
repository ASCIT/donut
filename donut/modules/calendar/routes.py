import flask
from donut import auth_utils
from donut.modules.calendar import helpers
from donut.modules.calendar import blueprint
import datetime


@blueprint.route('/calendar')
def calendar():
    return flask.render_template(
        'calendar.html', permissions=helpers.get_permission())


@blueprint.route('/calendar/add_events')
def add_events():
    return flask.render_template(
        'add_events-iframe.html', permissions=helpers.get_permission())


@blueprint.route('/calendar/display')
def display():
    return flask.render_template(
        'display-iframe.html', permissions=helpers.get_permission())


@blueprint.route('/calendar/share_cal')
def share_cal():
    return flask.render_template(
        'share_cal-iframe.html', permissions=helpers.get_permission())


@blueprint.route('/calendar/events_list')
def events_list():
    return flask.render_template(
        'events_list-iframe.html', permissions=helpers.get_permission())


@blueprint.route('/calendar/sync')
def sync():
    helpers.sync_data(all_data=True)
    return flask.render_template(
        'calendar.html', permissions=helpers.get_permission())


@blueprint.route('/1/calendar_all_events', methods=['POST'])
def get_all_events():
    return flask.jsonify({'events': helpers.sync_data(all_data=True)})


@blueprint.route('/1/calendar_all_events_backup', methods=['POST'])
def get_all_events_backup():
    return flask.jsonify({'events': helpers.get_all_events_backup()})


@blueprint.route('/1/calendar_events', methods=['POST'])
def get_events():
    return flask.jsonify({
        'events':
        helpers.sync_data(1, flask.request.form['year'], 12,
                          flask.request.form['year'])
    })


@blueprint.route('/1/calendar_events_backup', methods=['POST'])
def get_events_backup():
    return flask.jsonify({
        'events':
        helpers.get_events_backup(1, flask.request.form['year'], 12,
                                  flask.request.form['year'])
    })


@blueprint.route('/calendar/share_cal', methods=['POST'])
def calendar_share_cal():
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
        flask.flash('Sucess! Please check your gmail')
    return flask.redirect(flask.url_for('calendar.calendar'))


@blueprint.route('/1/calendar/delete_event', methods=['POST'])
def calendar_delete():
    return flask.jsonify({
        'deleted':
        helpers.delete(flask.request.form['id'], flask.request.form['tag'])
    })


@blueprint.route('/calendar/add_events/<int:update>', methods=['POST'])
def calendar_add_events(update=0):
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
    begin_datetime = datetime.datetime(
        int(start_date[0:4]),
        int(start_date[5:7]),
        int(start_date[8:10]), int(start_hour), int(start_time))
    end_datetime = datetime.datetime(
        int(end_date[0:4]),
        int(end_date[5:7]), int(end_date[8:10]), int(end_hour), int(end_time))
    if begin_datetime >= end_datetime:
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
        flask.flash('Error when adding events: ' + e +
                    ' ; If this error persists, contact devteam', 'error')

    return flask.redirect(flask.url_for('calendar.calendar'))
