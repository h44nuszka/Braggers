import math
import shutil
import time
from io import BytesIO
from werkzeug.utils import secure_filename
from flask import Flask, \
    render_template, \
    redirect, \
    request, \
    session, \
    send_file

import os
from flask_session.__init__ import Session
from datetime import timedelta, datetime
from zipfile import ZipFile

ALLOWED_EXTENSIONS = {'txt', 'pdf', 'png', 'jpg', 'jpeg', 'gif'}

app = Flask(__name__)
app.debug = True

app.config["SESSION_TYPE"] = "filesystem"
app.config['PERMANENT_SESSION_LIFETIME'] = timedelta(hours=5)
app.config['SEND_FILE_MAX_AGE_DEFAULT'] = 0
Session(app)


@app.errorhandler(500)
def internal_error(exception):
    app.logger.error(exception)
    return render_template('500.html'), 500


@app.after_request
def add_header(r):
    """
    Add headers to both force latest IE rendering engine or Chrome Frame,
    and also to cache the rendered page for 10 minutes.
    """
    r.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    r.headers["Pragma"] = "no-cache"
    r.headers["Expires"] = "0"
    r.headers['Cache-Control'] = 'public, max-age=0'
    return r


@app.route('/')
def index():
    return redirect('main')


@app.route('/main')
def main():
    deleteItems()
    session['portfolioName'] = None
    session['backgroundColor'] = None
    session['fontColor'] = None
    session['columns'] = None
    session['language'] = None
    session['menuElementsQty']= None
    session['menuItems'] = None
    session['siteContent'] = None
    session['menuElementsQty'] = None
    session['filenames'] = None
    session['names'] = None
    session['imageQty']= None
    session['imageInAColumn']= None

    session['IMAGE_UPLOADS'] = None
    session['DOWNLOAD_FOLDER'] = None

    session.modified = True

    session.clear()
    return render_template('index.html')


@app.route('/instructions')
def instructions():
    return render_template('instructions.html')


@app.route('/form')
def form():
    return render_template('form.html')


@app.route('/dataForm', methods=['GET','POST'])
def dataForm():
    if request.method == 'POST':
        DT = datetime.now()
        TS = str(datetime.timestamp(DT))
        #BASENAME = '/home/epi/19_rajh/Bragger/'
        BASENAME = '/mnt/c/Users/hania/Documents/studia/lic/'
        UPLOAD_FOLDER = BASENAME + 'static/templates/' + TS + '/static/img'
        DOWNLOAD_FOLDER = BASENAME + 'static/templates/' + TS
        session['IMAGE_UPLOADS'] = UPLOAD_FOLDER
        session['DOWNLOAD_FOLDER'] = DOWNLOAD_FOLDER
        #session['IMAGE_UPLOADS_IMG_PATH'] = '/~19_rajh/Bragger/static/templates/' + TS + '/static/img'
        session['IMAGE_UPLOADS_IMG_PATH'] = '/static/templates/' + TS + '/static/img'

        session['portfolioName'] = request.form['portfolioName']

        if request.form['colors'] == 'light':
            session['backgroundColor'] = '#FFFFFF'
            session['fontColor'] = '#606367'
        elif request.form['colors'] == 'dark':
            session['backgroundColor'] = '#757575'
            session['fontColor'] = '#E8D4D4'
        else:
            session['backgroundColor'] = request.form['background']
            session['fontColor'] = request.form['font']

        gridLayout = request.form['grid']
        gridLayout = gridLayout.split("x", 1)
        session['columns'] = int(gridLayout[0]) - 1

        session['language'] = request.form['language']

        session['menuElementsQty'] = int(request.form['menuElements'])
        session['menuItems'] = []
        session['siteContent'] = []
        appendMenuItemsAndContent()
        createFilesList()

        if session['imageQty'] % (session['columns']+1) < 2:
            session['imageInAColumn'] = session['imageQty'] // (session['columns']+1)
        else:
            if session['imageQty'] == 6:
                session['imageInAColumn'] = session['imageQty'] // (session['columns'] + 1)
            else:
                session['imageInAColumn'] = math.ceil(session['imageQty'] / (session['columns'] + 1))

        if session['menuElementsQty'] == 1:
            saveTemplate('mainPage.html')
        if session['menuElementsQty'] == 2:
            saveTemplate('mainPage.html')
            saveTemplate('secondPage.html')
        if session['menuElementsQty'] == 3:
            saveTemplate('mainPage.html')
            saveTemplate('secondPage.html')
            saveTemplate('thirdPage.html')
        if session['menuElementsQty'] == 4:
            saveTemplate('mainPage.html')
            saveTemplate('secondPage.html')
            saveTemplate('thirdPage.html')
            saveTemplate('fourthPage.html')

        session.modified = True

        return redirect('mainPage.html')


