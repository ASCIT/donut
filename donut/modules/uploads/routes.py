import flask
import os
from werkzeug import secure_filename
from donut.modules.uploads import blueprint, helpers

@blueprint.route('/lib/<path:url>')
def display(url):
    '''
    Displays the webpages that have been created by users.
    '''
    page = helpers.read_page(url.replace(' ', '_'))
    if page == None:
        return flask.abort(404)
    return flask.render_template(
        'page.html',
        title=url.replace('_', ' '),
        permissions=helpers.check_upload_permission())


@blueprint.route('/uploads/_send_page')
def get_page():
    '''
    Sends the page to frontend.
    '''
    url = flask.request.args.get('url')
    return helpers.read_page(url.replace(' ', '_'))


@blueprint.route('/uploads', methods=['GET'])
def uploads():
    '''
    Serves the webpage that allows a user to upload a file.
    '''
    if helpers.check_upload_permission():
        return flask.render_template('uploads.html')
    else:
        flask.abort(403)


@blueprint.route('/uploads/_upload_file', methods=['POST'])
def upload_file():
    '''
    Handles the uploading of the file
    '''
    if 'file' not in flask.request.files:
        flask.abort(500)
    file = flask.request.files['file']
    filename = secure_filename(file.filename)
    uploads = os.path.join(flask.current_app.root_path,
                           flask.current_app.config['UPLOAD_FOLDER'])
    if helpers.check_upload_permission():
        helpers.remove_link(filename)
        file.save(os.path.join(uploads, filename))
        return flask.jsonify({
            'url':
            flask.url_for('uploads.uploaded_file', filename=filename)
        })
    else:
        flask.abort(403)


@blueprint.route('/uploads/_check_valid_file', methods=['POST'])
def check_file():
    '''
    Checks if the file: exists, has a valid extension, and
    smaller than 10 mb
    '''
    if 'file' not in flask.request.files:
        return flask.jsonify({'error': 'No file selected'})
    if helpers.check_upload_permission():
        file = flask.request.files['file']
        return flask.jsonify({'error': helpers.check_valid_file(file)})
    else:
        return flask.abort(403)


@blueprint.route('/lib/uploaded_file/<filename>', methods=['GET'])
def uploaded_file(filename):
    '''
    Serves the actual uploaded file.
    '''
    uploads = os.path.join(flask.current_app.root_path,
                           flask.current_app.config['UPLOAD_FOLDER'])
    return flask.send_from_directory(uploads, filename, as_attachment=False)


@blueprint.route('/uploads/_delete')
def delete_uploaded_file():
    """
    End point for deleting an upload
    """
    filename = flask.request.args.get('filename')
    if filename != None and helpers.check_upload_permission():
        helpers.remove_link(filename)
    return flask.redirect(flask.url_for('uploads.uploaded_list'))


@blueprint.route('/uploads/uploaded_list', methods=['GET'])
def uploaded_list():
    '''
    Shows the list of uploaded files
    '''
    links = helpers.get_links()
    return flask.render_template(
        'uploaded_list.html',
        delete_file_endpoint='uploads.delete_uploaded_file',
        links=links,
        permissions=helpers.check_upload_permission())
