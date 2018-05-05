import flask
import os
from flask import current_app


def readPage(url):
    root = os.path.join(current_app.root_path, current_app.config["UPLOAD_FOLDER"])
    path = os.path.join(root, 'pages', url + '.md')
    content = ''
    with open(path, 'r') as f:
        content += f.read()
    return content
