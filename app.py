# -*- coding: utf-8 -*-
import os
from flask import Flask, request, redirect, render_template, flash
from werkzeug.utils import secure_filename
from collections import Counter
import unicodedata
import re
import codecs
import time
from flask import send_file
import urllib
from bs4 import BeautifulSoup


# Path donde se guardaran los archivos subidos, !Cambiar a un directorio existente!
UPLOAD_FOLDER = '/Users/JulioC/PycharmProjects/flask-practice/media'

# Extenciones de archivo permitidas.
ALLOWED_EXTENSIONS = set(['txt'])


# Configuracion de la app
app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER


# Metodo que obtiene el nombre del archivo en minusculas y solo con formato txt
def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


def get_words_dict(c):

    w_dict = {}

    for word, count in c.items():
        w_dict[word] = count

    return w_dict


# Lee el archvio txt dado la ruta lo condifica como UTF-8 luego obtiene un diccionario con con cada una de las palabras
# donde la palabra es la llave y el valor el numero de veces que se repite.
def get_words_txt(path):

    with codecs.open(path, encoding='utf-8') as f:
        words = [clean_word(word) for line in f for word in line.split()]
        c = Counter(words)

    return get_words_dict(c)


def get_words_html(url):

    html = urllib.urlopen(url).read()
    soup = BeautifulSoup(html, "html.parser")

    # kill all script and style elements
    for script in soup(["script", "style"]):
        script.extract()  # rip it out

    # get text
    text = soup.get_text()
    # break into lines and remove leading and trailing space on each
    lines = (line.strip() for line in text.splitlines())
    # break multi-headlines into a line each
    chunks = (phrase.strip() for line in lines for phrase in line.split("  "))
    # drop blank lines
    text = '\n'.join(chunk for chunk in chunks if chunk)

    plain_words = text.split()

    c_plain = Counter(plain_words)

    # Transformar y contar cada una de las palabras similares
    c = Counter()
    for k, v in c_plain.items():
        c.update({clean_word(k): v})

    return get_words_dict(c)


# Este metodo ordena un diccionario, primero lo covierte en una tupla luego ordena por valor y finalmente por la llave.
# en forma desendente.
def sort_words_dict(word_dict):

    words_tuple = tuple(word_dict.iteritems())
    words_sorted = sorted(sorted(words_tuple, key=lambda x: x[0])[:10], key=lambda x: x[1], reverse=True)

    return words_sorted


# Busca si existe una llave el un diccionario dado
def word_search(key, word_dict):

    if key in word_dict:
        res = word_dict[key]
    else:
        res = {}

    return res


# Este metodo toma cada palabra, elimina caracteres especiales y las tranforma a mayusculas.
def clean_word(word):

    w = unicodedata.normalize('NFKD', word).encode('ASCII', 'ignore').upper()
    regex = re.compile('[^a-zA-Z]')
    # El primer parametro el un string vacio por el que se remplazara , el segundo la palabra en cuestion.
    w = regex.sub('', w)
    return w


@app.route('/', methods=['GET', 'POST'])
def upload_file():
    start_time = time.time()
    if request.method == 'POST':

        if request.files['file'].filename != '':

            file_p = request.files['file']

            # Verificar que el nombre este en el formato permitido en ALLOWED_EXTENSIONS
            if file_p and allowed_file(file_p.filename):

                # Limpiar el nombre del archivo
                filename = secure_filename(file_p.filename)

                # Guardar archivo en el directorio definido
                path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
                file_p.save(path)

                # Obtener las palabras con su cuenta respectiva en un dicionario llave-valor
                words = get_words_txt(path)

                # Organizar por ocurrencia y orden alfabetico
                words_result_sorted = sort_words_dict(words)

                # Buscar una palabra dada
                search_key = request.form['buscar-palabra'].upper()
                search_result = word_search(search_key, words)

                end_time = time.time() - start_time

                return render_template('response.html', words_result=words_result_sorted, search_key=search_key,
                                       search_result=search_result, filename=filename, benchmark=end_time)
            else:
                # Caso contratrio mostrar una alerta.
                return render_template('alert.html', error_file=file_p.filename)

        elif request.form['url'] != '':
            url = request.form['url']
            r = urllib.urlopen(url)
            if r.getcode() == '200':
                # Obtener las palabras con su cuenta respectiva en un dicionario llave-valor
                words = get_words_html(url)

                # Organizar por ocurrencia y orden alfabetico
                words_result_sorted = sort_words_dict(words)

                # Buscar una palabra dada
                search_key = request.form['buscar-palabra'].upper()
                search_result = word_search(search_key, words)

                end_time = time.time() - start_time

                return render_template('response.html', url=url, words_result=words_result_sorted,
                                       search_key=search_key, search_result=search_result, benchmark=end_time)

            else:

                return render_template('alert.html', error_url=r.getcode(), url=url)

    return render_template('form.html')


# Descargar archivos subidos al directorio UPLOAD_FOLDER
@app.route('/file/<filename>', methods=['GET'])
def return_file(filename):
    try:

        return send_file(UPLOAD_FOLDER + "/" + str(filename))
    except Exception as e:
        return str(e)

if __name__ == '__main__':
    app.secret_key = 'dasdx45345'
    app.run(debug=True, port=4545)
