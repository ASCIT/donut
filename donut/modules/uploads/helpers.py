import flask
import os
from flask import current_app
import glob


def readPage(url):
    root = os.path.join(current_app.root_path,
                        current_app.config["UPLOAD_WEBPAGES"])
    path = os.path.join(root, url + '.md')
    content = ''
    with open(path, 'r') as f:
        content += f.read()
    return content


ALLOWED_EXTENSIONS = set(['txt', 'pdf', 'png', 'jpg', 'jpeg', 'gif'])


def allowed_file(filename):
    '''
    Checks for allowed file extensions.
    '''
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


def get_links():
    path = os.path.join(flask.current_app.root_path,
                        flask.current_app.config['UPLOAD_FOLDER'])
    links = glob.glob(path + '/*')
    matches = (x for x in links if 'pages' in x or 'static' in x)

    dele = ['', '']
    counter = 0
    for i in links:
        if 'pages' in i or 'static' in i:
            dele[counter] = i
            counter += 1
    links.remove(dele[0])
    links.remove(dele[1])
    for i in range(len(links)):
        links[i] = links[i].replace(path + '/', '')
        links[i] = (flask.url_for('uploads.uploaded_file', filename=links[i]),
                    links[i])
    return links
