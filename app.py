# -*- coding: utf-8 -*-
import os
from flask import Flask, request, render_template
from utils import *
from currency import convert
from werkzeug.utils import secure_filename
import time
from flask import send_file
import urllib2

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

                return render_template('response.html', words_result=words_result_sorted, show=True, search_key=search_key,
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

                    return render_template('response.html', url=url, words_result=words_result_sorted, show=True,
                                           search_key=search_key, search_result=search_result, benchmark=end_time)
            except urllib2.URLError, err:

                return render_template('alert.html', error_url=err, url=url)

        if request.form['en'] != '':

            search_key = request.form['buscar-palabra'].upper()
            search_key_words = search_key.split()

            c_from = 0
            c_to = 0

            if len(search_key_words) == 4:

                c_from = str(search_key_words[1])
                c_to = str(search_key_words[3])

            elif len(search_key_words) == 3:

                c_from = str(search_key_words[1])
                c_to = str(search_key_words[2])

            try:

                amount = float(search_key_words[0])
                c_amount = convert(c_from, c_to, amount)
            except Exception as error_c:

                return render_template('alert.html', error_c=error_c, search_key=search_key)

            print float(c_amount)

            show=False

            return render_template('response.html', show=show, amount=amount,c_from=c_from,c_to=c_to, c_amount=c_amount)

    return render_template('form.html')


@app.route('/currency', methods=['GET', 'POST'])
def convert_currency():
    if request.method == 'POST':
        amount = float(request.form['amount'])
        c_from = str(request.form.get('c_from'))
        c_to = str(request.form.get('c_to'))
        c_amount = convert(c_from, c_to, amount)

        show = False

        return render_template('response.html', show=show, amount=amount, c_from=c_from, c_to=c_to, c_amount=c_amount)

    return render_template('currency_form.html')


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
