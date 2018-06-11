import flask
import os
from flask import current_app
import glob


def read_page(url):
    root = os.path.join(current_app.root_path,
                        current_app.config["UPLOAD_WEBPAGES"])
    path = os.path.join(root, url + '.md')
    with open(path, 'r') as f:
        return f.read()


ALLOWED_EXTENSIONS = set(['txt', 'pdf', 'png', 'jpg', 'jpeg', 'gif'])


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
    for i in links:
        if filename in i:
            os.remove(i)


def get_links():
    '''
    Get links for all uploaded files
    '''
    path = os.path.join(flask.current_app.root_path,
                        flask.current_app.config['UPLOAD_FOLDER'])
    links = glob.glob(path + '/*')

    processed_links = []
    for i in range(len(links)):
        filename = os.path.basename(links[i])
        if filename != 'static' and filename != 'pages' and filename != '':
            processed_links.append((flask.url_for(
                'uploads.uploaded_file', filename=filename), filename))
    return processed_links