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
        session['imgCrop'] = request.form['imgCrop']

        handle_background_display()
        handle_languages()

        session['menuElementsQty'] = int(request.form['menuElements'])
        session['menuItems'] = []
        session['siteContent'] = []
        append_menu_items_and_content()
        create_files_list()
        calculate_image_in_column()

        save_templates()
        return redirect('mainPage.html')


@app.route('/mainPage.html')
def mainPage():
    if not session.get("uploaded_files"):
        return redirect("form")
    return render_template('mainPage.html',
                           imageFolder=session['IMAGE_UPLOADS_IMG_PATH'],
                           files=session['uploaded_files'],
                           imageInAColumn=session['imageInAColumn'],
                           background_img=session['background_img'],
                           background_display=session['background_display'],
                           menuItems=session['menuItems'],
                           menuElementsQty=session['menuElementsQty'],
                           imageQty=session['imageQty'],
                           columns=session['columns'],
                           imgCrop=session['imgCrop'],
                           portfolioName=session['portfolioName'],
                           language=session['language'],
                           secondLanguage=session['secondLanguage'],
                           backgroundColor=session['backgroundColor'],
                           fontColor=session['fontColor'])


@app.route('/secondPage.html')
def secondPage():
    return render_template('secondPage.html',
                           imageFolder=session['IMAGE_UPLOADS_IMG_PATH'],
                           menuItems=session['menuItems'],
                           menuElementsQty=session['menuElementsQty'],
                           background_img=session['background_img'],
                           background_display=session['background_display'],
                           backgroundColor=session['backgroundColor'],
                           fontColor=session['fontColor'],
                           language=session['language'],
                           secondLanguage=session['secondLanguage'],
                           siteContent=session['siteContent'],
                           portfolioName=session['portfolioName'])


@app.route('/thirdPage.html')
def thirdPage():
    return render_template('thirdPage.html',
                           imageFolder=session['IMAGE_UPLOADS_IMG_PATH'],
                           menuItems=session['menuItems'],
                           menuElementsQty=session['menuElementsQty'],
                           background_img=session['background_img'],
                           background_display=session['background_display'],
                           backgroundColor=session['backgroundColor'],
                           fontColor=session['fontColor'],
                           language=session['language'],
                           secondLanguage=session['secondLanguage'],
                           siteContent=session['siteContent'],
                           portfolioName=session['portfolioName'])


@app.route('/fourthPage.html')
def fourthPage():
    return render_template('fourthPage.html',
                           imageFolder=session['IMAGE_UPLOADS_IMG_PATH'],
                           menuItems=session['menuItems'],
                           menuElementsQty=session['menuElementsQty'],
                           backgroundColor=session['backgroundColor'],
                           background_img=session['background_img'],
                           background_display=session['background_display'],
                           fontColor=session['fontColor'],
                           language=session['language'],
                           secondLanguage=session['secondLanguage'],
                           siteContent=session['siteContent'],
                           portfolioName=session['portfolioName'])


@app.route('/mainPage_l2.html')
def mainPage_l2():
    if not session.get('uploaded_files'):
        return redirect("form")
    return render_template('mainPage_l2.html',
                           imageFolder=session['IMAGE_UPLOADS_IMG_PATH'],
                           files=session['uploaded_files'],
                           background_img=session['background_img'],
                           background_display=session['background_display'],
                           imageInAColumn=session['imageInAColumn'],
                           menuItems_l2=session['menuItems_l2'],
                           menuElementsQty=session['menuElementsQty'],
                           imageQty=session['imageQty'],
                           columns=session['columns'],
                           imgCrop=session['imgCrop'],
                           portfolioName=session['portfolioName'],
                           language=session['language'],
                           secondLanguage=session['secondLanguage'],
                           backgroundColor=session['backgroundColor'],
                           fontColor=session['fontColor'])


@app.route('/secondPage_l2.html')
def secondPage_l2():
    return render_template('secondPage_l2.html',
                           imageFolder=session['IMAGE_UPLOADS_IMG_PATH'],
                           menuItems_l2=session['menuItems_l2'],
                           menuElementsQty=session['menuElementsQty'],
                           background_img=session['background_img'],
                           background_display=session['background_display'],
                           backgroundColor=session['backgroundColor'],
                           fontColor=session['fontColor'],
                           language=session['language'],
                           secondLanguage=session['secondLanguage'],
                           siteContent_l2=session['siteContent_l2'],
                           portfolioName=session['portfolioName'])


@app.route('/thirdPage_l2.html')
def thirdPage_l2():
    return render_template('thirdPage_l2.html',
                           imageFolder=session['IMAGE_UPLOADS_IMG_PATH'],
                           menuItems_l2=session['menuItems_l2'],
                           menuElementsQty=session['menuElementsQty'],
                           backgroundColor=session['backgroundColor'],
                           background_img=session['background_img'],
                           background_display=session['background_display'],
                           fontColor=session['fontColor'],
                           language=session['language'],
                           secondLanguage=session['secondLanguage'],
                           siteContent_l2=session['siteContent_l2'],
                           portfolioName=session['portfolioName'])


