import datetime
import flask
import pymysql.cursors
from pymysql.constants import ER
from pymysql.err import IntegrityError

from donut.auth_utils import get_user_id

TERMS = {'FA': 1, 'WI': 2, 'SP': 3}
TERM_NAMES = {v: k for k, v in TERMS.items()}


def get_most_recent_term():
    """
    Returns the most recent {'year', 'term'} struct with courses,
    or None if there are no courses.
    """
    terms = get_terms()
    return terms[0] if terms else None


def get_current_term(today=None):
    """
    Returns the {'year', 'term'} struct for the term containing the given
    date (defaults to today), falling back to the most recent term with
    courses if the mapped term has no courses.

    Month mapping (Caltech registrar convention):
    - Sep-Dec -> FA (1) of the same calendar year
    - Jan-Mar -> WI (2) of the same calendar year
    - Apr-Jun -> SP (3) of the same calendar year
    - Jul-Aug -> no regular term; fall back to most recent term
    """
    if today is None:
        today = datetime.date.today()
    month = today.month
    year = today.year
    mapped_term = None
    if 9 <= month <= 12:
        mapped_term = {'year': year, 'term': TERMS['FA']}
    elif 1 <= month <= 3:
        mapped_term = {'year': year, 'term': TERMS['WI']}
    elif 4 <= month <= 6:
        mapped_term = {'year': year, 'term': TERMS['SP']}

    if mapped_term is not None:
        query = """
            SELECT year, term FROM courses
            WHERE year = %s AND term = %s
            LIMIT 1
        """
        with flask.g.pymysql_db.cursor() as cursor:
            cursor.execute(query, (mapped_term['year'], mapped_term['term']))
            if cursor.fetchone():
                return mapped_term
    return get_most_recent_term()


def try_int(x):
    """
    Converts a float to an int if it is already an integral value.
    Makes the JSON a little smaller.
    """
    as_int = int(x)
    return as_int if as_int == x else x


def get_terms():
    """
    Returns {'year', 'term'} structs for each year with courses,
    sorted from most to least recent.
    """
    query = """
        SELECT DISTINCT year, term FROM courses
        ORDER BY year DESC, (term + 1) % 3 DESC
    """
    with flask.g.pymysql_db.cursor() as cursor:
        cursor.execute(query)
        return cursor.fetchall()


def get_year_courses():
    """
    Returns {'ids'[], number', name', 'units'[3], 'instructor', 'terms'[]}
    structs for all courses in the most recent FA, WI, and SP terms.
    'ids' and 'terms' link the ids of different terms of the same course.
    """
    # Find most recent year for each term that has courses
    term_years = {}
    for term_year in get_terms():
        term = term_year['term']
        if term not in term_years:
            term_years[term] = term_year['year']
    query = """
        SELECT
            course_id,
            CONCAT(department, ' ', course_number) AS number,
            name,
            units_lecture, units_lab, units_homework
        FROM courses
        WHERE year = %s AND term = %s
    """
    instructor_query = """
        SELECT DISTINCT instructor
        FROM sections NATURAL JOIN instructors
        WHERE course_id = %s
    """
    courses = {}  # mapping of course numbers to course structs
    with flask.g.pymysql_db.cursor() as cursor:
        for term, year in term_years.items():
            cursor.execute(query, (year, term))
            for course in cursor.fetchall():
                number = course['number']
                cursor.execute(instructor_query, course['course_id'])
                instructors = cursor.fetchall()
                instructor = instructors[0]['instructor'] \
                    if len(instructors) == 1 else None
                matching_course = courses.get(number)
                if matching_course:
                    matching_course['terms'].append(term)
                    matching_course['ids'].append(course['course_id'])
                    if instructor != matching_course['instructor']:
                        matching_course['instructor'] = None
                else:
                    units = (course['units_lecture'], course['units_lab'],
                             course['units_homework'])
                    courses[number] = {
                        # Separate course id for each term
                        'ids': [course['course_id']],
                        'number': number,
                        'name': course['name'],
                        'units': tuple(map(try_int, units)),
                        'instructor': instructor,
                        'terms': [term]
                    }
    return sorted(
        courses.values(), key=lambda course: course['number'].lower())


