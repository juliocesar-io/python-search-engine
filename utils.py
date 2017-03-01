# -*- coding: utf-8 -*-
from collections import Counter
import unicodedata
import re
import urllib
import codecs
from bs4 import BeautifulSoup

"""
"" Created by Julio César 27/02/2017.
"""

# Extenciones de archivo permitidas.
ALLOWED_EXTENSIONS = set(['txt'])

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

    # Eliminar etiquetas de scripts y estilos.
    for script in soup(["script", "style"]):
        script.extract()  # rip it out

    # Obtener texto
    text = soup.get_text()
    # Eliminar espacios en blanco
    lines = (line.strip() for line in text.splitlines())
    chunks = (phrase.strip() for line in lines for phrase in line.split("  "))
    text = '\n'.join(chunk for chunk in chunks if chunk)

    # Obener lista de palabras
    plain_words = text.split()

    # Contar palabras de la lista
    c_plain = Counter(plain_words)

    # Transformar y contar cada una de las palabras similares (incluyendo acentos, mayus/min.)
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
