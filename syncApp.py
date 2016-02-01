import os
from flask import Flask, request, redirect, url_for, make_response, send_file
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

#Variables for file upload
UPLOAD_FOLDER = './uploads'
ALLOWED_EXTENSIONS = set(['txt', 'pdf', 'png', 'jpg', 'jpeg', 'gif'])

#connect to the Cloudant Database instance
couch = couchdb.Server("https://be8dae94-2e36-4ff1-ba74-bdc4f6be1804-bluemix:473146b3b4d9073f3f02c83b97b5f8778a45a62e94177c1a1ecd1601edd24cfa@be8dae94-2e36-4ff1-ba74-bdc4f6be1804-bluemix.cloudant.com")
db = couch['appsync']

app = Flask(__name__)
app.config.from_object(__name__)
#Uncomment the below line when deploying it on Bluemix server
#port = int(os.getenv("VCAP_APP_PORT",'5000'))
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

#Function to validate the type of file being uploaded. Takes one parameter which is the file and does not return anything
def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1] in ALLOWED_EXTENSIONS

#Function to display selectver.html template which lets the user to select the version of the file to download
#Takes filename as the parameter
@app.route('/download/selectver/<filename>')
def selectver(filename):
    return render_template('selectver.html',db=db, filename = filename)

#Function to prepare the requested file to download to the user machine.
#Takes filename as the parameter
@app.route('/download/<filename>', methods = ["post"])
def downloadFile(filename):
    version = request.form['version'].encode('ascii','ignore')
    downdoc = db.get(filename)
    file = open(UPLOAD_FOLDER + '/' + filename,"w+")
    file.write(downdoc['version'][version]['rev_content'])
    file.close()
    return send_file(app.config['UPLOAD_FOLDER'] + '/'+ filename, as_attachment=True)


#Function to list the file name which are in the database
@app.route('/list')
def getContainers():
 return render_template('Filelist.html', db=db)

@app.route('/listver/<filename>')
def listVersions(filename):
    doc = db.get(filename)
    return render_template('listver.html', doc=doc)

#Function to load the index file (Home page)
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

#Function which inserts,updates documents in the DB
#Takes filename as the parameter
@app.route('/uploading/<filename>')
def insertFileIntoDB(filename):
    #open the file and read the contents of the file
    file = open(UPLOAD_FOLDER + "/" + filename, "rb")
    content = file.read()

    #Get the modified date property of the file
    dateModified = time.strftime("%m/%d/%Y %I:%M:%S %p",time.localtime(os.stat(UPLOAD_FOLDER + "/" + filename).st_mtime))
    #calculate the hashcode for the contents of the file
    filehash = hashlib.sha224(content).hexdigest()
    doc = db.get(filename)
    if doc:
        for ver in doc['version']:
            #check whether the content already exist in DB
            if (doc['version'][ver]):
                if(doc['version'][ver]['rev_hashcode'] == filehash):
                    message = 'Sorry! File already exist on the server'
                    return render_template('info.html',message=message)
        #Add sub document into the document
        latest_version = int(doc['latest_version'].encode('ascii','ignore')) + 1
        latest_version = str(latest_version)
        doc['latest_version'] = latest_version
        doc['disp_modified_date'] = dateModified
        doc['version'][latest_version] = {'rev_content' : content,
                    'rev_hashcode' : filehash,
                    'datemodified' : dateModified}
        db.save(doc)
        '''doc = db.save({
            '_id' : filename,
            'latest_version': latest_version,
            'disp_modified_date' : dateModified,
            'version' : {
            latest_version:
                {
                    'rev_content' : content,
                    'rev_hashcode' : filehash,
                    'datemodified' : dateModified
                }
        }

        })'''
        message = "New version " + latest_version + " for the file " + filename + " added successfully."
        return render_template('info.html', message = message)
    latest_version = str(1)
    docid,docrev = db.save({
            '_id' : filename,
            'latest_version' : latest_version,
            'disp_modified_date' : dateModified,
            'version':
                {
                    latest_version :
                         {
                        'rev_content': content,
                        'rev_hashcode' : filehash,
                        'datemodified' : dateModified
                        }
                }
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
    <h1 align="center">Upload new File</h1>
    <div align="center"><form action="" method=post enctype=multipart/form-data>
      <input type=file name=file>
         <input type=submit value=Upload>
         <p>(Upload only .txt files)
    </form>
    <a href='/'> << Back </a></div>
    '''

@app.route('/deletever/<filename>')
def deleteverFile(filename):
    return render_template('deletever.html',db=db, filename = filename)
    #deldocs = db.get(filename)
    #res = db.delete(deldocs)

def deleteFullFile(doc):
    for ver in doc['version']:
        if doc['version'][ver] :
            return
    db.delete(doc)
    return "As there was only one version of the file, the file deleted!"

@app.route('/delete/<filename>',methods=['POST'])
def deleteFile(filename):
    version = request.form['version'].encode('ascii','ignore')
    downdoc = db.get(filename)
    downdoc['version'][version] = None
    db.save(downdoc)
    res = deleteFullFile(downdoc)
    if res:
        message = res
    else:
        message = "Version " + version + " deleted!"
    return render_template('info.html',message=message)

if __name__ == '__main__':
    #app.run(host='0.0.0.0',port=port)
    app.run()