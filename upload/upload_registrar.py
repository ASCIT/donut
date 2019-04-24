#!usr/bin/env python


'''
Registrar student data upload script.

Args:
    filename: registrar provided file of new students
    database: select "dev" or "prod" database
    -v: increase output verbosity

Written by Michael Huynh
July 05, 2017
'''


import argparse, csv, collections
from datetime import date

from donut.pymysql_connection import make_db
from donut.constants import (registrar_gender, registrar_month,
    registrar_column_labels)


def parse_args():
    '''
    Set up the argument parser and parse all input arguments.
    '''
    parser = argparse.ArgumentParser()
    parser.add_argument('filename',
        help='registrar provided file of new students')
    parser.add_argument('database', choices=['test', 'dev', 'prod'],
        help='select dev or prod database')
    parser.add_argument('-v', '--verbose',
        help='increase verbosity of script output', action='store_true')
    args = parser.parse_args()
    return args


def parse_file(filename, verbose = False):
    '''
    Parse the file and return an array of member dictionaries.
    '''
    with open(filename) as registrar_file:
        print("Loaded file \"{}\"".format(args.filename))

        reader = csv.DictReader(registrar_file, delimiter='\t', quotechar='\"')
        parsed_data = list(reader)

        print("Loaded and parsed {} students.".format(len(parsed_data)))

        return parsed_data


def to_lowercase(input):
    return collections.OrderedDict({
        k.lower(): v for k, v in input.items()
    })


def rename_columns(mapping):
    def rename(input):
        output = input.copy()

        for k, v in mapping.items():
            del output[k]
            output[v] = input[k]

        return output
    return rename


def expand_gender(gender_convert):
    '''

    '''
    def expand(input):
        output = input.copy()

        output['gender'] = gender_convert[output['gender']]

        return output
    return expand


def parse_birthday(month_convert):
    '''
    Normalizes `birthday` into a standard Python `date` object.
    '''
    def parse(input):
        output = input.copy()

        birthday = output['birthday'].split('-')

        output['birthday'] = date(
            int(birthday[2]),
            month_convert[birthday[1]],
            int(birthday[0]))

        return output
    return parse


def parse_msc(input):
    '''
    Splits MSC by whitespace and takes the numerical part as an `int`.
    '''
    output = input.copy()

    msc = output['msc'].split(' ')

    output['msc'] = int(msc[1])

    return output


def combine_address(address_columns):
    '''
    Closure that returns a higher-order function that given a list of address
    columns, will combine all values in those columns into the column `address`
    and deletes the columns in `address_columns`.
    '''
    def combine(input):
        output = input.copy()

        output['address'] = ' '.join([
            input[l] for l in address_columns if input[l] != ''
        ])
        for l in address_columns:
            del output[l]

        return output
    return combine


def apply_transforms(data, *transforms):
    '''
    Takes any list of higher-order function arguments that should each have the
    form `OrderedDict` -> `OrderedDict` to transform and normalize the given
    registrar data.
    '''
    transformed_data = []
    for row in data:
        transformed_row = row
        for transform in transforms:
            transformed_row = transform(transformed_row)
        transformed_data.append(transformed_row)
    return transformed_data


def upload_to_members_table(col_names, member_data, database, verbose = False):
    '''
    Establish a connection to the desired database and upload student data to
    it. Data is an array of member objects, where each member object is a
    member parsed from the registrar file.
    '''

    sql = (
        'INSERT INTO `members` ({}) VALUES ({}) '
        'ON DUPLICATE KEY UPDATE {}'
    ).format(
        ', '.join(['{}'.format(col) for col in col_names]),
        ', '.join(['%s' for _ in col_names]),
        ', '.join(['{}=%s'.format(col) for col in col_names])
    )

    print('Connecting to \"{}\" database.'.format(database))

    db_conn = make_db(database)

    print('Connected. Staging changes...')

    try:
        with db_conn.cursor() as cursor:
            for member in member_data:
                mogrified_sql = cursor.mogrify(sql,
                    [member[col] if col in member else None for col in col_names] * 2)
                if verbose:
                    print(mogrified_sql)
                cursor.execute(mogrified_sql)

            do_commit = input('Staged uploading {} members. Commit changes? [y/n] '
                .format(len(member_data)))
            while not (do_commit == 'y' or do_commit == 'n'):
                print('Unrecognized command {}.'.format(do_commit))
                do_commit = input('Staged uploading {} members. Commit changes? [y/n] '
                    .format(len(member_data)))
            if do_commit == 'y':
                print('Comitting...')
                db_conn.commit()
            else:
                print('Rolling back all server changes...')
                db_conn.rollback()
    except Exception as e:
        print(e)
        print('Rolling back all server changes...')
        db_conn.rollback()
    finally:
        print('Disconnecting from server.')

        db_conn.close()


def upload_to_position_holders_table():
    # TODO
    # This function should update the appropriate values in the
    # `position_holders` table to signify house membership data from the
    # registrar.
    pass


def upload_to_member_options():
    # TODO
    # This function should update the appropriate values in the
    # `member_options` table to signify majors and minors from the registrar
    # data.
    pass


if __name__ == '__main__':
    args = parse_args()
    try:
        parsed_data = parse_file(args.filename, args.verbose)
        transformed_data = apply_transforms(
            parsed_data,
            to_lowercase,
            rename_columns({
                'birth_date': 'birthday',
                'phone_number': 'phone',
                'nick_name': 'preferred_name',
            }),
            expand_gender(registrar_gender),
            parse_birthday(registrar_month),
            parse_msc,
            combine_address([
                'line1',
                'line2',
                'line3',
            ]))

        # Perform insertion into the base `members` table
        upload_to_members_table(
            registrar_column_labels,
            transformed_data,
            args.database,
            args.verbose)

        # Perform insertion into the `position_holders` table for House
        # affiliations
        upload_to_position_holders_table()

        # Perform insertion into the `member_options` table for Options
        upload_to_member_options_table()

        print('Done.')
    except FileNotFoundError:
        print('Cannot open file \"{}\"'.format(args.filename))
