import flask
import pytest
from werkzeug.datastructures import MultiDict

from donut.modules.name_game import helpers
from donut.testing.fixtures import client

# The house, major, and members used to play a game in a test.
HOUSE_ID = 20
PHYSICS_ID = 20
EE_ID = 21
FIRST_USER_ID = 20
# The image of each of the members added by the people fixture.
IMAGE_BYTES = {20: b'ALPHA', 21: b'BETA', 22: b'GAMMA', 23: b'DELTA'}

SETUP_QUERIES = [
    """
    INSERT INTO options(option_id, option_name) VALUES
        (20, 'Physics'),
        (21, 'EE');
    """,
    """
    INSERT INTO members(user_id, uid, first_name, last_name, preferred_name,
        middle_name, email, graduation_year) VALUES
        (20, '2090001', 'Alice', 'Alpha', NULL, NULL, 'alpha@example.com', 2027),
        (21, '2090002', 'Bob', 'Beta', 'Bobby', 'B', 'beta@example.com', 2028),
        (22, '2090003', 'Cara', 'Gamma', NULL, NULL, 'gamma@example.com', 2029),
        (23, '2090004', 'Dan', 'Delta', NULL, NULL, 'delta@example.com', 2030);
    """,
    """
    INSERT INTO images(user_id, extension, image) VALUES
        (20, 'png', 'ALPHA'),
        (21, 'png', 'BETA'),
        (22, 'png', 'GAMMA'),
        (23, 'png', 'DELTA');
    """,
    """
    INSERT INTO member_options(user_id, option_id, option_type) VALUES
        (20, 20, 'Major'),
        (21, 21, 'Major'),
        (22, 1, 'Major');
    """,
    """
    INSERT INTO groups(group_id, group_name, type) VALUES
        (20, 'Bechtel House', 'house');
    """,
    """
    INSERT INTO positions(group_id, pos_id, pos_name) VALUES
        (20, 20, 'Full Member');
    """,
    """
    INSERT INTO position_holders(pos_id, user_id) VALUES
        (20, 20),
        (3, 21);
    """,
]

# Removes everything that the people fixture adds, and is run both before and
# after the game is played so that the other tests never see it.
CLEANUP_QUERIES = [
    ('DELETE FROM position_holders WHERE pos_id = %s OR user_id >= %s',
     [HOUSE_ID, FIRST_USER_ID]),
    ('DELETE FROM positions WHERE pos_id = %s', [HOUSE_ID]),
    ('DELETE FROM groups WHERE group_id = %s', [HOUSE_ID]),
    ('DELETE FROM member_options WHERE user_id >= %s', [FIRST_USER_ID]),
    ('DELETE FROM images WHERE user_id >= %s', [FIRST_USER_ID]),
    ('DELETE FROM members WHERE user_id >= %s', [FIRST_USER_ID]),
    ('DELETE FROM options WHERE option_id >= %s', [PHYSICS_ID]),
]


@pytest.fixture
def people(client):
    """
    Adds members with images, majors, houses, and class years for the game to
    be played with, and removes them afterwards so that the other tests do not
    see them.
    """
    with flask.g.pymysql_db.cursor() as cursor:
        for query, args in CLEANUP_QUERIES:
            cursor.execute(query, args)
        for query in SETUP_QUERIES:
            cursor.execute(query)

    yield

    with flask.g.pymysql_db.cursor() as cursor:
        for query, args in CLEANUP_QUERIES:
            cursor.execute(query, args)


def start_game(client, **overrides):
    """
    Requests the game with the given query arguments, falling back to the people
    added by the people fixture for the ones that are not given.
    """
    args = {
        'game_mode': helpers.MULTIPLE_CHOICE,
        'min_grad_year': '2027',
        'max_grad_year': '2030'
    }
    args.update(overrides)
    return client.get(flask.url_for('name_game.name_game'), query_string=args)


def test_normalize_name():
    assert helpers.normalize_name('Sander, CALEB') == 'sander caleb'
    assert helpers.normalize_name("  O'Brien  Jr. ") == 'obrien jr'


