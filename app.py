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


# Lee el archvio txt dado la ruta lo condifica como UTF-8 luego obtiene un diccionario con con cada una de las palabras
# donde la palabra es la llave y el valor el numero de veces que se repite.
def get_words_dict(path):

    w_dic = {}
    with codecs.open(path, encoding='utf-8') as f:
        words = [clean_word(word) for line in f for word in line.split()]
        c = Counter(words)
        for word, count in c.items():
            w_dic[word] = count

    return w_dic


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

        # Verificar si en la peticion POST esta el archivo 'file'
        if 'file' not in request.files:
            flash('No file part')
            return redirect(request.url)
        file_p = request.files['file']

        # Si no se selecciona un archivo es porque el nombre esta vacio, entonces se redirecciona al formulario.
        if file_p.filename == '':
            return redirect(request.url)
        else:
            # Caso contratrio se comprueba que el archivo este permitido, si no, mostrar una alerta.
            if not allowed_file(file_p.filename):
                return render_template('alert.html', filename=file_p.filename)

        # Verificar que el nombre este en el formato permitido en ALLOWED_EXTENSIONS
        if file_p and allowed_file(file_p.filename):

            # Limpiar el nombre del archivo
            filename = secure_filename(file_p.filename)

            # Guardar archivo en el directorio definido
            path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            file_p.save(path)

            # Obtener las palabras con su cuenta respectiva en un dicionario llave-valor
            words = get_words_dict(path)

            # Organizar por ocurrencia y orden alfabetico
            words_result_sorted = sort_words_dict(words)

            # Buscar una palabra dada
            search_key = request.form['buscar-palabra'].upper()
            search_result = word_search(search_key, words)

            end_time = time.time() - start_time

        return render_template('response.html', words_result=words_result_sorted, search_key=search_key,
                               search_result=search_result, filename=filename, benchmark=end_time)
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