def add_planner_course(username, course_id, year):
    """
    Adds a certain course to a certain user's planner for a given year.
    Year 1 is frosh year, year 2 is smore year, etc.
    """
    user_id = get_user_id(username)
    query = 'INSERT INTO planner_courses (user_id, course_id, planner_year) VALUES (%s, %s, %s)'
    with flask.g.pymysql_db.cursor() as cursor:
        cursor.execute(query, (user_id, course_id, year))


def drop_planner_course(username, course_id, year):
    """
    Removes a certain course from a certain user's planner for a given year.
    Year 1 is frosh year, year 2 is smore year, etc.
    """
    user_id = get_user_id(username)
    query = """
        DELETE FROM planner_courses
        WHERE user_id = %s AND course_id = %s AND planner_year = %s
    """
    with flask.g.pymysql_db.cursor() as cursor:
        cursor.execute(query, (user_id, course_id, year))


def add_planner_placeholder(username, year, term, course, units):
    """
    Adds a placedholder course to a user's planner for a given term.
    Year 1 is frosh year, year 2 is smore year, etc.
    Term 1 is FA, 2 is WI, and 3 is SP.
    """
    user_id = get_user_id(username)
    query = """
        INSERT INTO planner_placeholders
            (user_id, planner_year, term, course_name, course_units)
        VALUES (%s, %s, %s, %s, %s)
    """
    with flask.g.pymysql_db.cursor() as cursor:
        cursor.execute(query, (user_id, year, term, course, units))
        return cursor.lastrowid


def drop_planner_placeholder(username, placeholder_id):
    """
    Removes the placeholder with the given ID from the user's planner.
    Returns whether successful (i.e. the given placeholder did belong to the user).
    """
    user_id = get_user_id(username)
    query = """
        DELETE FROM planner_placeholders
        WHERE placeholder_id = %s AND user_id = %s
    """
    with flask.g.pymysql_db.cursor() as cursor:
        cursor.execute(query, (placeholder_id, user_id))
        return cursor.rowcount > 0


def get_user_planner_courses(username):
    """
    Returns {'ids'[1], 'number', 'units', 'terms'[1], 'year'} structs
    for each course on a certain user's planner.
    Unlike in get_planner_courses(), the unit counts are already summed.
    """
    query = """
        SELECT
            course_id,
            CONCAT(department, ' ', course_number) AS number,
            term,
            units,
            planner_year
        FROM users NATURAL JOIN planner_courses NATURAL JOIN courses
        WHERE username = %s
        ORDER BY units DESC, number
    """
    with flask.g.pymysql_db.cursor() as cursor:
        cursor.execute(query, username)
        courses = cursor.fetchall()
    return [{
        'ids': (course['course_id'], ),
        'number': course['number'],
        'units': try_int(course['units']),
        'terms': (course['term'], ),
        'year': course['planner_year']
    } for course in courses]


def get_user_planner_placeholders(username):
    query = """
        SELECT placeholder_id, planner_year, term, course_name, course_units
        FROM planner_placeholders NATURAL JOIN users
        WHERE username = %s
        ORDER BY course_units DESC, course_name
    """
    with flask.g.pymysql_db.cursor() as cursor:
        cursor.execute(query, username)
        placeholders = cursor.fetchall()
    return [{
        'id': placeholder['placeholder_id'],
        'year': placeholder['planner_year'],
        'term': placeholder['term'],
        'course': placeholder['course_name'],
        'units': try_int(placeholder['course_units'])
    } for placeholder in placeholders]


