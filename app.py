import math
import shutil
import time
from io import BytesIO
from werkzeug.utils import secure_filename
from flask import Flask, render_template, redirect, request, session, send_file, make_response
import os
from flask_session.__init__ import Session
from datetime import timedelta, datetime
from zipfile import ZipFile

app = Flask(__name__)
app.debug = True

# Configurations
app.config["SESSION_TYPE"] = "filesystem"
app.config['PERMANENT_SESSION_LIFETIME'] = timedelta(hours=5)
app.config['SEND_FILE_MAX_AGE_DEFAULT'] = 0
Session(app)

ALLOWED_EXTENSIONS = {'txt', 'pdf', 'png', 'jpg', 'jpeg', 'gif'}
BASE_DIR = '/mnt/c/Users/hania/Documents/studia/lic/'
STATIC_TEMPLATES_DIR = os.path.join(BASE_DIR, 'static/templates')


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
    clear_session()
    delete_old_directories()
    return render_template('index.html')


@app.route('/instructions')
def instructions():
    return render_template('instructions.html')


@app.route('/form')
def form():
    return render_template('form.html')


@app.route('/dataForm', methods=['GET', 'POST'])
def dataForm():
    if request.method == 'POST':
        DT = datetime.now()
        TS = str(datetime.timestamp(DT))
        # BASE_DIR = '/home/epi/19_rajh/Bragger/'
        BASE_DIR = '/mnt/c/Users/hania/Documents/studia/lic/'
        UPLOAD_FOLDER = os.path.join(BASE_DIR, 'static/templates', TS, 'static/img')
        DOWNLOAD_FOLDER = os.path.join(BASE_DIR, 'static/templates', TS)

        session['IMAGE_UPLOADS'] = UPLOAD_FOLDER
        session['DOWNLOAD_FOLDER'] = DOWNLOAD_FOLDER
        # session['IMAGE_UPLOADS_IMG_PATH'] = '/~19_rajh/Bragger/static/templates/' + TS + '/static/img'
        session['IMAGE_UPLOADS_IMG_PATH'] = '/static/templates/' + TS + '/static/img'

        session['portfolioName'] = request.form['portfolioName']
        session['backgroundColor'], session['fontColor'] = get_colors(request.form['colors'], request.form)
        session['columns'] = int(request.form['grid'].split("x", 1)[0]) - 1

        handle_languages()

        session['menuElementsQty'] = int(request.form['menuElements'])
        session['menuItems'] = []
        session['siteContent'] = []
        append_menu_items_and_content()
        create_files_list()
        calculate_image_in_column()

        save_templates()
        print(session)
        return redirect('mainPage.html')


@app.route('/mainPage.html')
def mainPage():
    if not session.get("secure_filenames"):
        return redirect("form")
    return render_template('mainPage.html',
                           imageFolder=session['IMAGE_UPLOADS_IMG_PATH'],
                           filenamesNames2=zip(session['secure_filenames'], session['names']),
                           filenamesNames=zip(session['secure_filenames'], session['names']),
                           imageInAColumn=session['imageInAColumn'],
                           menuItems=session['menuItems'],
                           menuElementsQty=session['menuElementsQty'],
                           imageQty=session['imageQty'],
                           columns=session['columns'],
                           portfolioName=session['portfolioName'],
                           language=session['language'],
                           secondLanguage=session['secondLanguage'],
                           backgroundColor=session['backgroundColor'],
                           fontColor=session['fontColor'])


@app.route('/secondPage.html')
def secondPage():
    return render_template('secondPage.html',
                           menuItems=session['menuItems'],
                           menuElementsQty=session['menuElementsQty'],
                           backgroundColor=session['backgroundColor'],
                           fontColor=session['fontColor'],
                           language=session['language'],
                           secondLanguage=session['secondLanguage'],
                           siteContent=session['siteContent'],
                           portfolioName=session['portfolioName'])


@app.route('/thirdPage.html')
def thirdPage():
    return render_template('thirdPage.html',
                           menuItems=session['menuItems'],
                           menuElementsQty=session['menuElementsQty'],
                           backgroundColor=session['backgroundColor'],
                           fontColor=session['fontColor'],
                           language=session['language'],
                           secondLanguage=session['secondLanguage'],
                           siteContent=session['siteContent'],
                           portfolioName=session['portfolioName'])


