import flask
import os
import glob
from donut.modules.uploads.upload_permission import UploadPermissions
from donut.auth_utils import check_permission, check_login
from donut.modules.editor import helpers as editor_helpers

ALLOWED_EXTENSIONS = set(
    ['docx', 'doc', 'txt', 'pdf', 'png', 'jpg', 'jpeg', 'gif'])

# 10 MB
MAX_FILE_SIZE = 10 * 1024 * 1024


def read_page(url):
    return editor_helpers.read_markdown(url)


def allowed_file(filename):
    '''
    Checks for allowed file extensions.
    '''
    splits = filename.rsplit('.', 1)
    return len(splits) >= 2 and splits[1].lower() in ALLOWED_EXTENSIONS


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
            os.remove(link)
            break


def check_valid_file(file):
    '''
    Checks if the file: exists, has a valid extension, and
    smaller than 10 mb
    '''
    file.seek(0, os.SEEK_END)
    file_length = file.tell()
    if file_length > MAX_FILE_SIZE:
        return "File size larger than 10 mb"
    if not allowed_file(file.filename):
        return "Invalid file name"
    path = os.path.join(flask.current_app.root_path,
                        flask.current_app.config['UPLOAD_FOLDER'])
    links = glob.glob(path + '/*')
    filename = file.filename.replace(' ', '_')
    filename = os.path.basename(filename)
    for link in links:
        cur_filename = os.path.basename(link)
        if cur_filename == filename:
            return 'Duplicate title'
    return ''


def check_upload_permission():
    """
    Checks if the user has upload permissions
    """
    return check_login() and check_permission(flask.session['username'],
                                              UploadPermissions.ABLE)


def get_links():
    '''
    Get links for all uploaded files
    '''
    path = os.path.join(flask.current_app.root_path,
                        flask.current_app.config['UPLOAD_FOLDER'])
    links = glob.glob(path + '/*')

    processed_links = {}
    for link in links:
        filename = os.path.basename(link)
        if '.' in filename:
            processed_links[filename] = flask.url_for(
                'uploads.uploaded_file', filename=filename)
    return processed_links
