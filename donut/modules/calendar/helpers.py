import flask
import pymysql.cursors
import datetime
import calendar
from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from google.oauth2 import service_account
from donut.modules.calendar.permissions import calendar_permissions
from donut import auth_utils
import json

# DEBUGGING
import time
current_milli_time = lambda: int(round(time.time() * 1000))

SCOPES = ['https://www.googleapis.com/auth/calendar']
SERVICE_ACCOUNT_FILE = 'calendar.json'
creds = service_account.Credentials.from_service_account_file(
    SERVICE_ACCOUNT_FILE, scopes=SCOPES)

service = build('calendar', 'v3', credentials=creds)

cal_permissions = {
    'Avery': calendar_permissions.AVERY,
    'Blacker': calendar_permissions.BLACKER,
    'Dabney': calendar_permissions.DABNEY,
    'Fleming': calendar_permissions.FLEMING,
    'Lloyd': calendar_permissions.LLOYD,
    'Page': calendar_permissions.PAGE,
    'Ricketts': calendar_permissions.RICKETTS,
    'Ruddock': calendar_permissions.RUDDOCK,
    'Other': calendar_permissions.OTHER,  # For clubs
    'Athletics': calendar_permissions.
    ATHLETICS  # For all ath team and sports related events?
}

cal_id = {
    'Avery': 'el289n0076jqiklh4a04bs89gs@group.calendar.google.com',
    'Blacker': 'g77nktkofnupa29gg3lt419sik@group.calendar.google.com',
    'Dabney': 'l0m8d3bu0s3pt07oprvkm4su98@group.calendar.google.com',
    'Ricketts': 'i5aas9edk4r7db7g6a6gu6ijvg@group.calendar.google.com',
    'Fleming': 'ashica43p5tcnpvhlp37ohmirg@group.calendar.google.com',
    'Ruddock': '0ahv6ak2b73hvsbs15ncravju0@group.calendar.google.com',
    'Page': 'l7eb65otse6bm2apsp5d44lfa4@group.calendar.google.com',
    'Lloyd': 'jmit10sipo9jumhauqqadds7m8@group.calendar.google.com',
    'Other': 'autpk7a63u98aqqtrnj0mentpg@group.calendar.google.com',
    'Athletics': 'g2itc2p2r9affcc77l1d2vg47s@group.calendar.google.com'
}


def get_all_events_backup():
    '''
    Returns a list of all events from our db. 
    '''
    query = '''
        SELECT * FROM calendar_events
    '''
    with flask.g.pymysql_db.cursor() as cursor:
        cursor.execute(query)
        db_events = cursor.fetchall()
    for i in db_events:
        set_event_dict(i)
    return db_events


def set_event_dict(db_event):
    db_event['id'] = db_event['google_event_id']
    db_event['start'] = {
        'dateTime': db_event['begin_time'].isoformat('T') + 'Z'
    }
    db_event['end'] = {'dateTime': db_event['end_time'].isoformat('T') + 'Z'}
    db_event['organizer'] = {'displayName': db_event['calendar_tag']}


def get_events_backup(begin_month=datetime.datetime.now().month,
                      begin_year=datetime.datetime.now().year,
                      end_month=datetime.datetime.now().month,
                      end_year=datetime.datetime.now().year + 2):
    '''
    Gets events from our db. Backup from google calendars data. 
    '''
    query = """
            SELECT * FROM calendar_events 
            WHERE %s <= end_time AND begin_time <= %s
            ORDER BY begin_time
    """

    min_time = datetime.datetime(int(begin_year), begin_month,
                                 1).isoformat('T') + 'Z'
    max_time = datetime.datetime(
        int(end_year),
        int(end_month), calendar.monthrange(
            int(end_year), int(end_month))[1]).isoformat('T') + 'Z'
    with flask.g.pymysql_db.cursor() as cursor:
        cursor.execute(query, [min_time, max_time])
        db_events = cursor.fetchall()
    for i in db_events:
        set_event_dict(i)
    return db_events