@app.route('/fourthPage_l2.html')
def fourthPage_l2():
    return render_template('fourthPage_l2.html',
                           imageFolder=session['IMAGE_UPLOADS_IMG_PATH'],
                           menuItems_l2=session['menuItems_l2'],
                           menuElementsQty=session['menuElementsQty'],
                           backgroundColor=session['backgroundColor'],
                           background_img=session['background_img'],
                           background_display=session['background_display'],
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
                                    files=session['uploaded_files'],
                                    imageInAColumn=session['imageInAColumn'],
                                    background_img=session['background_img'],
                                    background_display=session['background_display'],
                                    menuItems=session['menuItems'],
                                    menuElementsQty=session['menuElementsQty'],
                                    imageQty=session['imageQty'],
                                    columns=session['columns'],
                                    imgCrop=session['imgCrop'],
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
    #directory_static = '/home/epi/19_rajh/Bragger/static/staticTemplates/static'
    directory_static = '/mnt/c/Users/hania/Documents/studia/lic/static/staticTemplates/static'

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
    # Sprawdź, czy liczba obrazów jest zerowa lub ujemna
    if session['imageQty'] <= 0:
        session['imageInAColumn'] = 0
        return

    # Oblicz liczbę kolumn
    num_columns = session['columns'] + 2

    # Sprawdź, czy liczba kolumn jest większa niż liczba obrazów
    if num_columns >= session['imageQty']:
        # Każda kolumna dostaje jeden obraz, pozostałe kolumny pozostaną puste
        session['imageInAColumn'] = 1
        return

    # Oblicz liczbę obrazów na kolumnę
    # Podstawowa liczba obrazów na kolumnę
    base_count = session['imageQty'] // num_columns
    # Pozostałe obrazy, które muszą być równomiernie rozdzielone
    remainder = session['imageQty'] % num_columns

    # Jeśli są resztki, zwiększamy liczbę obrazów w kilku kolumnach
    session['imageInAColumn'] = base_count + (1 if remainder > 0 else 0)

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
    session['uploaded_files']:
        'file_path': file_path,
        'label': label
    """

    if not os.path.exists(session['IMAGE_UPLOADS']):
        os.makedirs(session['IMAGE_UPLOADS'])

    # Pobieranie etykiet
    file_labels = request.form.getlist('file_labels[]')

    # Przechowywanie plików
    uploaded_files = request.files.getlist('image')  # Pobieranie listy przesyłanych plików
    session['uploaded_files'] = []
    session['imageQty'] = len(uploaded_files)

    for i, file in enumerate(uploaded_files):
        if file:
            # Zapisz plik na dysku
            original_filename = secure_filename(file.filename)
            file_path = os.path.join(session['IMAGE_UPLOADS'], original_filename)
            file.save(file_path)

            # Pobierz etykietę dla pliku
            label = file_labels[i] if i < len(file_labels) and file_labels[i].strip() else 'Bez tytułu'

            # Dodaj informacje do sesji (lub przechowuj w bazie danych)
            session['uploaded_files'].append({
                'file_path': original_filename,
                'label': label
            })

    background_img = request.files.get('background_img')
    session['background_img'] = False
    if background_img and background_img.filename:
        file_path = os.path.join(session['IMAGE_UPLOADS'], 'background.png')
        background_img.save(file_path)
        session['background_img'] = True
    session.modified = True


def handle_languages():
    session['language'] = request.form['language']
    session['is_second_language'] = bool(request.form.get('secondLanguage'))

    # Handle None or empty second_language
    if not session['is_second_language']:
        session['secondLanguage'] = None
        session['menuItems_l2'] = []
        session['siteContent_l2'] = []

    else:
        session['secondLanguage'] = request.form.get('secondLanguage')
        session['menuItems_l2'] = []
        session['siteContent_l2'] = []

    session.modified = True


def handle_background_display():
    session['background_display'] = ''
    background_display = request.form.get('background_display', '')
    if background_display:
        if background_display == 'cover':
            session['background_display'] = 'background-repeat: no-repeat!important;background-attachment: fixed!important;background-size: cover!important;'
        elif background_display == 'repeat':
            session['background_display'] = ''
        elif background_display == 'stretch':
            session['background_display'] = 'background-repeat: no-repeat!important; background-attachment:fixed!important; background-size: 100% 100%!important;'
        else:
            session['background_display'] = ''

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
                                        files=session['uploaded_files'],
                                        imageInAColumn=session['imageInAColumn'],
                                        background_img=session['background_img'],
                                        background_display=session['background_display'],
                                        menuItems=session['menuItems'],
                                        menuElementsQty=session['menuElementsQty'],
                                        imageQty=session['imageQty'],
                                        columns=session['columns'],
                                        imgCrop=session['imgCrop'],
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
                                        files=session['uploaded_files'],
                                        imageInAColumn=session['imageInAColumn'],
                                        background_img=session['background_img'],
                                        background_display=session['background_display'],
                                        menuItems_l2=session['menuItems_l2'],
                                        menuElementsQty=session['menuElementsQty'],
                                        imageQty=session['imageQty'],
                                        columns=session['columns'],
                                        imgCrop=session['imgCrop'],
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
                                        imageFolder=session['IMAGE_UPLOADS_IMG_PATH'],
                                        menuItems=session['menuItems'],
                                        menuItems_l2=session['menuItems_l2'],
                                        menuElementsQty=session['menuElementsQty'],
                                        background_img=session['background_img'],
                                        background_display=session['background_display'],
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
        'siteContent', 'siteContent_l2', 'imageQty', 'imageInAColumn', 'IMAGE_UPLOADS', 'imgCrop',
        'DOWNLOAD_FOLDER', 'IMAGE_UPLOADS_IMG_PATH', 'filenames', 'names', 'uploaded_files', 'secure_filenames'
    ]
    for key in keys_to_clear:
        session.pop(key, None)
    session.modified = True


if __name__ == "__main__":
    app.run(host='0.0.0.0', port=5121, debug=True)