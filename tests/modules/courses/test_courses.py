"""
Tests donut/modules/courses
"""
import datetime
import flask
import json
import pytest
from donut.testing.fixtures import client
from donut import app
from donut.modules.courses import helpers, routes


def test_planner(client):
    rv = client.get(flask.url_for('courses.planner'))
    assert rv.status_code == 200


def test_scheduler(client):
    rv = client.get(flask.url_for('courses.scheduler'))
    assert rv.status_code == 200


def test_now(client):
    rv = client.get(flask.url_for('courses.now'))
    assert rv.status_code == 200


def test_now_courses(client):
    rv = client.get(flask.url_for('courses.now_courses'))
    assert rv.status_code == 200
    assert rv.headers.get('Cache-Control') == 'no-store'
    data = json.loads(rv.data)
    assert set(data) == {'year', 'term', 'term_label', 'rows'}
    for row in data['rows']:
        if row['type'] == 'splitter':
            assert set(row) == {'type'}
        else:
            assert row['type'] == 'course'
            assert set(row) == {
                'type', 'number', 'name', 'instructor', 'location', 'time'
            }


def test_campus_events(client):
    # Fail-soft: 200 with a rows list even if the upstream feeds are down.
    rv = client.get(flask.url_for('courses.campus_events'))
    assert rv.status_code == 200
    assert rv.headers.get('Cache-Control') == 'no-store'
    data = json.loads(rv.data)
    assert set(data) == {'rows'}
    for row in data['rows']:
        if row['type'] == 'splitter':
            assert set(row) == {'type'}
        else:
            assert row['type'] == 'event'
            assert set(row) == {'type', 'title', 'url', 'location', 'time'}


def test_parse_campus_events():
    xml = b"""<?xml version="1.0" encoding="utf-8"?>
    <rss version="2.0"><channel>
      <item>
        <title>Machine Assisted Proof</title>
        <link>https://www.caltech.edu/campus-life-events/calendar/talk</link>
        <description>Terence Tao, UCLA</description>
        <pubDate>Fri, 09 Oct 2026 19:00:00 -0700</pubDate>
        <category>Public Lecture</category>
      </item>
      <item>
        <title>Untimed Event</title>
        <link>https://example.com/untimed</link>
      </item>
    </channel></rss>"""
    events = helpers.parse_campus_events(xml)
    assert len(events) == 1
    event = events[0]
    assert event['title'] == 'Machine Assisted Proof'
    assert event['url'] == \
        'https://www.caltech.edu/campus-life-events/calendar/talk'
    assert event['location'] == ''
    assert event['starts'] == datetime.datetime(2026, 10, 9, 19, 0)
    assert event['ends'] == event['starts'] + datetime.timedelta(hours=2)


def test_athletics_game_name():
    assert helpers.athletics_game_name(
        "8/29 11:00 AM [W] California Institute of Technology Men's "
        "Water Polo at Crafton Hills") == "Men's Water Polo at Crafton Hills"
    assert helpers.athletics_game_name(
        "9/1 11:00 AM California Institute of Technology Men's Soccer "
        "vs Park University Gilbert") == \
        "Men's Soccer vs Park University Gilbert"


def test_parse_athletics_events():
    xml = b"""<?xml version="1.0" encoding="utf-8"?>
    <rss version="2.0" xmlns:ev="http://purl.org/rss/1.0/modules/event/"
      xmlns:s="http://sidearmsports.com/schemas/cal_rss/1.0/">
    <channel>
      <item>
        <title>10/3 1:00 PM California Institute of Technology Football vs Pomona-Pitzer</title>
        <link>https://gocaltech.com/calendar.aspx?game_id=1</link>
        <ev:location>Pasadena, CA</ev:location>
        <s:localstartdate>2026-10-03T13:00:00.0000000</s:localstartdate>
        <s:localenddate>2026-10-03T16:00:00.0000000</s:localenddate>
      </item>
      <item>
        <title>Untimed Game</title>
        <link>https://gocaltech.com/calendar.aspx?game_id=2</link>
      </item>
    </channel></rss>"""
    events = helpers.parse_athletics_events(xml)
    assert len(events) == 1
    event = events[0]
    assert event['title'] == 'Football vs Pomona-Pitzer'
    assert event['url'] == 'https://gocaltech.com/calendar.aspx?game_id=1'
    assert event['location'] == 'Pasadena, CA'
    assert event['starts'] == datetime.datetime(2026, 10, 3, 13, 0)
    assert event['ends'] == datetime.datetime(2026, 10, 3, 16, 0)


