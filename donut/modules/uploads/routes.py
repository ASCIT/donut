import flask
import json
import os
from werkzeug import secure_filename

#DEBUGGING
import glob

from donut.modules.uploads import blueprint, helpers


@blueprint.route('/lib/<path:url>')
def display(url):
    page = helpers.readPage(url.lower())

    return flask.render_template('page.html', page=page, title=url)


@blueprint.route('/uploads', methods=['GET', 'POST'])
def uploads():
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
            file.save(os.path.join(flask.current_app.config['UPLOAD_FOLDER'],
                             filename))
            return flask.redirect(
                flask.url_for('uploads.uploaded_file', filename=filename))
        else:
            flask.flash('Unsupported filetype')
    return flask.render_template('uploads.html')


@blueprint.route('/uploaded_file/<filename>', methods = ['GET'])
def uploaded_file(filename):
    print(filename)
    print(flask.current_app.config['UPLOAD_FOLDER'])
    print(glob.glob(flask.current_app.config['UPLOAD_FOLDER']+'/*'))
    return flask.send_from_directory(flask.current_app.config['UPLOAD_FOLDER'],
                                     filename, as_attachment=True)

ALLOWED_EXTENSIONS = set(['txt', 'pdf', 'png', 'jpg', 'jpeg', 'gif'])

@blueprint.route('/uploaded_list')
def uploadedList():
    links = glob.glob(flask.current_app.config['UPLOAD_FOLDER']+'/*')
    for i in range(len(links)):
        links[i] = (flask.url_for('uploads.uploaded_file', filename=links[i][22:]), links[i][22:])
    return flask.render_template('uploaded_list.html', links=links)

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


@blueprint.route('/_uploader', methods=['POST'])
def upload_file():
    if request.method == 'POST':

        if 'file' not in request.files:
            flash('No file part')
            return redirect(request.url)
        file = request.files['file']

        if file.filename == '':
            flash('No selected file')
            return flask.redirect(request.url)
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            file.save(
                os.path.join(flask.current_app.config['UPLOAD_FOLDER'],
                             filename))
            return flask.redirect(
                flask.url_for('uploaded_file', filename=filename))
    return
