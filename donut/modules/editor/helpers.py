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
    return


def read_markdown(name):
    '''
    Reads in the mark down text from a file.
    '''
    underCommittee = [
        'BoC', 'ascit_bylaws', 'BoC.bylaws', 'BoC.defendants', 'BoC.FAQ',
        'BoC.reporters', 'BoC.witnesses', 'CRC', 'honor_system_handbook'
    ]

    # Check if the pages were already created prior (only the BoC pages)
    if name in underCommittee:
        curFile = read_file(
            os.path.join(flask.current_app.config["COMMITTEE_UPLOAD_FOLDER"],
                         name + ".html"))
        return curFile
    else:
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
            curFile += f.read()
        return curFile
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
    for i in range(len(links)):
        links[i] = links[i].replace(root + '/', '').replace('.md', '')
        if links[
                i] not in 'BoC ASCIT_Bylaws BoC_Bylaws BoC_Defendants BoC_FAQ BoC_Reporters BoC_Witness CRC':
            link = flask.url_for('uploads.display', url=links[i])
            results.append((link, links[i]))
    return results


def remove_link(filename):
    '''
    Get rid of matching filenames
    '''
    path = os.path.join(flask.current_app.root_path,
                        flask.current_app.config['UPLOAD_WEBPAGES'])
    links = glob.glob(path + '/*')
    for i in links:
        if filename in i:
            os.remove(i)


def write_markdown(markdown, title):
    '''
        Creates an html file that was just created,
        as well as the routes for flask
    '''
    # Special cases for exisiting BoC and currenly existing pages.
    underCommittee = [
        'BoC', 'ascit_bylaws', 'BoC.bylaws', 'BoC.defendants', 'BoC.FAQ',
        'BoC.reporters', 'BoC.witnesses', 'CRC', 'honor_system_handbook'
    ]
    if title in underCommittee:
        root = flask.current_app.config["COMMITTEE_UPLOAD_FOLDER"]
        path = os.path.join(root, title + '.html')
        f = open(path, "w+")
        f.write(markdown)
        f.close()
    # Non-special cases.
    root = os.path.join(flask.current_app.root_path,
                        flask.current_app.config["UPLOAD_WEBPAGES"])

    title = title.replace(' ', '_')
    path = os.path.join(root, title + ".md")

    # Writing to the new html file
    f = open(path, "w+")
    f.write(markdown)
    f.close()

    f = open(
        os.path.join(flask.current_app.root_path,
                     flask.current_app.config["EXISTING_LIST"], 'pages.txt'),
        "w+")
    f.write(title)
    f.close()
    return 0
