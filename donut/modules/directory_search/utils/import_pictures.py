#!/usr/bin/env python
"""
Imports ID pictures for new undergrads from the card office.
The pictures are given in a zip file.
"""

import argparse
from zipfile import ZipFile

from donut.pymysql_connection import make_db

EXTENSIONS = {
    'jpg': 'jpg',
    'jpeg': 'jpg',
    'png': 'png'
}
GET_USER_ID_QUERY = 'SELECT user_id FROM members WHERE uid = %s'
INSERT_QUERY = """
    INSERT INTO images (user_id, extension, image) VALUES (%s, %s, %s)
    ON DUPLICATE KEY UPDATE image = VALUES(image)
"""


def import_zip(env, file):
    db = make_db(env)
    try:
        db.begin()
        with db.cursor() as cursor:
            with ZipFile(file) as images_zip:
                import_images(cursor, images_zip)
        db.commit()
    finally:
        db.close()


def import_images(cursor, images_zip):
    for info in images_zip.infolist():
        if info.is_dir():
            continue

        path = info.filename
        _, file = path.rsplit('/', 1)
        uid, extension = file.rsplit('.', 1)
        new_extension = EXTENSIONS.get(extension.lower())
        if new_extension is None:
            raise Exception('Unknown file extension: ' + extension)
        cursor.execute(GET_USER_ID_QUERY, int(uid))
        user = cursor.fetchone()
        if user is None:
            raise Exception('Unknown UID: ' + uid)

        with images_zip.open(path) as image_file:
            image = image_file.read()
        cursor.execute(INSERT_QUERY, (user['user_id'], new_extension, image))
        print('Inserted image for UID', uid)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(
        description='Imports a zip file of ID photos from the card office')
    parser.add_argument(
        '-e', '--env', default='dev', help='Database to update (default dev)')
    parser.add_argument(
        'file', help='Path to zip file of images, e.g. ug_photos.zip')
    args = parser.parse_args()

    import_zip(args.env, args.file)