@app.route('/fourthPage.html')
def fourthPage():
    return render_template('fourthPage.html',
                           menuItems=session['menuItems'],
                           menuElementsQty=session['menuElementsQty'],
                           backgroundColor=session['backgroundColor'],
                           fontColor=session['fontColor'],
                           language=session['language'],
                           secondLanguage=session['secondLanguage'],
                           siteContent=session['siteContent'],
                           portfolioName=session['portfolioName'])


@app.route('/mainPage_l2.html')
def mainPage_l2():
    if not session.get("secure_filenames"):
        return redirect("form")
    return render_template('mainPage_l2.html',
                           imageFolder=session['IMAGE_UPLOADS_IMG_PATH'],
                           filenamesNames2=zip(session['secure_filenames'], session['names']),
                           filenamesNames=zip(session['secure_filenames'], session['names']),
                           imageInAColumn=session['imageInAColumn'],
                           menuItems_l2=session['menuItems_l2'],
                           menuElementsQty=session['menuElementsQty'],
                           imageQty=session['imageQty'],
                           columns=session['columns'],
                           portfolioName=session['portfolioName'],
                           language=session['language'],
                           secondLanguage=session['secondLanguage'],
                           backgroundColor=session['backgroundColor'],
                           fontColor=session['fontColor'])


@app.route('/secondPage_l2.html')
def secondPage_l2():
    return render_template('secondPage_l2.html',
                           menuItems_l2=session['menuItems_l2'],
                           menuElementsQty=session['menuElementsQty'],
                           backgroundColor=session['backgroundColor'],
                           fontColor=session['fontColor'],
                           language=session['language'],
                           secondLanguage=session['secondLanguage'],
                           siteContent_l2=session['siteContent_l2'],
                           portfolioName=session['portfolioName'])


@app.route('/thirdPage_l2.html')
def thirdPage_l2():
    return render_template('thirdPage_l2.html',
                           menuItems_l2=session['menuItems_l2'],
                           menuElementsQty=session['menuElementsQty'],
                           backgroundColor=session['backgroundColor'],
                           fontColor=session['fontColor'],
                           language=session['language'],
                           secondLanguage=session['secondLanguage'],
                           siteContent_l2=session['siteContent_l2'],
                           portfolioName=session['portfolioName'])


@app.route('/fourthPage_l2.html')
def fourthPage_l2():
    return render_template('fourthPage_l2.html',
                           menuItems_l2=session['menuItems_l2'],
                           menuElementsQty=session['menuElementsQty'],
                           backgroundColor=session['backgroundColor'],
                           fontColor=session['fontColor'],
                           language=session['language'],
                           secondLanguage=session['secondLanguage'],
                           siteContent_l2=session['siteContent_l2'],
                           portfolioName=session['portfolioName'])


@app.route('/end')
def end():
    """
    Handle export based on the user's choice.
    """
    export_type = request.args.get('type', 'zip')

    if export_type == 'zip':
        return create_zip_and_send()


@app.route('/delete')
def delete():
    delete_old_directories()
    return redirect('instructions')


@app.route('/pdf_preview')
def pdf_preview():
    page_template = render_template('mainPagePDF.html',
                                    imageFolder=session['IMAGE_UPLOADS_IMG_PATH'],
                                    filenamesNames=zip(session['secure_filenames'], session['names']),
                                    filenamesNames2=zip(session['secure_filenames'], session['names']),
                                    imageInAColumn=session['imageInAColumn'],
                                    menuItems=session['menuItems'],
                                    menuElementsQty=session['menuElementsQty'],
                                    imageQty=session['imageQty'],
                                    columns=session['columns'],
                                    portfolioName=session['portfolioName'],
                                    language=session['language'],
                                    secondLanguage=session['secondLanguage'],
                                    backgroundColor=session['backgroundColor'],
                                    fontColor=session['fontColor'])

    #page_template = page_template.replace(session['IMAGE_UPLOADS_IMG_PATH'], "static/img")

    return page_template


def create_zip_and_send():
    """
    Zip and send full package with compressed directory.
    """
    if not session.get('DOWNLOAD_FOLDER'):
        return redirect("/form")

    file_name = 'yourTemplates.zip'
    directory = session['DOWNLOAD_FOLDER']
    directory_static = '/home/epi/19_rajh/Bragger/static/staticTemplates/static'

    memory_file = BytesIO()
    with ZipFile(memory_file, 'w') as zf:
        for dirpath, _, files in os.walk(directory):
            for file in files:
                filepath = os.path.join(dirpath, file)
                arcname = os.path.relpath(filepath, directory)
                zf.write(filepath, arcname)
        for dirpath, _, files in os.walk(directory_static):
            for file in files:
                filepath = os.path.join(dirpath, file)
                arcname = os.path.relpath(filepath, directory_static)
                zf.write(filepath, arcname)
    memory_file.seek(0)
    return send_file(memory_file, as_attachment=True, download_name=file_name)


