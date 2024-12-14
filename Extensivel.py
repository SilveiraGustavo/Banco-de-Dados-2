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