import os
from flask import Flask, request, redirect, url_for, make_response
from werkzeug import secure_filename
from flask import send_from_directory
import swiftclient
import keystoneclient
from flask import render_template
import couchdb
import datetime
import hashlib
import time

#variables for Cloudant Database
USERNAME = "7d79e7d0-6d67-4a21-aac0-15fff940c492-bluemix"
PASSWORD = "4828714fecff497426fe357632f22a10f6d0a82e2d0f3888ea59bbad2a57e5fb"

#connect to the Cloudant Database instance
couch = couchdb.Server("https://7d79e7d0-6d67-4a21-aac0-15fff940c492-bluemix:4828714fecff497426fe357632f22a10f6d0a82e2d0f3888ea59bbad2a57e5fb@7d79e7d0-6d67-4a21-aac0-15fff940c492-bluemix.cloudant.com")
db = couch['appsync']

UPLOAD_FOLDER = './uploads'
ALLOWED_EXTENSIONS = set(['txt', 'pdf', 'png', 'jpg', 'jpeg', 'gif'])

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1] in ALLOWED_EXTENSIONS

@app.route('/click/<objectname>')
def click_here(objectname):
    return  objectname

@app.route('/container/<filename>')
def downloadFile(filename):
    downdoc = db.get(filename)
    file = open(UPLOAD_FOLDER + '/' + filename,"w+")
    file.write(downdoc['contents'])
    file.close()
    response = make_response()
    response.headers["Content-Disposition"] = ""\
        "attachment; filename=%s" % UPLOAD_FOLDER + "/" +filename
    return response
    #return send_from_directory(directory=app.config['UPLOAD_FOLDER'], filename=filename)


@app.route('/container')
def getContainers():
 return render_template('hello.html', db=db)

@app.route('/', methods = ['POST','GET'])
def index():
    if request.method == 'POST':
        if request.form['submit'] == 'Upload':
            return redirect(url_for('upload_file'))
        elif request.form['submit'] == 'click here':
            return redirect(url_for('getContainers'))
    return '''
    <!doctype html>
        <title>Welcome!</title>
        <h1>Welcome to Cloud computing!</h1>
        <form action="" method=post enctype=multipart/form-data>
        <input type='submit' name='submit' value='click here'>
        <input type='submit' name='submit' value='Upload'> </form>
        '''

@app.route('/uploading/<filename>')
def insertFileIntoDB(filename):
    #read the file and store the contents
    file = open(UPLOAD_FOLDER + "/" + filename, "rb")
    content = file.read()
    dateModified = time.strftime("%m/%d/%Y %I:%M:%S %p",time.localtime(os.stat(UPLOAD_FOLDER + "/" + filename).st_mtime))
    #dateModified = os.path.getmtime(filename)
    #generate the hash code for the contents of the file
    filehash = hashlib.sha224(content).hexdigest()
    #acess the db to check whether it has document for same file name
    doc = db.get(filename)
    if doc:
        if doc['hashcode'] == filehash:
            return "File Exist on the server"

    docid,docrev = db.save({
        '_id' : filename,
        'contents' : content,
        'hashcode' : filehash,
        'datemodified' : dateModified
    })
    doc = db.get(docid)
    return doc['datemodified']


@app.route('/upload', methods=['GET', 'POST'])
def upload_file():
    if request.method == 'POST':
        file = request.files['file']
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
            file.close()
        return redirect(url_for('insertFileIntoDB',filename = filename))

    return '''
    <!doctype html>
    <title>Upload new File</title>
    <h1>Upload new File</h1>
    <form action="" method=post enctype=multipart/form-data>
      <p><input type=file name=file>
         <input type=submit value=Upload>
    </form>
    '''
@app.route('/delete/<filename>')
def deleteFile(filename):
    deldocs = db.get(filename)
    res = db.delete(deldocs)
    return '''
    <!doctype html>
    <p>File deleted</p>
    <a href = '/'>Home</a>'''

@app.route('/uploads/<filename>')
def uploaded_file(filename):
    return filename


if __name__ == '__main__':
    app.run()