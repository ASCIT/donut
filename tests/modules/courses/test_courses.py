"""
Tests donut/modules/courses
"""
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
            'times': '147 NYS\n107 MEAD'
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
            'times': 'MWF 13:00 - 13:55'
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
            'number': section,
            'times': 'MWF 10:00 - 10:55\nR 09:00 - 09:55'
        } for section in (1,
                          2)] + [{
                              'grades': 'PASS-FAIL',
                              'instructor': 'Rains, E',
                              'number': 7,
                              'times': 'MWF 10:00 - 10:55\nR 09:00 - 09:55'
                          }, {
                              'grades': 'PASS-FAIL',
                              'instructor': 'Rains, E',
                              'number': 8,
                              'times': 'R 10:00 - 10:55\nMWF 10:00 - 10:55'
                          }],
        'units': [4, 0, 5]
    }]


def test_planner_mine(client):
    # Test when not logged in
    rv = client.get(flask.url_for('courses.planner_mine'))
    assert rv.status_code == 200
    assert json.loads(rv.data) == []
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
    assert json.loads(rv.data) == []
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
        'message': 'Cannot schedule class twice in a term'
    }
    # Test courses list now that courses have been added; verify order
    rv = client.get(flask.url_for('courses.planner_mine'))
    assert rv.status_code == 200
    assert json.loads(rv.data) == [{
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
    }]
    # Test dropping a course
    rv = client.get(
        flask.url_for('courses.planner_drop_course', course_id=5, year=1))
    assert rv.status_code == 200
    assert json.loads(rv.data) == {'success': True}
    rv = client.get(flask.url_for('courses.planner_mine'))
    assert rv.status_code == 200
    assert json.loads(rv.data) == [{
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
    }]


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