def insert_event_to_db(calendar_tag,
                       google_event_id,
                       event_summary,
                       event_description,
                       event_location,
                       begin_time,
                       end_time,
                       username=''):
    '''
    Inserts events to our db. If the event already exists (by looking 
    for the google id) then update. 
    '''
    insert = '''
        INSERT INTO calendar_events (username, calendar_tag, 
        google_event_id, summary, description, 
        location, begin_time, end_time) VALUES
        (%s, %s, %s, %s, %s, %s, %s, %s) ON DUPLICATE KEY UPDATE
        username = VALUES(username), 
        summary=VALUES(summary), 
        description=VALUES(description),
        location=VALUES(location),
        begin_time=VALUES(begin_time),
        end_time=VALUES(end_time)
    '''
    with flask.g.pymysql_db.cursor() as cursor:
        cursor.execute(insert, [
            username, calendar_tag, google_event_id, event_summary,
            event_description, event_location, begin_time, end_time
        ])


def delete_event_from_db(google_id):
    '''
    Deletes events with a google_id from our db
    '''

    delete = '''
        DELETE FROM calendar_events WHERE google_event_id = %s
    '''
    with flask.g.pymysql_db.cursor() as cursor:
        cursor.execute(delete, [google_id])


def sync_data(begin_month=datetime.datetime.now().month,
              begin_year=datetime.datetime.now().year,
              end_month=datetime.datetime.now().month,
              end_year=datetime.datetime.now().year + 2,
              all_data=False):
    """
    Syncs data from google calendars to our own DB. The user
    may edit things on their google calendars page, and therefore
    our db data may not always be up to date with google's. 
    Any changes to our db data is always also made to google's 
    but not vice versa 
    This function is called manually, since always syncing data
    before serving the page may not be feasible --
    we have many calendars so every time we are requesting many
    requests. After about 2 reloads in ~<30 seconds, google starts
    throttling us and it will take upwards of minutes before either
    timing out or the requests are finished. 

    This function syncs either a period or all data, if all_data is set
    to true. 
    """
    min_time = datetime.datetime(int(begin_year), begin_month,
                                 1).isoformat('T') + 'Z'
    max_time = datetime.datetime(
        int(end_year),
        int(end_month), calendar.monthrange(
            int(end_year), int(end_month))[1]).isoformat('T') + 'Z'
    try:

        all_events = get_all_events() if all_data else get_events(
            begin_month, begin_year, end_month, end_year)
        if all_events == []:
            return
        # First, get the events from the database
        if all_data:
            query = """
                    SELECT * FROM calendar_events 
                    ORDER BY begin_time
                """
            with flask.g.pymysql_db.cursor() as cursor:
                cursor.execute(query)
                db_events = cursor.fetchall()
        else:
            query = """
                    SELECT * FROM calendar_events 
                    WHERE %s <= end_time AND begin_time <= %s
                    ORDER BY begin_time
                """
            with flask.g.pymysql_db.cursor() as cursor:
                cursor.execute(query, [min_time, max_time])
                db_events = cursor.fetchall()

        for i in all_events:
            calendar_tag = i['organizer']['displayName']
            google_event_id = i['id']
            event_summary = i.get('summary', '')
            event_description = i.get('description', '')
            event_location = i.get('location', '')
            begin_time = i['start']['dateTime'] if 'dateTime' in i[
                'start'] else i['start']['date']
            end_time = i['end']['dateTime'] if 'dateTime' in i['end'] else i[
                'end']['date']
            insert_event_to_db(calendar_tag, google_event_id, event_summary,
                               event_description, event_location, begin_time,
                               end_time)
            to_be_deleted = ''

            # Find the current google event in our db and make
            # sure that we mark it as visited.
            for db_event_key in db_events:
                if db_event_key['google_event_id'] == google_event_id:
                    to_be_deleted = db_event_key
                    db_events.remove(to_be_deleted)
                    break

        for db_event_key in db_events:
            delete_event_from_db(db_event_key['google_event_id'])
        return all_events
    except Exception as e:
        return []


def get_events(begin_month=datetime.datetime.now().month,
               begin_year=datetime.datetime.now().year,
               end_month=datetime.datetime.now().month,
               end_year=datetime.datetime.now().year + 2):
    """
    Gets events from the beginning to the end from google. 
    """
    try:
        min_time = datetime.datetime(int(begin_year), begin_month,
                                     1).isoformat('T') + 'Z'
        max_time = datetime.datetime(
            int(end_year),
            int(end_month),
            calendar.monthrange(int(end_year),
                                int(end_month))[1]).isoformat('T') + 'Z'
        all_events = []

        for key, value in cal_id.items():
            next_page = True
            while next_page:
                events_result = service.events().list(
                    calendarId=value,
                    timeMin=min_time,
                    timeMax=max_time,
                    singleEvents=True,
                    orderBy='startTime').execute()
                events = events_result.get('items', [])
                all_events.extend(events)
                next_page = 'nextPageToken' in events_result
        return all_events
    except:
        return []