@app.route('/mainPage.html')
def mainPage():
    if not session.get("secure_filenames"):
        return redirect("form")
    return render_template('mainPage.html', imageFolder=session['IMAGE_UPLOADS_IMG_PATH'], filenamesNames2=zip(session['secure_filenames'], session['names']), filenamesNames=zip(session['secure_filenames'], session['names']), imageInAColumn=session['imageInAColumn'], menuItems=session['menuItems'], menuElementsQty=session['menuElementsQty'], imageQty=session['imageQty'], columns=session['columns'], portfolioName=session['portfolioName'], language=session['language'], backgroundColor=session['backgroundColor'], fontColor=session['fontColor'])


@app.route('/secondPage.html')
def secondPage():
    return render_template('secondPage.html', menuItems=session['menuItems'], menuElementsQty=session['menuElementsQty'], backgroundColor=session['backgroundColor'], fontColor=session['fontColor'], language=session['language'], siteContent=session['siteContent'], portfolioName=session['portfolioName'])


@app.route('/thirdPage.html')
def thirdPage():
    return render_template('thirdPage.html', menuItems=session['menuItems'], menuElementsQty=session['menuElementsQty'], backgroundColor=session['backgroundColor'], fontColor=session['fontColor'], language=session['language'], siteContent=session['siteContent'], portfolioName=session['portfolioName'])


@app.route('/fourthPage.html')
def fourthPage():
    return render_template('fourthPage.html', menuItems=session['menuItems'], menuElementsQty=session['menuElementsQty'], backgroundColor=session['backgroundColor'], fontColor=session['fontColor'], language=session['language'], siteContent=session['siteContent'], portfolioName=session['portfolioName'])


@app.route('/end')
def end():
    """
    Zip and send full package with compressed directory.
    """
    fileName = 'yourTemplates.zip'

    if not session.get('DOWNLOAD_FOLDER'):
        return redirect("form")
    directory = session['DOWNLOAD_FOLDER']

    rootdir = os.path.basename(directory)

    directory_static = '/home/epi/19_rajh/Bragger/static/staticTemplates/static'
    rootdir_static = os.path.basename(directory_static)

    memory_file = BytesIO()
    with ZipFile(memory_file, 'w') as zf:
        for dirpath, dirnames, files in os.walk(directory):
            for file in files:
                filepath = os.path.join(dirpath, file)
                parentpath = os.path.relpath(filepath, directory)
                arcname = os.path.join(rootdir, parentpath)
                zf.write(filepath, arcname)
        for dirpath, dirnames, files in os.walk(directory_static):
            for file in files:
                filepath = os.path.join(dirpath, file)
                parentpath = os.path.relpath(filepath, directory_static)
                arcname = os.path.join(rootdir_static, parentpath)
                zf.write(filepath, arcname)
    memory_file.seek(0)
    session.modified = True
    return send_file(memory_file, attachment_filename=fileName, as_attachment=True, cache_timeout=0)


@app.route('/delete')
def delete():
    deleteItems()
    return redirect('instructions')


