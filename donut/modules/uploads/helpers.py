import flask
import os
from flask import current_app
import glob
import time

ALLOWED_EXTENSIONS = set(
    ['docx', 'doc', 'txt', 'pdf', 'png', 'jpg', 'jpeg', 'gif'])


def read_page(url):
    root = os.path.join(current_app.root_path,
                        current_app.config["UPLOAD_WEBPAGES"])
    path = os.path.join(root, url + '.md')
    if os.path.isfile(path):
        with open(path, 'r') as f:
            return f.read()
    else:
        return -1


def allowed_file(filename):
    '''
    Checks for allowed file extensions.
    '''
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


def remove_link(filename):
    '''
    Get rid of matching filenames
    '''
    path = os.path.join(flask.current_app.root_path,
                        flask.current_app.config['UPLOAD_FOLDER'])
    links = glob.glob(path + '/*')
    for link in links:
        name = link.replace(path + '/', '')
        if filename == name:
            print(os.remove(link))
            time.sleep(1)


def check_valid_file(file):
    '''
    Checks if the file: exists, has a valid extension, and
    smaller than 10 mb
    '''
    file.seek(0, os.SEEK_END)
    file_length = file.tell()
    if file_length > 10 * 1024 * 1024:
        return "File size larger than 10 mb"
    if not allowed_file(file.filename):
        return "Invalid file name"
    path = os.path.join(flask.current_app.root_path,
                        flask.current_app.config['UPLOAD_FOLDER'])
    links = glob.glob(path + '/*')
    filename = file.filename.replace(' ', '_')
    for link in links:
        cur_filename = os.path.basename(link)
        if cur_filename == filename:
            return 'Duplicate title'
    return ''


def get_links():
    '''
    Get links for all uploaded files
    '''
    path = os.path.join(flask.current_app.root_path,
                        flask.current_app.config['UPLOAD_FOLDER'])
    links = glob.glob(path + '/*')

    processed_links = []
    for link in links:
        filename = os.path.basename(link)
        if filename != 'static' and filename != 'pages' and filename != '':
            processed_links.append((flask.url_for(
                'uploads.uploaded_file', filename=filename), filename))
    return processed_links
