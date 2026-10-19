"""
Helpers for the name game, a memorization game about the faces and names of
the people in the directory.

The game is given to the player one face at a time. In multiple choice mode
the player picks one of four names, in free response mode the player types the
name of the face.

The game is not stored anywhere. Choosing the filters picks a random roster of
people, which is handed to the browser along with the names that are accepted
as an answer for each of them, and the browser plays the game with that. The
whole roster is looked up in one query, and only the people who are played are
sent to the browser, so that playing a game does not depend on how many people
match the filters.
"""

from datetime import date
import random
import re

import flask

from donut.modules.directory_search import helpers as directory_helpers
from donut.validation_utils import validate_int

# Maximum number of faces in a single game.
MAX_PEOPLE = 50
# Number of names shown in multiple choice mode.
NUM_CHOICES = 4

MULTIPLE_CHOICE = 'multiple_choice'
FREE_RESPONSE = 'free_response'
GAME_MODES = (MULTIPLE_CHOICE, FREE_RESPONSE)
# Names of the game modes, for the setup form.
GAME_MODE_NAMES = {
    MULTIPLE_CHOICE: 'Multiple choice',
    FREE_RESPONSE: 'Free response'
}

# Everything the game needs to show a person: the name that the directory
# displays, and the names it goes by. Only people with an image in the
# directory can be played, so the images are joined in.
MEMBERS_SELECT = """
    SELECT user_id, full_name, first_name, middle_name, last_name,
        preferred_name
    FROM members
        NATURAL JOIN members_full_name
        NATURAL JOIN images
"""


def placeholders(count):
    """Returns a comma separated list of count SQL placeholders."""
    return ', '.join(['%s'] * count)


def get_houses():
    """Returns the houses that a game can be restricted to."""
    return directory_helpers.get_houses()


def get_majors():
    """Returns the majors that a game can be restricted to."""
    query = """
        SELECT option_id, option_name
        FROM options
        WHERE option_id IN (
            SELECT option_id FROM member_options WHERE option_type = 'Major'
        )
        ORDER BY option_name
    """
    with flask.g.pymysql_db.cursor() as cursor:
        cursor.execute(query)
        return cursor.fetchall()


def get_default_grad_years():
    """
    Returns the (min, max) class years offered by default on the setup form,
    which is the range of the class years of the current undergraduates.
    """
    this_year = date.today().year
    return (this_year + 1, this_year + 4)


def people_matching(min_grad_year, max_grad_year, houses=(), majors=()):
    """
    Returns the condition that selects the people who match the given filters,
    and the arguments to substitute into it. Their class year is between
    min_grad_year and max_grad_year inclusive, they are a member of one of the
    houses if any are given, and they are pursuing one of the majors if any are
    given.
    """
    condition = 'graduation_year >= %s AND graduation_year <= %s'
    args = [min_grad_year, max_grad_year]
    if houses:
        condition += """
            AND user_id IN (
                SELECT user_id
                FROM house_positions NATURAL JOIN current_position_holders
                WHERE group_id IN (%s)
            )
        """ % placeholders(len(houses))
        args += houses
    if majors:
        condition += """
            AND user_id IN (
                SELECT user_id FROM member_options
                WHERE option_type = 'Major' AND option_id IN (%s)
            )
        """ % placeholders(len(majors))
        args += majors
    return condition, args


def count_people(min_grad_year, max_grad_year, houses=(), majors=()):
    """
    Returns how many people match the given filters. This is only needed to
    explain why a game cannot be played, so it is not part of finding the
    people to play.
    """
    condition, args = people_matching(min_grad_year, max_grad_year, houses,
                                      majors)
    query = 'SELECT COUNT(*) AS cnt FROM (' + MEMBERS_SELECT + ' WHERE ' + \
        condition + ') AS matching_people'
    with flask.g.pymysql_db.cursor() as cursor:
        cursor.execute(query, args)
        return cursor.fetchone()['cnt']


