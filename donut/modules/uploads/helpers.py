import flask
import os


def readPage(url):
    root = uploads = os.path.join(flask.current_app.root_path,
                               flask.current_app.config['UPLOAD_FOLDER'])
    path = os.path.join(root + "/static", url + '.md')
    content = ''
    with open(path, 'r') as f:
        content += f.read()
    return content