def test_group_event_rows():
    now = datetime.datetime(2026, 9, 29, 18, 0)
    events = [
        {
            'title': 'Ongoing Talk',
            'url': 'https://example.com/a',
            'location': '',
            'starts': datetime.datetime(2026, 9, 29, 17, 0),
            'ends': datetime.datetime(2026, 9, 29, 19, 0)
        },
        {
            'title': 'Soon Game',
            'url': 'https://example.com/b',
            'location': 'Pasadena, CA',
            'starts': datetime.datetime(2026, 9, 29, 18, 30),
            'ends': datetime.datetime(2026, 9, 29, 20, 30)
        },
        {
            'title': 'Later Game',
            'url': 'https://example.com/c',
            'location': 'Pasadena, CA',
            'starts': datetime.datetime(2026, 9, 29, 21, 0),
            'ends': datetime.datetime(2026, 9, 29, 23, 0)
        },
        {
            'title': 'Yesterday Game',
            'url': 'https://example.com/d',
            'location': 'Pasadena, CA',
            'starts': datetime.datetime(2026, 9, 28, 18, 0),
            'ends': datetime.datetime(2026, 9, 28, 20, 0)
        },
    ]
    rows = helpers._group_event_rows(events, now)
    assert [row.get('title', row['type']) for row in rows] == [
        'Ongoing Talk', 'splitter', 'Soon Game', 'splitter', 'Later Game'
    ]
    assert rows[0]['time'] == '5:00 PM'
    assert rows[0]['location'] == ''


def test_planner_courses(client):
    rv = client.get(flask.url_for('courses.planner_courses'))
    assert rv.status_code == 200
    data = json.loads(rv.data)
    for course in data:  # sort term-id pairs
        id_terms = sorted(zip(course['ids'], course['terms']))
        course['ids'] = [course_id for course_id, _ in id_terms]
        course['terms'] = [term for _, term in id_terms]
    assert data == [
        {
            'ids': [6],
            'instructor': 'Meyerowitz, E / Zinn, K',
            'name': 'Principles of Biology',
            'number': 'Bi 1',
            'terms': [3],
            'units': [4, 0, 5]
        },
        {
            'ids': [7, 8, 9],
            'instructor':
            None,  # 2 are with 'Mendez, J', and 1 with 'Jendez, M'
            'name': 'Experimental Methods in Solar Energy Conversion',
            'number': 'Ch 3x',
            'terms': [1, 2, 3],
            'units': [1, 3, 2]
        },
        {
            'ids': [1],
            'instructor': 'Pinkston, D',
            'name': 'Operating Systems',
            'number': 'CS 124',
            'terms': [1],
            'units': [3, 6, 3]
        },
        {
            'ids': [3],
            'instructor': 'Umans, C',
            'name': 'Decidability and Tractability',
            'number': 'CS 21',
            'terms': [2],
            'units': [3, 0, 6]
        },
        {
            'ids': [5],
            'instructor': 'Vidick, T',
            'name': 'Algorithms',
            'number': 'CS 38',
            'terms': [3],
            'units': [3, 0, 6]
        },
        {
            'ids': [4],
            'instructor': None,
            'name': 'Calculus of One and Several Variables and Linear Algebra',
            'number': 'Ma 1b',
            'terms': [2],
            'units': [4, 0, 5]
        },
        {
            'ids': [2],
            'instructor': 'Cheung, C',
            'name': 'Classical Mechanics and Electromagnetism',
            'number': 'Ph 1a',
            'terms': [1],
            'units': [4, 0, 5]
        }
    ]


