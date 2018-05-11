import flask
import os


def create_new_html():
    """
    Creates a blank html page.
    """
    with open("template.html") as f:
        with open("title.html") as f1:
            for line in f:
                f1.write(line)
    return


def rename_title(oldfilename, newfilename):
    """
    Changes the file name of an html file
    Need to look for paths
    """

    os.rename(oldfilename, newfilename)
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
        curFile = read_file(os.path.join(flask.current_app.config["COMMITTEE_UPLOAD_FOLDER"], name + ".html"))
        return curFile
    else:
        path = os.path.join(flask.current_app.root_path,
                                   flask.current_app.config['UPLOAD_WEBPAGES'])
        curFile = read_file(os.path.join(path, name + '.md'))
        return curFile


def read_file(path):
    curFile = ''
    with open(path) as f:
        curFile += f.read()
    return curFile


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
    root = os.path.join(flask.current_app.root_path, flask.current_app.config["UPLOAD_WEBPAGES"])

    title = title.replace(' ', '_')
    path = os.path.join(root, title + ".md")

    # Writing to the new html file
    f = open(path, "w+")
    f.write(markdown)
    f.close()

    f = open(os.path.join(flask.current_app.root_path,
                          flask.current_app.config["EXISTING_LIST"],'pages.txt'), "w+")
    f.write(title)
    f.close()
    return 0
