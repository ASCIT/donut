import flask
import json
import os
from werkzeug import secure_filename

#DEBUGGING
import glob

from donut.modules.uploads import blueprint, helpers
from donut.resources import Permissions
from donut.auth_utils import check_permission

@blueprint.route('/lib/<path:url>')
def display(url):
    '''
        Displays the webpages that have been created by users.
    '''
    page = helpers.readPage(url.replace(' ', '_'))
    return flask.render_template('page.html', page=page, title=url, permission=check_permission(Permissions.ADMIN))

@blueprint.route('/uploads', methods=['GET', 'POST'])
def uploads():
    '''
    Serves the webpage that allows a user to upload a file.
    '''
    if flask.request.method == 'POST':
        if 'file' not in flask.request.files:
            flask.flash('No file part')
            return flask.render_template('uploads.html')
        file = flask.request.files['file']

        if file.filename == '':
            flask.flash('No selected file')
            return flask.redirect(request.url)
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            uploads = os.path.join(flask.current_app.root_path,
                           flask.current_app.config['UPLOAD_FOLDER'])
            file.save(os.path.join(uploads, filename))
            return flask.redirect(
                flask.url_for('uploads.uploaded_file', filename=filename))
        else:
            flask.flash('Unsupported filetype')
    return flask.render_template('uploads.html')


@blueprint.route('/uploaded_file/<filename>', methods = ['GET'])
def uploaded_file(filename):
    '''
    Serves the actual uploaded file.
    '''
    print(filename)
    print(glob.glob(flask.current_app.config['UPLOAD_FOLDER']+'/*'))
    uploads = os.path.join(flask.current_app.root_path,
                           flask.current_app.config['UPLOAD_FOLDER'])
    print(uploads)
    return flask.send_from_directory(uploads,
                                     filename, as_attachment=False)


ALLOWED_EXTENSIONS = set(['txt', 'pdf', 'png', 'jpg', 'jpeg', 'gif'])

@blueprint.route('/uploaded_list')
def uploaded_list():
    '''
    Shows the list of uploaded files
    '''
    path = os.path.join(flask.current_app.root_path,
                           flask.current_app.config['UPLOAD_FOLDER'])
    links = glob.glob(path + '/*')
    for i in range(len(links)):
        links[i] = links[i].replace(path + '/', '')
        links[i] = (flask.url_for(
            'uploads.uploaded_file', filename=links[i]), links[i])
    return flask.render_template('uploaded_list.html', links=links)

def allowed_file(filename):
    '''
    Checks for allowed file extensions.
    '''
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS
