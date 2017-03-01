# -*- coding: utf-8 -*-
from collections import Counter
import unicodedata
import re
import codecs
import urllib
from bs4 import BeautifulSoup

"""
"" Created by Julio César 27/02/2017.
"""

# Extenciones de archivo permitidas.
ALLOWED_EXTENSIONS = set(['txt'])


def allowed_file(filename):
    # Metodo que obtiene el nombre del archivo en minusculas y solo con formato txt
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


def get_words_dict(c):

    w_dict = {}

    for word, count in c.items():
        w_dict[word] = count

    return w_dict


def get_words_txt(path):
    # Lee el archvio txt dado la ruta lo condifica como UTF-8 luego obtiene un diccionario con con cada
    # una de las palabras donde la palabra es la llave y el valor el numero de veces que se repite.
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

    w_dict = get_words_dict(c)

    del w_dict['']

    return w_dict


def sort_words_dict(word_dict):
    # Este metodo ordena un diccionario, primero lo covierte en una tupla luego ordena por valor y
    # finalmente por la llave en forma desendente.
    words_tuple = tuple(word_dict.iteritems())
    words_sorted = sorted(sorted(words_tuple, key=lambda x: x[0]), key=lambda x: x[1], reverse=True)[:10]

    print words_sorted

    return words_sorted


def word_search(key, word_dict):
    # Verifica si existe una llave el un diccionario dado

    if key in word_dict:
        res = word_dict[key]
    else:
        res = {}

    return res


def clean_word(word):
    # Este metodo toma cada palabra, elimina caracteres especiales y las tranforma a mayusculas.
    w = unicodedata.normalize('NFKD', word).encode('ASCII', 'ignore').upper()
    regex = re.compile('[^a-zA-Z]')
    # El primer parametro el un string vacio por el que se remplazara , el segundo la palabra en cuestion.
    w = regex.sub('', w)
    return w
