import os
from flask import Flask, request, redirect, url_for, make_response
from werkzeug import secure_filename
from flask import send_from_directory
from flask import render_template
import couchdb
import datetime
import hashlib
import time
import json

#variables for Cloudant Database
USERNAME = "be8dae94-2e36-4ff1-ba74-bdc4f6be1804-bluemix"
PASSWORD = "473146b3b4d9073f3f02c83b97b5f8778a45a62e94177c1a1ecd1601edd24cfa"

UPLOAD_FOLDER = './uploads'
ALLOWED_EXTENSIONS = set(['txt', 'pdf', 'png', 'jpg', 'jpeg', 'gif'])

#connect to the Cloudant Database instance
couch = couchdb.Server("https://be8dae94-2e36-4ff1-ba74-bdc4f6be1804-bluemix:473146b3b4d9073f3f02c83b97b5f8778a45a62e94177c1a1ecd1601edd24cfa@be8dae94-2e36-4ff1-ba74-bdc4f6be1804-bluemix.cloudant.com")
db = couch['appsync']

app = Flask(__name__)
app.config.from_object(__name__)
port = int(os.getenv("VCAP_APP_PORT",'5000'))

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1] in ALLOWED_EXTENSIONS

@app.route('/list/<filename>')
def downloadFile(filename):
    downdoc = db.get(filename)
    file = open(UPLOAD_FOLDER + '/' + filename,"w+")
    file.write(downdoc['contents'])
    file.close()
    return send_from_directory(directory=app.config['UPLOAD_FOLDER'], filename=filename)


@app.route('/list')
def getContainers():
 return render_template('Filelist.html', db=db)

@app.route('/', methods = ['POST','GET'])
def index():
    if request.method == 'POST':
        if request.form['submit'] == 'Upload File':
            return redirect(url_for('upload_file'))
        elif request.form['submit'] == 'View Files':
            return redirect(url_for('getContainers'))
    return '''
    <!DOCTYPE html>
<head>
    <meta charset="UTF-8">
    <title>Home</title>
</head>
<body>
<h1 align="center">Welcome to Cloud computing!</h1>
<h3 align="center">File storage service by BlueMix</h3><br/><br/>
<table width="40%" align="center">
<form action="" method=post enctype=multipart/form-data>
        <tr align="center">
            <th ><input type='submit' name='submit' value='View Files'></th>
            <th > <input type='submit' name='submit' value='Upload File' ></th>
        </tr>

</form>
</table>
</body>'''

@app.route('/uploading/<filename>')
def insertFileIntoDB(filename):
    file = open(UPLOAD_FOLDER + "/" + filename, "rb")
    content = file.read()
    dateModified = time.strftime("%m/%d/%Y %I:%M:%S %p",time.localtime(os.stat(UPLOAD_FOLDER + "/" + filename).st_mtime))
    filehash = hashlib.sha224(content).hexdigest()

    doc = db.get(filename)
    if doc:
        if doc['hashcode'] == filehash:
            message = 'Sorry! File already exist on the server'
            return render_template('info.html',message=message)
        else:
            doc['contents'] = content
            doc['hashcode'] = filehash
            doc['datemodified'] = dateModified
            db.save(doc)
            message = "File Update Successfully"
            return render_template('info.html', message = message)

    docid,docrev = db.save({
        '_id' : filename,
        'contents' : content,
        'hashcode' : filehash,
        'datemodified' : dateModified
    })
    doc = db.get(docid)
    message = "File uploaded Successfully"
    return render_template('info.html',message=message)


@app.route('/upload', methods=['GET', 'POST'])
def upload_file():
    if request.method == 'POST':
        file = request.files['file']
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
            file.close()
            return redirect(url_for('insertFileIntoDB',filename = filename))
        else:
            message = "Sorry! Either File is not supported or file not selected"
            return render_template('info.html',message=message)
    return '''
    <!doctype html>
    <title>Upload new File</title>
    <h1>Upload new File</h1>
    <form action="" method=post enctype=multipart/form-data>
      <p><input type=file name=file>
         <input type=submit value=Upload>
    </form>
    <a href='/'> << Back </a>
    '''

@app.route('/delete/<filename>')
def deleteFile(filename):
    deldocs = db.get(filename)
    res = db.delete(deldocs)
    message = "File deleted!"
    return render_template('info.html',message=message)



if __name__ == '__main__':
    app.run(host='0.0.0.0',port=port)