def get_scheduler_courses(year, term):
    """
    Returns {'id', 'number', 'name', 'units'[3], 'sections'[]} structs for each
    course in a certain term of a certain year.
    'sections' is a list of {'number', 'instructor', 'grades', 'times'} structs.
    """
    query = """
        SELECT
            course_id,
            CONCAT(department, ' ', course_number) AS number,
            name,
            units_lecture, units_lab, units_homework,
            section_number,
            instructor,
            grades_type,
            times,
            locations
        FROM
            courses
            NATURAL JOIN sections
            NATURAL JOIN instructors
            NATURAL JOIN grades_types
        WHERE year = %s AND term = %s
    """
    with flask.g.pymysql_db.cursor() as cursor:
        cursor.execute(query, (year, term))
        sections = cursor.fetchall()
    course_sections = {}
    for section in sections:
        course_id = section['course_id']
        course = course_sections.get(course_id)
        if course:
            sections = course['sections']
        else:
            sections = []
            units = (section['units_lecture'], section['units_lab'],
                     section['units_homework'])
            course_sections[course_id] = {
                'id': course_id,
                'number': section['number'],
                'name': section['name'],
                'units': tuple(map(try_int, units)),
                'sections': sections
            }
        sections.append({
            'number': section['section_number'],
            'instructor': section['instructor'],
            'grades': section['grades_type'],
            'times': section['times'],
            'locations': section['locations']
        })
    courses = course_sections.values()
    for course in courses:
        course['sections'].sort(key=lambda section: section['number'])
    return sorted(courses, key=lambda course: course['number'].lower())


# Cache for the current term's full schedule. The schedule DB only changes
# on registrar imports (rare), so caching this avoids re-running the large
# scheduler query on every page view.
_NOW_COURSES_CACHE = {'key': None, 'courses': None, 'expires': 0.0}
_NOW_COURSES_TTL = 900  # seconds


def get_cached_scheduler_courses(year, term):
    """
    Same as get_scheduler_courses(), but cached in-process for a short TTL
    to minimize database load from repeated page views.
    """
    import time
    key = (year, term)
    now = time.time()
    if _NOW_COURSES_CACHE['key'] == key and \
            _NOW_COURSES_CACHE['expires'] > now:
        return _NOW_COURSES_CACHE['courses']
    courses = get_scheduler_courses(year, term)
    _NOW_COURSES_CACHE.update(
        key=key, courses=courses, expires=now + _NOW_COURSES_TTL)
    return courses


def _parse_time_bound(value):
    """Parses an 'HH:MM' string into hours since midnight, or None."""
    try:
        hour, minute = value.split(':')
        return int(hour) + int(minute) / 60
    except (ValueError, AttributeError):
        return None


def _find_courses_at(courses, weekday_letter, now_hours, found_ids):
    """
    Returns [{'number', 'name', 'instructor', 'location', 'time'}] rows for
    courses in session at the given weekday/time. Mirrors the original
    mock-page logic: skips Intercollegiate courses, OM times, and arranged
    ('A') locations. found_ids prevents listing the same course twice.
    """
    rows = []
    for course in courses:
        if course['id'] in found_ids:
            continue
        if course['name'].startswith('Intercollegiate'):
            continue
        match = None
        for section in course['sections']:
            locations = (section.get('locations') or '').split('\n')
            times = (section.get('times') or '').split('\n')
            for i, time in enumerate(times):
                if not time or time.startswith('OM'):
                    continue
                if weekday_letter not in time:
                    continue
                if i >= len(locations) or locations[i] == 'A':
                    continue
                parts = time.split(' ')
                if len(parts) < 4:
                    continue
                start = _parse_time_bound(parts[1])
                end = _parse_time_bound(parts[3])
                if start is None or end is None:
                    continue
                if start <= now_hours <= end:
                    match = {
                        'number': course['number'],
                        'name': course['name'],
                        'instructor': section['instructor'],
                        'location': locations[i],
                        'time': time
                    }
                    break
            if match is not None:
                break
        if match is not None:
            found_ids.add(course['id'])
            rows.append(match)
    return rows