def get_colors(color_choice, form):
    """
    Determine the background and font colors based on user choice.
    """
    if color_choice == 'light':
        return '#FFFFFF', '#606367'
    elif color_choice == 'dark':
        return '#757575', '#E8D4D4'
    else:
        return form['background'], form['font']


def calculate_image_in_column():
    if session['imageQty'] % (session['columns'] + 1) < 2:
        session['imageInAColumn'] = session['imageQty'] // (session['columns'] + 1)
    else:
        if session['imageQty'] == 6:
            session['imageInAColumn'] = session['imageQty'] // (session['columns'] + 1)
        else:
            session['imageInAColumn'] = math.ceil(session['imageQty'] / (session['columns'] + 1))


def append_menu_items_and_content():
    """
       Append menu items and content based on the number of menu elements.
    """
    for i in range(1, session['menuElementsQty'] + 1):
        session['menuItems'].append(request.form[f'menuItem{i}'])
        if i > 1:
            session['siteContent'].append(request.form[f'description{i}'])

    # dla drugiego języka
    if session['is_second_language']:
        for i in range(1, session['menuElementsQty'] + 1):
            session['menuItems_l2'].append(request.form[f'menuItem{i}_l2'])
            if i > 1:
                session['siteContent_l2'].append(request.form[f'description{i}_l2'])

def create_files_list():
    """
    Save uploaded images.
    session['secure_filenames'] is a list of filenames.
    session['names'] is a list of filenames formatted to names displayed on the template.
    """
    filenames = []
    session['names'] = []
    session['secure_filenames'] = []
    images = request.files.getlist('image')

    if not os.path.exists(session['IMAGE_UPLOADS']):
        os.makedirs(session['IMAGE_UPLOADS'])

    for image in images:
        filename = secure_filename(image.filename)
        image.save(os.path.join(session['IMAGE_UPLOADS'], filename))
        filenames.append(filename)

    session['imageQty'] = len(images)
    session['names'] = sorted([
        # For each filename in the list:
        # 1. Split the filename at the first period ('.') and take the part before it
        # 2. Replace underscores ('_') with spaces (' ')
        # 3. Replace hyphens ('-') with spaces (' ')
        # 4. Collect all processed names into a list
        name.split('.', 1)[0].replace("_", " ").replace("-", " ")
        for name in filenames
        # Sort the processed list of names alphabetically
    ])
    session['secure_filenames'] = sorted(filenames)
    session.modified = True


def handle_languages():
    session['language'] = request.form['language']
    session['is_second_language'] = bool(request.form.get('secondLanguage'))

    # Handle None or empty second_language
    if not session['is_second_language']:
        session['secondLanguage'] = None
        session['menuItems_l2'] = None
        session['siteContent_l2'] = None

    else:
        session['secondLanguage'] = request.form.get('secondLanguage')
        session['menuItems_l2'] = []
        session['siteContent_l2'] = []

    print(session)
    session.modified = True


def save_templates():
    """
    Save generated portfolio templates based on the number of menu elements.
    """
    template_mapping = {
        1: ['mainPage.html'],
        2: ['mainPage.html', 'secondPage.html'],
        3: ['mainPage.html', 'secondPage.html', 'thirdPage.html'],
        4: ['mainPage.html', 'secondPage.html', 'thirdPage.html', 'fourthPage.html']
    }
    for page_name in template_mapping.get(session['menuElementsQty'], []):
        save_template(page_name)

    if session.get('is_second_language'):
        template_mapping = {
            1: ['mainPage_l2.html'],
            2: ['mainPage_l2.html', 'secondPage_l2.html'],
            3: ['mainPage_l2.html', 'secondPage_l2.html', 'thirdPage_l2.html'],
            4: ['mainPage_l2.html', 'secondPage_l2.html', 'thirdPage_l2.html', 'fourthPage_l2.html']
        }
        for page_name in template_mapping.get(session['menuElementsQty'], []):
            save_template(page_name)