def test_name_answers():
    # Alice, who has no preferred or middle name
    assert helpers.name_answers({
        'first_name': 'Alice',
        'middle_name': None,
        'last_name': 'Alpha',
        'preferred_name': None
    }) == ['alice alpha', 'alpha alice']
    # Bob, whose preferred name is Bobby and whose middle name is B
    assert helpers.name_answers({
        'first_name': 'Bob',
        'middle_name': 'B',
        'last_name': 'Beta',
        'preferred_name': 'Bobby'
    }) == [
        'beta bob', 'beta bobby', 'bob b beta', 'bob beta', 'bobby b beta',
        'bobby beta'
    ]
    assert helpers.name_answers({
        'first_name': 'Alice',
        'middle_name': None,
        'last_name': None,
        'preferred_name': None
    }) == []


def ids_of(members):
    """
    Returns the user ids of the given members, sorted, since they are looked up
    in random order.
    """
    return sorted(member['user_id'] for member in members)


def test_find_members(client, people):
    assert ids_of(helpers.find_members(2027, 2030, [], [])) == [20, 21, 22, 23]
    assert ids_of(helpers.find_members(2028, 2028, [], [])) == [21]
    # csander has an image, a class year, and a major
    assert ids_of(helpers.find_members(2021, 2030, [], [])) == [
        3, 20, 21, 22, 23
    ]
    # members without an image cannot be shown
    assert 1 not in ids_of(helpers.find_members(1901, 2155, [], []))

    assert ids_of(helpers.find_members(2027, 2030, [HOUSE_ID], [])) == [20]
    assert ids_of(helpers.find_members(2027, 2030, [2], [])) == [21]
    assert ids_of(helpers.find_members(2027, 2030, [], [PHYSICS_ID])) == [20]
    assert ids_of(helpers.find_members(2027, 2030, [], [EE_ID])) == [21]
    assert ids_of(helpers.find_members(2027, 2030, [], [1])) == [22]
    # Alice is in Bechtel House, but her major is not EE
    assert ids_of(helpers.find_members(2027, 2030, [HOUSE_ID], [EE_ID])) == []
    assert helpers.count_people(2027, 2030, [HOUSE_ID], [EE_ID]) == 0

    # Only the people that are played are asked for
    assert len(helpers.find_members(2027, 2030, [], [], 2)) == 2


def test_count_people(client, people):
    assert helpers.count_people(2027, 2030, [], []) == 4
    assert helpers.count_people(2021, 2030, [], []) == 5
    assert helpers.count_people(1901, 2155, [], []) == 5


def test_make_roster(client, people):
    roster = helpers.make_roster(helpers.MULTIPLE_CHOICE, 2027, 2030)
    assert len(roster) == 4
    assert set(person['id'] for person in roster) == {20, 21, 22, 23}
    assert set(person['name'] for person in roster) == {
        'Alice Alpha', 'Bobby Beta', 'Cara Gamma', 'Dan Delta'
    }
    assert set(person['image'] for person in roster) == set(
        flask.url_for('name_game.get_image', user_id=user_id)
        for user_id in (20, 21, 22, 23))
    alice = next(person for person in roster if person['id'] == 20)
    assert alice['answers'] == ['alice alpha', 'alpha alice']

    roster = helpers.make_roster(
        helpers.FREE_RESPONSE, 2027, 2030, num_people=2)
    assert len(roster) == 2

    # A game never has more faces than there are people to show them
    roster = helpers.make_roster(
        helpers.MULTIPLE_CHOICE, 2027, 2030, num_people=1000)
    assert len(roster) == 4

    # The same filters give the faces in a different order every time
    orders = set(
        tuple(person['id']
              for person in helpers.make_roster(helpers.FREE_RESPONSE, 2027,
                                                2030)) for _ in range(5))
    assert len(orders) > 1


def test_make_roster_too_few_people(client, people):
    # Only one person is in Bechtel House, and multiple choice needs four
    with pytest.raises(ValueError):
        helpers.make_roster(helpers.MULTIPLE_CHOICE, 2027, 2030, houses=[20])

    roster = helpers.make_roster(
        helpers.FREE_RESPONSE, 2027, 2030, houses=[20])
    assert len(roster) == 1


