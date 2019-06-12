"""
Tests donut/modules/editor/
"""

from datetime import date
import flask
import pytest
from donut.testing.fixtures import client
from donut import app
import donut.modules.core.helpers as core_helpers
from donut.modules.calendar import helpers
from donut.modules.calendar import routes
import os


def test_plain_calendar_page(client):
    assert client.get(flask.url_for('calendar.add_events')).status_code == 200
    rv = client.get(flask.url_for('calendar.calendar'))
    assert b'Please log in to share to your calendar' in rv.data
    assert rv.status_code == 200
    assert client.get(flask.url_for('calendar.sync')).status_code == 200
    assert client.post(
        flask.url_for('calendar.get_all_events')).status_code == 200
    assert client.post(
        flask.url_for('calendar.get_all_events_backup')).status_code == 200
    assert client.post(
        flask.url_for('calendar.get_events_backup'),
        data=dict(year=2019)).status_code == 200
    assert client.post(
        flask.url_for('calendar.get_events'),
        data=dict(year=2019)).status_code == 200
    assert client.post(
        flask.url_for('calendar.calendar_share_cal')).status_code == 302
    assert client.post(
        flask.url_for('calendar.calendar_add_events',
                      update=0)).status_code == 302


def test_data_handling(client):

    #perms = helpers.get_permission()
    #assert not perms['Any']
    with client.session_transaction() as sess:
        # Should be able to do everything
        sess['username'] = 'dqu'
    with app.test_request_context():
        flask.session['username'] = 'dqu'
        assert helpers.get_permission() == {
            'Avery': True,
            'Blacker': True,
            'Dabney': True,
            'Fleming': True,
            'Lloyd': True,
            'Page': True,
            'Ricketts': True,
            'Ruddock': True,
            'Other': True,
            'Athletics': True,
            'Any': True
        }
        all_events = helpers.sync_data(all_data=True)
        assert all_events != []

        db_all_events = helpers.get_events_backup(all_data=True)
        for i in db_all_events:
            assert any(i['id'] == vals['id'] for vals in all_events)

        the_first_events = helpers.get_events(11, 1111, 11, 1111)
        # In case some misguided soul or sadistic person decides to modify things in year 1111....
        ori_num = len(the_first_events)
        update_name = '我要放飞自我 la la la'

        db_events = helpers.get_events_backup(11, 1111, 11, 1111)

        assert len(db_events) == ori_num

        for i in db_events:
            assert any(i['id'] == vals['id'] for vals in the_first_events)

        # Testing insert
        name = 'this is the very first event find me and my art on inst @wingfril'
        description = 'This could be blank。 but i think that having some info is nice hahahahahhh'
        start_time = '1111-11-23T23:33:33Z'
        end_time = '1111-11-24T23:33:33Z'
        helpers.add_event(name, description, ['Avery'], start_time, end_time,
                          0)
        modded_events = helpers.get_events(11, 1111, 11, 1111)
        assert len(modded_events) == ori_num + 1

        for i in modded_events:
            if i['summary'] == name and i['description'] == description:
                the_first_event = i
        assert the_first_event

        # Testing updates
        update_name = '我要放飞自我 la la la'
        update_description = '''The Heavy Task of Reducing Air Pollution from Heavy-Duty Diesel
A Discussion with Dr. Francisco Dóñez, U.S. Environmental Protection Agency
This Thursday | May 30th | 12:00 to 1:30 pm (with a break at 12:50 for those with 1 pm commitments)
BBB B180 | Lunch Provided | Please RSVP Wednesday: https://forms.gle/UdeiV4oftb89eikk8 

Join us for a discussion with Dr. Francisco Dóñez, from the Air and Radiation Division at the U.S. Environmental Protection Agency (EPA) Pacific Southwest Regional Office (Region 9), who will speak about the EPA’s work to reduce air pollution from heavy-duty vehicles and equipment, particularly in the freight movement sector.  It is an effort crucial to air quality in southern California and an urgent environmental justice issue in numerous communities.  He will also discuss the intersecting issues of health, technology, policy and justice surrounding this work.

Dr. Dóñez leads the Ports and Railroad sector workgroups for the West Coast Collaborative, a public-private partnership to reduce air pollution form heavy-duty diesel engines.  He has championed environmental justice, diversity and equity perspectives within EPA and other organizations.  

Dr. Dóñez spent his early career at EPA headquarters in Washington, DC, where he performed economic analysis of environmental regulations, and coordinated climate change policy and research collaborations with the Mexican government.  Dr. Dóñez earned a Ph.D in Energy and Resources from UC Berkeley, an M.S. In public policy from Georgia Tech, and an S.B. in mechanical engineering from MIT.

Programs introduce one perspective in order to stimulate thought and to provide a forum for respectful dialogue and examination.  The views expressed by speakers are solely those of the speakers.  Presentations do not necessarily reflect the opinion of the California Institute of Technology or the Caltech Y and should not be taken as an endorsement of the ideas, speakers or groups.i\'m writing this at 2am. i have too much time'''
        helpers.add_event(
            update_name,
            update_description, [the_first_event['organizer']['displayName']],
            the_first_event['start']['dateTime'],
            the_first_event['end']['dateTime'],
            1,
            event_id=the_first_event['id'])

        modded_events = helpers.get_events(11, 1111, 11, 1111)

        assert len(modded_events) == ori_num + 1
        for i in modded_events:
            if i['summary'] == update_name and i['description'] == update_description:
                deleted = helpers.delete(i['id'],
                                         i['organizer']['displayName'])

        modded_events = helpers.get_events(11, 1111, 11, 1111)
        assert len(modded_events) == ori_num

        db_events = helpers.get_events_backup(11, 1111, 11, 1111)
        assert ori_num == len(db_events)