def get_all_events():
    '''
    Gets all events from google calendars for ALL calendars. 
    '''
    try:
        all_events = []
        for key, value in cal_id.items():
            next_page = True
            while next_page:
                events_result = service.events().list(
                    calendarId=value,
                    singleEvents=True,
                    maxResults=2500,
                    orderBy='startTime').execute()
                events = events_result.get('items', [])
                all_events.extend(events)
                next_page = 'nextPageToken' in events_result
        return all_events
    except:
        return []


def add_event(name,
              description,
              calendar_tag,
              begin_time,
              end_time,
              update,
              location='',
              event_id=""):
    """
    Adds or updates events. If we are updating the event, 
    we need to have the event_id. 
    name: name of event
    description: description of event
    calendar_tag: a list of calendar tags for an event. Only
        a single value for updates
    begin_time: in format YYYY-MM-DDThh:mm:00Z
    end_time: as above. 
    update: bool for it we are adding events or updating them
    location: not required; location for event
    """
    try:
        if update:
            event = service.events().get(
                calendarId=cal_id[calendar_tag[0]],
                eventId=event_id).execute()
            event['start']['dateTime'] = begin_time
            event['end']['dateTime'] = end_time
            event['start']['date'] = None
            event['end']['date'] = None
            event['end']['timeZone'] = 'America/Los_Angeles'
            event['start']['timeZone'] = 'America/Los_Angeles'
            event['summary'] = name
            event['description'] = description
            event['location'] = location
            if get_permission()[calendar_tag[0]]:
                new_event = service.events().update(
                    calendarId=cal_id[calendar_tag[0]],
                    eventId=event['id'],
                    body=event).execute()
                insert_event_to_db(calendar_tag[0], new_event['id'], name,
                                   description, location, begin_time, end_time,
                                   flask.session['username'])
            return ''
        for cal_tag in calendar_tag:
            event = {
                'summary': name,
                'description': description,
                'start': {
                    'dateTime': begin_time,
                    'timeZone': 'America/Los_Angeles',
                },
                'end': {
                    'dateTime': end_time,
                    'timeZone': 'America/Los_Angeles',
                },
                'location': location,
                'visibility': 'public',
            }
            if get_permission()[cal_tag]:
                created_event = service.events().insert(
                    calendarId=cal_id[cal_tag], body=event).execute()
                insert_event_to_db(cal_tag, created_event['id'], name,
                                   description, location, begin_time, end_time,
                                   flask.session['username'])
        return ''
    except Exception as e:
        return e.get('message', e)


def share_calendar(calendars, email, permission_level):
    '''
    Shares a set of calendars to a given email
    '''
    try:
        for index, cal_name in enumerate(calendars):
            role = permission_level if auth_utils.check_permission(
                flask.session['username'],
                cal_permissions[cal_name]) else 'reader'

            # Shares a calendar given the id and an email
            rule = {
                'scope': {
                    'type': 'user',
                    'value': email,
                },
                'role': role
            }
            created_rule = service.acl().insert(
                calendarId=cal_id[cal_name], body=rule).execute()

            query = """
                INSERT INTO calendar_logs (username, calendar_gmail, user_gmail, acl_id, request_time, request_permission) VALUES
                (%s, %s, %s, %s, NOW(), %s) 
                """
            with flask.g.pymysql_db.cursor() as cursor:
                cursor.execute(query,
                               (flask.session['username'], cal_id[cal_name],
                                email, created_rule['id'], role))
        return ''
    except Exception as e:
        return e.get('message', e)


def delete(cal_event_id, cal_name):
    try:
        if get_permission()[cal_name]:
            service.events().delete(
                calendarId=cal_id[cal_name], eventId=cal_event_id).execute()
            delete_event_from_db(cal_event_id)
        return ''
    except Exception as e:
        return e.get('message', e)


def get_permission():
    ''' 
    Returns permissions list related to calendars 
    '''
    perms = {}
    # If they have edit permissions on anything, the events pages and stuff
    # will show up.
    anyy = False
    for tag in cal_permissions:
        perms[
            tag] = 'username' in flask.session and auth_utils.check_permission(
                flask.session['username'], cal_permissions[tag])
        anyy = perms[tag] or anyy
    perms['Any'] = anyy
    return perms
