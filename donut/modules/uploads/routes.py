import flask
import json
from werkzeug import secure_filename

from donut.modules.uploads import blueprint, helpers


@blueprint.route('/lib/<path:url>')
def display(url):
    page = helpers.readPage(url.lower())

    return flask.render_template('page.html', page = page, title = url)


@blueprint.route('/uploads')
def uploads():
    return flask.render_template('uploads.html')

ALLOWED_EXTENSIONS = set(['txt', 'pdf', 'png', 'jpg', 'jpeg', 'gif'])

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@blueprint.route('/_uploader', methods=['GET', 'POST'])
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
            file.save(os.path.join(flask.current_app.config['UPLOAD_FOLDER'], filename))
            return flask.redirect(flask.url_for('uploaded_file',
                                    filename=filename))
    return