def test_scheduler_courses(client):
    # Test nonexistant term
    rv = client.get(
        flask.url_for('courses.scheduler_courses', year=2018, term=2))
    assert rv.status_code == 200
    assert json.loads(rv.data) == []
    # Test actual term
    rv = client.get(
        flask.url_for('courses.scheduler_courses', year=2019, term=2))
    assert rv.status_code == 200
    assert json.loads(rv.data) == [{
        'id':
        8,
        'name':
        'Experimental Methods in Solar Energy Conversion',
        'number':
        'Ch 3x',
        'sections': [{
            'grades': 'PASS-FAIL',
            'instructor': 'Mendez, J',
            'number': 1,
            'times': 'F 09:00 - 09:55\nW 13:00 - 15:55',
            'locations': '147 NYS\n107 MEAD'
        }],
        'units': [1, 3, 2]
    }, {
        'id':
        3,
        'name':
        'Decidability and Tractability',
        'number':
        'CS 21',
        'sections': [{
            'grades': 'LETTER',
            'instructor': 'Umans, C',
            'number': 1,
            'times': 'MWF 13:00 - 13:55',
            'locations': '105 ANB'
        }],
        'units': [3, 0, 6]
    }, {
        'id':
        4,
        'name':
        'Calculus of One and Several Variables and Linear Algebra',
        'number':
        'Ma 1b',
        'sections': [{
            'grades': 'PASS-FAIL',
            'instructor': 'Kechris, A',
            'number': 1,
            'times': 'MWF 10:00 - 10:55\nR 09:00 - 09:55',
            'locations': '119 KRK\n103 DWN'
        }, {
            'grades': 'PASS-FAIL',
            'instructor': 'Kechris, A',
            'number': 2,
            'times': 'MWF 10:00 - 10:55\nR 09:00 - 09:55',
            'locations': '119 KRK\n119 DWN'
        }, {
            'grades': 'PASS-FAIL',
            'instructor': 'Rains, E',
            'number': 7,
            'times': 'MWF 10:00 - 10:55\nR 09:00 - 09:55',
            'locations': '310 LINDE\nB111 DWN'
        }, {
            'grades': 'PASS-FAIL',
            'instructor': 'Rains, E',
            'number': 8,
            'times': 'R 10:00 - 10:55\nMWF 10:00 - 10:55',
            'locations': '142 KCK\n310 LINDE'
        }],
        'units': [4, 0, 5]
    }]


def test_planner_mine(client):
    # Test when not logged in
    rv = client.get(flask.url_for('courses.planner_mine'))
    assert rv.status_code == 200
    assert json.loads(rv.data) == {'courses': [], 'placeholders': []}
    rv = client.get(
        flask.url_for('courses.planner_add_course', course_id=1, year=2))
    assert rv.status_code == 200
    assert json.loads(rv.data) == {
        'success': False,
        'message': 'Must be logged in to save'
    }
    rv = client.get(
        flask.url_for('courses.planner_drop_course', course_id=1, year=2))
    assert rv.status_code == 200
    assert json.loads(rv.data) == {
        'success': False,
        'message': 'Must be logged in to save'
    }
    # Test courses list when no courses have been added
    with client.session_transaction() as sess:
        sess['username'] = 'csander'
    rv = client.get(flask.url_for('courses.planner_mine'))
    assert rv.status_code == 200
    assert json.loads(rv.data) == {'courses': [], 'placeholders': []}
    # Test adding some courses
    rv = client.get(
        flask.url_for('courses.planner_add_course', course_id=1, year=2))
    assert rv.status_code == 200
    assert json.loads(rv.data) == {'success': True}
    rv = client.get(
        flask.url_for('courses.planner_add_course', course_id=5, year=1))
    assert rv.status_code == 200
    assert json.loads(rv.data) == {'success': True}
    rv = client.get(
        flask.url_for('courses.planner_add_course', course_id=6, year=1))
    assert rv.status_code == 200
    assert json.loads(rv.data) == {'success': True}
    # Test adding a duplicate course (should fail)
    rv = client.get(
        flask.url_for('courses.planner_add_course', course_id=1, year=2))
    assert rv.status_code == 200
    assert json.loads(rv.data) == {
        'success': False,
        'message': 'Cannot add a class twice in the same term'
    }
    # Test courses list now that courses have been added; verify order
    rv = client.get(flask.url_for('courses.planner_mine'))
    assert rv.status_code == 200
    assert json.loads(rv.data) == {
        'courses': [{
            'ids': [1],
            'number': 'CS 124',
            'terms': [1],
            'units': 12,
            'year': 2
        }, {
            'ids': [6],
            'number': 'Bi 1',
            'terms': [3],
            'units': 9,
            'year': 1
        }, {
            'ids': [5],
            'number': 'CS 38',
            'terms': [3],
            'units': 9,
            'year': 1
        }],
        'placeholders': []
    }
    # Test dropping a course
    rv = client.get(
        flask.url_for('courses.planner_drop_course', course_id=5, year=1))
    assert rv.status_code == 200
    assert json.loads(rv.data) == {'success': True}
    rv = client.get(flask.url_for('courses.planner_mine'))
    assert rv.status_code == 200
    assert json.loads(rv.data) == {
        'courses': [{
            'ids': [1],
            'number': 'CS 124',
            'terms': [1],
            'units': 12,
            'year': 2
        }, {
            'ids': [6],
            'number': 'Bi 1',
            'terms': [3],
            'units': 9,
            'year': 1
        }],
        'placeholders': []
    }