def get_now_rows(now=None):
    """
    Returns {'year', 'term', 'rows'} for the current term, where 'rows' is a
    small pre-filtered list of {'type': 'course', ...} and
    {'type': 'splitter'} dicts: classes in session now, followed by upcoming
    classes grouped behind splitter rows. Doing this server-side keeps the
    API response tiny (dozens of rows instead of the full course catalog)
    and means the client makes exactly one lightweight request.
    """
    if now is None:
        now = datetime.datetime.now()
    term = get_current_term(today=now.date()
                            if isinstance(now, datetime.datetime) else now)
    if term is None:
        return {'year': None, 'term': None, 'rows': []}
    courses = get_cached_scheduler_courses(term['year'], term['term'])

    weekday = ['M', 'T', 'W', 'R', 'F', 'S', 'U'][now.weekday()]
    now_hours = now.hour + now.minute / 60

    found_ids = set()
    rows = []
    for row in _find_courses_at(courses, weekday, now_hours, found_ids):
        rows.append(dict(row, type='course'))

    # Upcoming half-hour/hour boundaries within the next ~6 hours,
    # mirroring the mock page's lookahead.
    upcoming_hour = now.hour
    upcoming_minute = now.minute
    for _ in range(6):
        for mark in (30, 60, 30, 60):
            if upcoming_minute >= mark:
                continue
            upcoming_minute = mark
            probe_hours = upcoming_hour + upcoming_minute / 60
            if probe_hours >= 24:
                continue
            upcoming_rows = _find_courses_at(courses, weekday, probe_hours,
                                             found_ids)
            if upcoming_rows:
                rows.append({'type': 'splitter'})
                for row in upcoming_rows:
                    rows.append(dict(row, type='course'))
        upcoming_minute = 0
        upcoming_hour += 1
        if upcoming_hour >= 24:
            break
    return {'year': term['year'], 'term': term['term'], 'rows': rows}


# External event feeds shown on the /now page alongside classes.
# Fetched server-side (browsers can't fetch these feeds directly due to CORS)
# and cached in-process so all page views share one upstream fetch.
# All times are compared in server-local wall time; the server runs on
# Pacific time, matching the Pasadena events in these feeds.
CAMPUS_EVENTS_URL = \
    'https://www.caltech.edu/campus-life-events/calendar/rss?type=public'
ATHLETICS_EVENTS_URL = 'https://gocaltech.com/calendar.ashx/calendar.rss' \
    '?sport_id=0&_=cmulxmhf50001359smxfilrwh'
_EVENTS_CACHE = {'events': None, 'expires': 0.0}
_EVENTS_TTL = 1800  # seconds
_EVENTS_FETCH_TIMEOUT = 10  # seconds
# The campus feed lists only start times, so assume this duration when
# deciding whether an event is currently ongoing.
_CAMPUS_DEFAULT_DURATION = datetime.timedelta(hours=2)


def _fetch_url(url):
    """Fetches a URL, returning response bytes or None on any failure."""
    import urllib.request
    request = urllib.request.Request(
        url, headers={'User-Agent': 'donut-caltech-events/1.0'})
    try:
        with urllib.request.urlopen(
                request, timeout=_EVENTS_FETCH_TIMEOUT) as response:
            return response.read()
    except Exception:
        flask.current_app.logger.warning('Failed to fetch %s', url)
        return None


def _as_local_naive(value):
    """Converts an aware datetime to naive server-local time, or None."""
    if value is None:
        return None
    if value.tzinfo is None:
        return value
    return value.astimezone().replace(tzinfo=None)


def parse_campus_events(xml_bytes):
    """
    Parses Caltech campus-life RSS items into
    {'title', 'url', 'location', 'starts', 'ends'} dicts.
    The feed carries no location or end time, so location is '' and the
    end is assumed to be _CAMPUS_DEFAULT_DURATION after the start.
    """
    import email.utils
    import xml.etree.ElementTree as ET
    events = []
    try:
        channel = ET.fromstring(xml_bytes).find('channel')
        items = channel.findall('item') if channel is not None else []
    except ET.ParseError:
        return events
    for item in items:
        title = (item.findtext('title') or '').strip()
        if not title:
            continue
        try:
            starts = _as_local_naive(
                email.utils.parsedate_to_datetime(
                    item.findtext('pubDate') or ''))
        except (TypeError, ValueError):
            continue
        if starts is None:
            continue
        events.append({
            'title': title,
            'url': (item.findtext('link') or '').strip(),
            'location': '',
            'starts': starts,
            'ends': starts + _CAMPUS_DEFAULT_DURATION
        })
    return events