def test_get_filters(client):
    assert helpers.get_filters(MultiDict()) is None

    filters = helpers.get_filters(
        MultiDict([('game_mode', 'free_response'), ('min_grad_year', '2027'), (
            'max_grad_year', '2030'), ('house_id', '2'), ('house_id', '20'), (
                'major_id', '1'), ('num_people', '5')]))
    assert filters == {
        'game_mode': 'free_response',
        'min_grad_year': 2027,
        'max_grad_year': 2030,
        'houses': [2, 20],
        'majors': [1],
        'num_people': 5
    }

    # Filters that are not given are not restrictive
    assert helpers.get_filters(
        MultiDict([('min_grad_year', '2027'), ('max_grad_year', '2030')])) == {
            'game_mode': 'multiple_choice',
            'min_grad_year': 2027,
            'max_grad_year': 2030,
            'houses': [],
            'majors': [],
            'num_people': None
        }


for invalid in [
    [('game_mode', 'multiple_choice')],
    [('min_grad_year', '2027')],
    [('game_mode', 'not-a-real-mode'), ('min_grad_year', '2027'),
     ('max_grad_year', '2030')],
    [('min_grad_year', 'not-a-real-year'), ('max_grad_year', '2030')],
    [('min_grad_year', '2027'), ('max_grad_year', 'not-a-real-year')],
    [('min_grad_year', '2027'), ('max_grad_year', '2030'),
     ('house_id', 'not-a-real-house')],
    [('min_grad_year', '2027'), ('max_grad_year', '2030'),
     ('major_id', 'not-a-real-major')],
    [('min_grad_year', '2027'), ('max_grad_year', '2030'),
     ('num_people', 'not-a-real-number')],
    [('min_grad_year', '2027'), ('max_grad_year', '2030'), ('num_people',
                                                            '1000')],
]:
    assert helpers.get_filters(MultiDict(invalid)) is None


def test_name_game_page(client):
    response = client.get(flask.url_for('name_game.name_game'))
    assert response.status_code == 200
    page = response.get_data(as_text=True)
    # The game is set up with a form that only gets
    assert "method='GET'" in page
    assert "type='number'" in page
    assert 'All houses' in page
    assert 'All majors' in page
    assert 'nameGame.play(' not in page


def test_name_game_play_page(client, people):
    response = start_game(client)
    assert response.status_code == 200
    page = response.get_data(as_text=True)
    assert 'nameGame.play(' in page
    assert '"multiple_choice"' in page
    assert 'press 1, 2, 3, or 4' in page
    for person_id in (20, 21, 22, 23):
        assert '/1/name_game/image/%d' % person_id in page


def test_name_game_play_page_free_response(client, people):
    response = start_game(
        client, game_mode=helpers.FREE_RESPONSE, num_people='2')
    assert response.status_code == 200
    page = response.get_data(as_text=True)
    assert '"free_response"' in page
    assert 'any capitalization' in page


def test_name_game_play_page_not_enough_people(client, people):
    response = start_game(client, house_id=HOUSE_ID)
    assert response.status_code == 302
    assert response.headers['location'] == flask.url_for('name_game.name_game')

    # Filters that make no sense show the setup form again
    for query_string in ({
            'game_mode': 'multiple_choice'
    }, {
            'game_mode': 'not-a-real-mode'
    }):
        response = client.get(
            flask.url_for('name_game.name_game'), query_string=query_string)
        assert response.status_code == 200
        assert 'nameGame.play(' not in response.get_data(as_text=True)


def test_name_game_needs_a_login(client, people):
    off_campus = {'environ_base': {'REMOTE_ADDR': '8.8.8.8'}}

    # On the Caltech internet, no login is needed
    assert client.get(flask.url_for('name_game.name_game')).status_code == 200

    # Off campus, the game is for people who are logged in
    response = client.get(flask.url_for('name_game.name_game'), **off_campus)
    assert response.status_code == 302
    assert response.headers['location'] == flask.url_for('auth.login')
    assert client.get(
        flask.url_for('name_game.get_image', user_id=20),
        **off_campus).status_code == 401

    with client.session_transaction() as sess:
        sess['username'] = 'csander'
    assert client.get(flask.url_for('name_game.name_game'),
                      **off_campus).status_code == 200
    assert client.get(
        flask.url_for('name_game.get_image', user_id=20),
        **off_campus).status_code == 200


def test_name_game_image(client, people):
    response = client.get(flask.url_for('name_game.get_image', user_id=20))
    assert response.status_code == 200
    assert response.headers['Content-Type'] == 'image/png'
    assert response.data == IMAGE_BYTES[20]
