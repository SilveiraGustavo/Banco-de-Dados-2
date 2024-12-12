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
