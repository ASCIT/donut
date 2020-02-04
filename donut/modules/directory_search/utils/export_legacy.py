#!/usr/bin/env python
"""
Exports directory tables from donut-legacy as CSV files
and images as a zip file
"""
import argparse
import os

TABLES = ('campus_buildings', 'directory_addresses',
          'directory_campus_addresses', 'directory_phones', 'hovse_members',
          'hovses', 'hovse_membership_types', 'images', 'image_inums', 'inums',
          'people', 'position_holders', 'position_organizations',
          'position_titles', 'undergrad_options',
          'undergrad_option_objectives', 'undergrads', 'groups',
          'group_members_src')


def export_tables(args):
    for table in TABLES:
        print('Exporting ' + table)
        os.system(
            'echo "COPY ' + table + " TO STDOUT DELIMITER ',' CSV HEADER;\" | PGPASSWORD='" + \
            args.db_password + "' psql " + args.db + ' ' + args.user + ' > ' + table + '.csv')


def export_images():
    print('Exporting directory images')
    os.system('zip -r9 images /home/demo/www/id_photo > /dev/null')


if __name__ == '__main__':
    parser = argparse.ArgumentParser(
        description='Exports tables and images from the legacy database')
    parser.add_argument('-d', '--db', default='ascit', help='Database name')
    parser.add_argument('-u', '--user', default='devel', help='Database user')
    parser.add_argument('db_password', help='Database password')
    args = parser.parse_args()

    export_tables(args)
    export_images()
