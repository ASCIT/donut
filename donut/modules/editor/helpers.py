import flask
import os
import glob
from flask import current_app, redirect, url_for


def rename_title(oldfilename, newfilename):
    """
    Changes the file name of an html file
    Need to look for paths
    """
    oldpath = os.path.join(current_app.root_path,
                           current_app.config["UPLOAD_WEBPAGES"],
                           oldfilename + '.md')
    newpath = os.path.join(current_app.root_path,
                           current_app.config["UPLOAD_WEBPAGES"],
                           newfilename + '.md')
    os.rename(oldpath, newpath)


def read_markdown(name):
    '''
    Reads in the mark down text from a file.
    '''

    path = os.path.join(flask.current_app.root_path,
                        flask.current_app.config['UPLOAD_WEBPAGES'])
    curFile = read_file(os.path.join(path, name + '.md'))
    return curFile


def read_file(path):
    '''
    Reads in a file
    '''
    curFile = ''
    if os.path.isfile(path):
        with open(path) as f:
            return f.read()
    else:
        return ""


def get_links():
    '''
    Get links for all created webpages
    '''
    root = os.path.join(current_app.root_path,
                        current_app.config["UPLOAD_WEBPAGES"])
    links = glob.glob(root + '/*')
    results = []
    for filenames in links:
        filenames = filenames.replace(root + '/',
                                      '').replace('.md', '').replace('_', ' ')
        link = flask.url_for('uploads.display', url=filenames)
        results.append((link, filenames))
    return results


def remove_link(filename):
    '''
    Get rid of matching filenames
    '''
    path = os.path.join(flask.current_app.root_path,
                        flask.current_app.config['UPLOAD_WEBPAGES'])
    links = glob.glob(path + '/*')

    for i in links:
        name = i.replace(path + '/', '').replace('.md', '')
        if filename == name:
            os.remove(i)


def write_markdown(markdown, title):
    '''
        Creates an html file that was just created,
        as well as the routes for flask
    '''
    root = os.path.join(flask.current_app.root_path,
                        flask.current_app.config["UPLOAD_WEBPAGES"])

    title = title.replace(' ', '_')
    path = os.path.join(root, title + ".md")

    # Writing to the new html file
    with open(path, 'w+') as f:
        f.write(markdown)