def save_template(page_name):
    """
    Save generated portfolio templates.
    """
    if page_name == 'mainPage.html':
        main_name = page_name
        name = 'index.html'
        page_template = render_template(main_name,
                                        imageFolder=session['IMAGE_UPLOADS_IMG_PATH'],
                                        filenamesNames=zip(session['secure_filenames'], session['names']),
                                        filenamesNames2=zip(session['secure_filenames'], session['names']),
                                        imageInAColumn=session['imageInAColumn'],
                                        menuItems=session['menuItems'],
                                        menuElementsQty=session['menuElementsQty'],
                                        imageQty=session['imageQty'],
                                        columns=session['columns'],
                                        portfolioName=session['portfolioName'],
                                        language=session['language'],
                                        secondLanguage=session['secondLanguage'],
                                        backgroundColor=session['backgroundColor'],
                                        fontColor=session['fontColor'])

        page_template = page_template.replace(session['IMAGE_UPLOADS_IMG_PATH'], "static/img")
        page_template = page_template.replace(
            '<div class="preview"><p>To jest podgląd.</p><a href="/19_rajh/bragger/form"><button class="button">Chcę coś jeszcze zmienić!</button></a><a href="/19_rajh/bragger/end"><button class="button">Pobierz paczkę</button></a><a href="/19_rajh/bragger/delete"><button class="button">Zabierz mnie do instrukcji</button></a></div>',
            "")

    elif page_name == 'mainPage_l2.html':
        main_name = page_name
        name = 'index.html'
        page_template = render_template(main_name,
                                        imageFolder=session['IMAGE_UPLOADS_IMG_PATH'],
                                        filenamesNames=zip(session['secure_filenames'], session['names']),
                                        filenamesNames2=zip(session['secure_filenames'], session['names']),
                                        imageInAColumn=session['imageInAColumn'],
                                        menuItems_l2=session['menuItems_l2'],
                                        menuElementsQty=session['menuElementsQty'],
                                        imageQty=session['imageQty'],
                                        columns=session['columns'],
                                        portfolioName=session['portfolioName'],
                                        language=session['language'],
                                        secondLanguage=session['secondLanguage'],
                                        backgroundColor=session['backgroundColor'],
                                        fontColor=session['fontColor'])

        page_template = page_template.replace(session['IMAGE_UPLOADS_IMG_PATH'], "static/img")
        page_template = page_template.replace(
            '<div class="preview"><p>To jest podgląd.</p><a href="/19_rajh/bragger/form"><button class="button">Chcę coś jeszcze zmienić!</button></a><a href="/19_rajh/bragger/end"><button class="button">Pobierz paczkę</button></a><a href="/19_rajh/bragger/delete"><button class="button">Zabierz mnie do instrukcji</button></a></div>',
            "")
    else:
        page_template = render_template(page_name,
                                        menuItems=session['menuItems'],
                                        menuItems_l2=session['menuItems_l2'],
                                        menuElementsQty=session['menuElementsQty'],
                                        backgroundColor=session['backgroundColor'],
                                        fontColor=session['fontColor'],
                                        language=session['language'],
                                        secondLanguage=session['secondLanguage'],
                                        siteContent=session['siteContent'],
                                        siteContent_l2=session['siteContent_l2'],
                                        portfolioName=session['portfolioName'])

    page_template = page_template.replace('mainPage.html', 'index.html')
    path = os.path.join(session['DOWNLOAD_FOLDER'], page_name)
    with open(path, 'w', encoding='utf-8') as f:
        f.write(page_template)
        f.close()


def delete_old_directories():
    """
    Delete directories older than one day.
    """
    path = '/home/epi/19_rajh/Bragger/static/templates'
    if os.path.exists(path):
        for directory in os.listdir(path):
            old_folder = os.path.join(path, directory)
            if time.time() - float(directory) > 86400:
                shutil.rmtree(old_folder)


def clear_session():
    """
    Clear all session variables related to the portfolio.
    """
    keys_to_clear = [
        'portfolioName', 'backgroundColor', 'fontColor', 'columns',
        'language', 'secondLanguage', 'menuElementsQty', 'menuItems', 'menuItems_l2',
        'siteContent', 'siteContent_l2', 'imageQty', 'imageInAColumn', 'IMAGE_UPLOADS',
        'DOWNLOAD_FOLDER', 'IMAGE_UPLOADS_IMG_PATH', 'filenames', 'names', 'secure_filenames'
    ]
    for key in keys_to_clear:
        session.pop(key, None)
    session.modified = True


if __name__ == "__main__":
    app.run(host='0.0.0.0', port=5121, debug=True)
