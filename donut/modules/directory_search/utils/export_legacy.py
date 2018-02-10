"""Exports directory tables from donut-legacy as CSV files"""
import os
from sys import argv

TABLES = [
    'campus_buildings', 'directory_addresses', 'directory_campus_addresses',
    'directory_phones', 'hovse_members', 'hovses', 'hovse_membership_types',
    'images', 'image_inums', 'inums', 'people', 'position_holders',
    'position_organizations', 'position_titles', 'undergrad_options',
    'undergrad_option_objectives', 'undergrads', 'groups', 'group_members_src'
]

db_password = argv[1]

for table in TABLES:
    print('Exporting ' + table)
    os.system("""
        export PGPASSWORD='""" + db_password + """'
        echo "COPY """ + table +
              """ TO STDOUT DELIMITER ',' CSV HEADER;" | psql ascit devel > """
              + table + '.csv')