def athletics_game_name(title):
    """
    Extracts the sports game name from a SIDEARM athletics feed title,
    e.g. "8/29 11:00 AM [W] California Institute of Technology Men's
    Water Polo at Crafton Hills" -> "Men's Water Polo at Crafton Hills".
    """
    import re
    name = re.sub(
        r'^\d{1,2}/\d{1,2}\s+\d{1,2}:\d{2}\s*[AP]M\s*',
        '',
        title,
        flags=re.IGNORECASE)
    name = re.sub(r'^\[[WLT]\]\s*', '', name)
    name = re.sub(
        r'^(California Institute of Technology|Caltech)\s+',
        '',
        name,
        flags=re.IGNORECASE)
    return name.strip()


def _parse_sidearm_date(value):
    """Parses SIDEARM '2026-08-29T11:00:00.0000000[Z]' stamps, or None."""
    import re
    if not value:
        return None
    try:
        return datetime.datetime.strptime(
            re.sub(r'\.\d+', '', value.strip().rstrip('Z')),
            '%Y-%m-%dT%H:%M:%S')
    except ValueError:
        return None


def parse_athletics_events(xml_bytes):
    """
    Parses the GoCaltech SIDEARM RSS feed into event dicts (same shape as
    parse_campus_events), using the feed's local start/end times.
    """
    import xml.etree.ElementTree as ET
    namespaces = {
        'ev': 'http://purl.org/rss/1.0/modules/event/',
        's': 'http://sidearmsports.com/schemas/cal_rss/1.0/'
    }
    events = []
    try:
        channel = ET.fromstring(xml_bytes).find('channel')
        items = channel.findall('item') if channel is not None else []
    except ET.ParseError:
        return events
    for item in items:
        title = athletics_game_name((item.findtext('title') or '').strip())
        if not title:
            continue
        starts = _parse_sidearm_date(
            item.findtext('s:localstartdate', namespaces=namespaces))
        if starts is None:
            starts = _parse_sidearm_date(
                item.findtext('ev:startdate', namespaces=namespaces))
        if starts is None:
            continue
        ends = _parse_sidearm_date(
            item.findtext('s:localenddate', namespaces=namespaces))
        if ends is None:
            ends = _parse_sidearm_date(
                item.findtext('ev:enddate', namespaces=namespaces))
        if ends is None:
            ends = starts + _CAMPUS_DEFAULT_DURATION
        events.append({
            'title':
            title,
            'url': (item.findtext('link') or '').strip(),
            'location': (item.findtext('ev:location', namespaces=namespaces)
                         or '').strip(),
            'starts':
            starts,
            'ends':
            ends
        })
    return events


def _event_row(event):
    """Formats a parsed event as a {'type': 'event', ...} display row."""
    return {
        'type': 'event',
        'title': event['title'],
        'url': event['url'],
        'location': event['location'],
        'time': event['starts'].strftime('%-I:%M %p')
    }


def _group_event_rows(events, now):
    """
    Groups today's events into ongoing, starting within the next hour, and
    later today, with splitter rows between groups (mirroring the courses
    table). Returns a list of {'type': 'event', ...} / {'type': 'splitter'}
    dicts.
    """
    ongoing = sorted(
        (event for event in events if event['starts'] <= now <= event['ends']),
        key=lambda event: event['starts'])
    upcoming = sorted(
        (event for event in events
         if event['starts'] > now and event['starts'].date() == now.date()),
        key=lambda event: event['starts'])
    next_hour = [
        event for event in upcoming
        if event['starts'] <= now + datetime.timedelta(hours=1)
    ]
    later_today = [
        event for event in upcoming
        if event['starts'] > now + datetime.timedelta(hours=1)
    ]
    rows = [_event_row(event) for event in ongoing]
    for group in (next_hour, later_today):
        if group and rows:
            rows.append({'type': 'splitter'})
        rows.extend(_event_row(event) for event in group)
    return rows