def find_members(min_grad_year,
                 max_grad_year,
                 houses=(),
                 majors=(),
                 limit=None):
    """
    Returns up to limit of the people matching the given filters, in random
    order, with everything the game needs to show them. The random order is
    asked of the database, so that only the people who are played are read.
    """
    condition, args = people_matching(min_grad_year, max_grad_year, houses,
                                      majors)
    query = MEMBERS_SELECT + ' WHERE ' + condition + ' ORDER BY RAND()'
    if limit is not None:
        query += ' LIMIT %s'
        args.append(limit)
    with flask.g.pymysql_db.cursor() as cursor:
        cursor.execute(query, args)
        return cursor.fetchall()


def normalize_name(name):
    """
    Returns the given name in a form that can be compared case insensitively:
    lowercased, with punctuation and extra whitespace removed. The browser does
    the same to the name that is typed in, see name_game.js.
    """
    name = re.sub(r"[.,'’]", '', name.lower())
    return ' '.join(name.split())


def name_answers(member):
    """
    Returns the sorted names that are accepted as the correct free response
    answer for the given member, which is a row of MEMBERS_SELECT. The full
    name is the name displayed in the directory, which uses the preferred name
    if the member has one, but the legal name is accepted as well.
    """
    last_name = member['last_name']
    if not last_name:
        return []
    answers = set()
    for first_name in (member['first_name'], member['preferred_name']):
        if not first_name:
            continue
        answers.add(first_name + ' ' + last_name)
        answers.add(last_name + ' ' + first_name)
        answers.add(last_name + ', ' + first_name)
        if member['middle_name']:
            answers.add(
                ' '.join([first_name, member['middle_name'], last_name]))
    return sorted(set(normalize_name(answer) for answer in answers))


def parse_id_list(args, name):
    """
    Returns the list of ids among the given values, or None if any of them is
    not a valid id. The empty value selects everything, so it is skipped.
    """
    values = []
    for value in args.getlist(name):
        if value == '':
            continue
        if not validate_int(value, min=1, flash_errors=False):
            return None
        values.append(int(value))
    return values


def get_filters(args):
    """
    Returns the game settings in the given query arguments as a dictionary of
    the arguments taken by make_roster, or None if they are not valid. The
    filters are absent when the setup form has not been submitted yet.
    """
    if not args:
        return None

    game_mode = args.get('game_mode', MULTIPLE_CHOICE)
    if game_mode not in GAME_MODES:
        return None
    min_grad_year = args.get('min_grad_year')
    max_grad_year = args.get('max_grad_year')
    if min_grad_year is None or not validate_int(
            min_grad_year, min=1901, max=2155, flash_errors=False):
        return None
    if max_grad_year is None or not validate_int(
            max_grad_year, min=1901, max=2155, flash_errors=False):
        return None
    houses = parse_id_list(args, 'house_id')
    majors = parse_id_list(args, 'major_id')
    if houses is None or majors is None:
        return None
    num_people = args.get('num_people')
    if num_people and not validate_int(
            num_people, min=1, max=MAX_PEOPLE, flash_errors=False):
        return None

    return {
        'game_mode': game_mode,
        'min_grad_year': int(min_grad_year),
        'max_grad_year': int(max_grad_year),
        'houses': houses,
        'majors': majors,
        'num_people': int(num_people) if num_people else None
    }


def make_roster(game_mode,
                min_grad_year,
                max_grad_year,
                houses=(),
                majors=(),
                num_people=None):
    """
    Returns the people to play a game with: a random selection of the people
    matching the given filters. Every person in the roster is given the name
    that the directory displays, the names that are accepted as a free response
    answer for them, and the url of their image. At most MAX_PEOPLE people are
    returned, or num_people of them if that is fewer. Raises a ValueError with
    a message for the user if the filters do not leave enough people to play
    with.
    """
    minimum = NUM_CHOICES if game_mode == MULTIPLE_CHOICE else 1
    limit = min(num_people, MAX_PEOPLE) if num_people else MAX_PEOPLE
    members = find_members(min_grad_year, max_grad_year, houses, majors, limit)
    if len(members) < minimum:
        raise ValueError(
            'Only {0} people match your filters, but the game needs at least '
            '{1}. Try loosening the class years, houses, or majors.'.format(
                count_people(min_grad_year, max_grad_year, houses, majors),
                minimum))

    return [{
        'id':
        member['user_id'],
        'name':
        member['full_name'],
        'answers':
        name_answers(member),
        'image':
        flask.url_for('name_game.get_image', user_id=member['user_id'])
    } for member in members]
