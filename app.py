# -*- coding: utf-8 -*-
import os
from flask import Flask, request, render_template
from utils import *
from werkzeug.utils import secure_filename
import time
from flask import send_file
import urllib,urllib2

"""
"" Created by Julio César 27/02/2017.
"""

# Path donde se guardaran los archivos subidos, !Cambiar a un directorio existente!
UPLOAD_FOLDER = '/tmp'

# Configuracion de la app
app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER


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

                # Subir archivo local
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
            try:
                r = urllib2.urlopen(url)
                if str(r.getcode()) == '200':
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
            except urllib2.URLError, err:

                return render_template('alert.html', error_url=err, url=url)

    return render_template('form.html')


@app.route('/file/<filename>', methods=['GET'])
def return_file(filename):
    # Descargar archivos subidos al directorio UPLOAD_FOLDER
    try:
        return send_file(UPLOAD_FOLDER + "/" + str(filename))
    except Exception as e:
        return str(e)

if __name__ == '__main__':
    app.secret_key = 'dasdx45345'
    port = int(os.environ.get('PORT', 4545))
    app.run(host='0.0.0.0', port=port, debug=True)
