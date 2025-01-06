# Trabalho Final da disciplina de Banco de Dados 2
# Professor: Marcos Roberto Ribeiro
# Aluno: Gustavo Silveira Dias 

# Implementação do Hash Extensível 

import sys
import csv
import numpy as np
import time

size_page = 4096  # Definindo o tamanho da página 
files = 'Arquivo' # Definindo o arquivo que vai ser utilizado

def create_record(record=None):
    if record is None:
        record [[] , []]
    key = int(record[0])
    record = record[1:]
    return key, record

def size_record(record):
    return sys.getsizeof(record[0]) + sum(sys.getsizeof(x) for x in record[1])

def str_record(record):
    if record is not None and isinstance(record, tuple):
        return "{k}:{c}".format(k=record[0], c=record[1])
    elif record is not None and isinstance(record, int):
        return str(record)
    else:
        return "No key found."

def get_key(record):
    return record[0]

def get_record(record):
    return record

def create_bucket(sizeBucket =  1024, depth = 2):
    return {
        'depth':  depth,
        'sizeBucket': sizeBucket,
        'record': []
    }

def str_bucket(bucket):
    aux =  "depth: {}".format(bucket['depth'])
    for i in bucket['record']:
        aux = aux + "(" + str_record(i) + ")" + " , "
    return aux + "| "


def size_bucket(bucket):
    return sum(sys.getsizeof(i) for i in bucket['record'])

def empty(bucket): 
    return not bucket['record']

def full(bucket):
    if empty(bucket):
        return False
    else: 
        if (bucket['sizeBucket'] - size_bucket(bucket)) >= size_record(bucket['registros'][0]):
            return False
        else:
            return True


def Insert_into_bucket(bucket, element, ignore=False):
    if not full(bucket):
        bucket['record'].append(element)
        return None
    else: 
        bucket['record'].append(element)
        if not ignore:
            bucket['depth'] += 1
            new_bucket = create_bucket(bucket['sizeBucket'], bucket['depth'])
            return new_bucket
        return None