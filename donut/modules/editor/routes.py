import flask
import json
import os

from donut.modules.editor import blueprint, helpers



@blueprint.route('/editor')
def editor(input_text='Hello World!!!'):
    return flask.render_template('editor_page.html', input_text=input_text)


@blueprint.route('/_save', methods = ['POST'])
def save():
    if flask.request.method == 'POST':
        html = flask.request.form['html']
        title = flask.request.form['html']
    root = 'donut/modules/upload'
    root += "/templates"
    path = os.path.join(root, title+".html")
    f= open(path,"w+")
    f.write(html)
    f.close()

    f = open(root + "routes.py", "w")
    f.write("@blueprint.route('/"+title+"'\n")
    f.write("def "+title+"():\n")
    f.write("flask.render_template()\n\n")
    f.close()
    return redirect(url_for('uploaded_file', filename=filename))
