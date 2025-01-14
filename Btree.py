# Trabalho Final da disciplina de Banco de Dados 2
# Professor: Marcos Roberto Ribeiro
# Aluno: Gustavo Silveira Dias 


import sys
import csv
import numpy as np
import time

Time = time.time()

size_page =  4096 # Definindo o tamanho da página em Bytes
file = "arquivo" # Definindo o arquivo que vai ser utilizado 

def create_record(Fields=None):
    if Fields is None:
        Fields = [[], []]
    Key = int(Fields[0])
    Fields_records = Fields[1:]
    return {'getKey': lambda: Key, 'record': Fields_records}

def size_record(record):
    Key_size = sys.getsizeof(record[0])
    Fields_size = sum(sys.getsizeof(x) for x in record[1])
    return Key_size + Fields_size

def format_record(record):
    return " {k}:{c}".format(k=record[0], c=record[1])

def get_key(record):
    return record[0]

def get_record(record):
    return record


def create_page(sheet=False, size_page=4096):
    return {
        'sheet' : sheet,
        'size_page' : size_page,
        'record' : [],
        'key' : [],
        'children' : [],
        'page_right' : None,
        'page_left' : None
    }

def sheet(page): 
    return page['sheet']

def size_page(page):
    if sheet(page):
        return sum (sys.getsizeof(x) for x in page['record'])
    else:
        return sys.getsizeof(page['children']) + sum(sys.getsizeof(x) for x in page['key'])

def is_empty(page):
    if sheet(page):
        return not page['record']
    else: 
        return not page['key']

def is_full(page):
    if not is_empty(page):
        if sheet(page):
            return (page['size_page'] -  size_page(page)) < sys.getsizeof(page['record'][0])
        else: 
            free = page['size_page'] -size_page(page)
            return free <= (sys.getsizeof (page['key']) / len (page['key']) +
                            sys.getsizeof (page['children']) / len (page['children']))

def search_children(page, key):
    if not sheet(page):
        pos = -1