def createFilesList():
    """
    Save uploaded images.
    session['secure_filenames'] is a list of filenames.
    session['names'] is a list of filenames formatted to names displayed on the template.
    """
    filenames = []
    session['names'] = []
    session['secure_filenames'] = []
    images = request.files.getlist('image')
    cwd = os.getcwd()

    if not os.path.exists(session['IMAGE_UPLOADS']):
        os.makedirs(session['IMAGE_UPLOADS'])

    for image in images:
        image.save(os.path.join(cwd, session['IMAGE_UPLOADS'], secure_filename(image.filename)))
        filenames.append(image.filename)

    session['imageQty'] = len(images)

    for filename in filenames:
        name = filename.split('.', 1)
        session['names'].append(name[0])
        session['secure_filenames'].append(secure_filename(filename))

    tmp = []
    for name in session['names']:
        tmp1 = name
        if "_" in str(tmp1):
            tmp1 = tmp1.replace("_", " ")
        if "-" in str(tmp1):
            tmp1 = tmp1.replace("-", " ")

        tmp.append(tmp1)

    session['names'] = tmp
    session['names'].sort()
    session['secure_filenames'].sort()
    session.modified = True

def deleteItems():
    """
    Directories created by users are deleted after one day
    """

    path = '/home/epi/19_rajh/Bragger/static/templates'
    if os.path.exists(path):
        for directory in os.listdir(path):
            oldFolder = path + '/' + directory
            if time.time() - float(str(directory)) > 86400:
                shutil.rmtree(oldFolder)


def appendMenuItemsAndContent():
    if session['menuElementsQty'] == 4:
        saveMenuItems1()
        saveMenuItems2()
        saveMenuItems3()
        saveMenuItems4()
    elif session['menuElementsQty'] == 3:
        saveMenuItems1()
        saveMenuItems2()
        saveMenuItems3()
    elif session['menuElementsQty'] == 2:
        saveMenuItems1()
        saveMenuItems2()
    elif session['menuElementsQty'] == 1:
        saveMenuItems1()


def saveTemplate(pageName):
    """
    Saves generated portfolio templates.
    """
    name = pageName
    if pageName == 'mainPage.html':
        name = 'index.html'
        pageTemplate = render_template('mainPage.html', imageFolder = session['IMAGE_UPLOADS_IMG_PATH'], filenamesNames = zip(session['secure_filenames'],
                                            session['names']), filenamesNames2 = zip(session['secure_filenames'],
                                            session['names']), imageInAColumn=session['imageInAColumn'],
                                            menuItems=session['menuItems'],
                                            menuElementsQty=session['menuElementsQty'], imageQty=session['imageQty'],
                                            columns=session['columns'], portfolioName=session['portfolioName'],
                                            language=session['language'], backgroundColor=session['backgroundColor'],
                                            fontColor=session['fontColor'])

        pageTemplate = pageTemplate.replace(session['IMAGE_UPLOADS_IMG_PATH'], "static/img")
        pageTemplate = pageTemplate.replace('<div class="preview"><p>To jest podgląd.</p><a href="/19_rajh/bragger/form"><button class="button">Chcę coś jeszcze zmienić!</button></a><a href="/19_rajh/bragger/end"><button class="button">Pobierz paczkę</button></a><a href="/19_rajh/bragger/delete"><button class="button">Zabierz mnie do instrukcji</button></a></div>', "")
    else:
        pageTemplate = render_template(name, menuItems=session['menuItems'],
                                             menuElementsQty=session['menuElementsQty'],
                                             backgroundColor=session['backgroundColor'], fontColor=session['fontColor'],
                                             language=session['language'], siteContent=session['siteContent'], portfolioName=session['portfolioName'])

    pageTemplate = pageTemplate.replace('mainPage.html', 'index.html')
    path = session['DOWNLOAD_FOLDER'] + '/' + name
    with open(path, 'w', encoding='utf-8') as f:
        f.write(pageTemplate)
        f.close()


def saveMenuItems1():
    session['menuItems'].append(request.form['menuItem1'])

def saveMenuItems2():
    session['menuItems'].append(request.form['menuItem2'])
    session['siteContent'].append(request.form['description2'])

def saveMenuItems3():
    session['menuItems'].append(request.form['menuItem3'])
    session['siteContent'].append(request.form['description3'])

def saveMenuItems4():
    session['menuItems'].append(request.form['menuItem4'])
    session['siteContent'].append(request.form['description4'])


if __name__ == "__main__":
    app.run(host='0.0.0.0', port=5121, debug=True)