def test_scheduler_mine(client):
    # Test when not logged in
    rv = client.get(flask.url_for('courses.scheduler_mine', year=2018, term=1))
    assert rv.status_code == 200
    assert json.loads(rv.data) == []
    rv = client.get(
        flask.url_for('courses.scheduler_add_section', course=1, section=1))
    assert rv.status_code == 200
    assert json.loads(rv.data) == {
        'success': False,
        'message': 'Must be logged in to save'
    }
    rv = client.get(
        flask.url_for('courses.scheduler_drop_section', course=1, section=1))
    assert rv.status_code == 200
    assert json.loads(rv.data) == {
        'success': False,
        'message': 'Must be logged in to save'
    }
    # Test sections list when no sections have been added
    with client.session_transaction() as sess:
        sess['username'] = 'csander'
    rv = client.get(flask.url_for('courses.scheduler_mine', year=2018, term=1))
    assert rv.status_code == 200
    assert json.loads(rv.data) == []
    # Test adding some sections
    rv = client.get(
        flask.url_for('courses.scheduler_add_section', course=1, section=1))
    assert rv.status_code == 200
    assert json.loads(rv.data) == {'success': True}
    rv = client.get(
        flask.url_for('courses.scheduler_add_section', course=6, section=2))
    assert rv.status_code == 200
    assert json.loads(rv.data) == {'success': True}
    rv = client.get(
        flask.url_for('courses.scheduler_add_section', course=2, section=3))
    assert rv.status_code == 200
    assert json.loads(rv.data) == {'success': True}
    # Test sections list now that sections have been added
    rv = client.get(flask.url_for('courses.scheduler_mine', year=2018, term=1))
    assert rv.status_code == 200
    assert sorted(
        json.loads(rv.data), key=lambda course: course['id']) == [{
            'id': 1,
            'section': 1
        }, {
            'id': 2,
            'section': 3
        }]
    rv = client.get(flask.url_for('courses.scheduler_mine', year=2018, term=3))
    assert rv.status_code == 200
    assert json.loads(rv.data) == [{'id': 6, 'section': 2}]
    # Test dropping a section
    rv = client.get(
        flask.url_for('courses.scheduler_drop_section', course=1, section=1))
    assert rv.status_code == 200
    assert json.loads(rv.data) == {'success': True}
    rv = client.get(flask.url_for('courses.scheduler_mine', year=2018, term=1))
    assert rv.status_code == 200
    assert json.loads(rv.data) == [{'id': 2, 'section': 3}]
