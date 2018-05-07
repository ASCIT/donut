import flask
import os
from flask import current_app


def readPage(url):
    root = os.path.join(current_app.root_path, current_app.config["UPLOAD_WEBPAGES"])
    path = os.path.join(root, url + '.md')
    content = ''
    with open(path, 'r') as f:
        content += f.read()
    return content
