import flask
import os

def readPage(url):
    root = flask.current_app.config["UPLOAD_FOLDER"]
    path = os.path.join(root, url+'.md')
    content = ''
    with open(path, 'r') as f:
            content += f.read()
    f.close()
    return content