def get_event_rows(now=None):
    """
    Returns combined campus + athletics event rows for today, grouped as
    ongoing / next hour / later today. Upstream fetches are cached
    in-process; grouping is recomputed per request (cheap). Never raises:
    feed failures yield an empty list.
    """
    import time
    if now is None:
        now = datetime.datetime.now()
    fetched = time.time()
    if _EVENTS_CACHE['events'] is not None and \
            _EVENTS_CACHE['expires'] > fetched:
        events = _EVENTS_CACHE['events']
    else:
        events = []
        campus_xml = _fetch_url(CAMPUS_EVENTS_URL)
        if campus_xml:
            events.extend(parse_campus_events(campus_xml))
        athletics_xml = _fetch_url(ATHLETICS_EVENTS_URL)
        if athletics_xml:
            events.extend(parse_athletics_events(athletics_xml))
        _EVENTS_CACHE.update(events=events, expires=fetched + _EVENTS_TTL)
    return _group_event_rows(events, now)


def add_scheduler_section(username, course, section):
    """
    Adds a certain section number of a certain course
    to a certain user's schedule for the course's term.
    """
    user_id = get_user_id(username)
    query = """
        INSERT INTO scheduler_sections (user_id, course_id, section_number)
        VALUES (%s, %s, %s)
    """
    with flask.g.pymysql_db.cursor() as cursor:
        cursor.execute(query, (user_id, course, section))


def drop_scheduler_section(username, course, section):
    """
    Removes a certain section number of a certain course
    from a certain user's schedule for the course's term.
    """
    user_id = get_user_id(username)
    query = """
        DELETE FROM scheduler_sections
        WHERE user_id = %s AND course_id = %s AND section_number = %s
    """
    with flask.g.pymysql_db.cursor() as cursor:
        cursor.execute(query, (user_id, course, section))


def get_user_scheduler_sections(username, year, term):
    """
    Returns {'id' (course_id), 'section' (section_number)} structs for each
    section on a certain user's schedule for a certain term of a certain year.
    """
    query = """
        SELECT course_id, section_number
        FROM
            users
            NATURAL JOIN scheduler_sections
            NATURAL JOIN courses
        WHERE username = %s AND year = %s AND term = %s
    """
    with flask.g.pymysql_db.cursor() as cursor:
        cursor.execute(query, (username, year, term))
        sections = cursor.fetchall()
    return [{
        'id': section['course_id'],
        'section': section['section_number']
    } for section in sections]

is_duplicate_error = lambda e: \
    isinstance(e, IntegrityError) and e.args[0] == ER.DUP_ENTRY


def get_notes(username, course, section):
    user_id = get_user_id(username)
    query = """
        SELECT notes FROM scheduler_sections
        WHERE user_id = %s AND course_id = %s AND section_number = %s
    """
    with flask.g.pymysql_db.cursor() as cursor:
        cursor.execute(query, (user_id, course, section))
        notes = cursor.fetchone()
    return notes and notes['notes']


def edit_notes(username, course, section, notes):
    user_id = get_user_id(username)
    query = """
        UPDATE scheduler_sections SET notes = %s
        WHERE user_id = %s AND course_id = %s AND section_number = %s
    """
    with flask.g.pymysql_db.cursor() as cursor:
        cursor.execute(query, (notes, user_id, course, section))


def delete_notes(username, course, section):
    user_id = get_user_id(username)
    query = """
        UPDATE scheduler_sections SET notes = NULL
        WHERE user_id = %s AND course_id = %s AND section_number = %s
    """
    with flask.g.pymysql_db.cursor() as cursor:
        cursor.execute(query, (user_id, course, section))
