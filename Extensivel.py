# Trabalho Final da disciplina de Banco de Dados 2
# Professor: Marcos Roberto Ribeiro
# Aluno: Gustavo Silveira Dias 

# Implementação do Hash Extensível 

import sys
import csv
import numpy as np
import time

SIZE_PAGE = 4096  # Tamanho da página padrão
FILE_NAME = 'arquivo.csv'  # Nome do arquivo utilizado

# Criação de registro
def create_record(record=None):
    if record is None:
        record = [[], []]
    key = int(record[0])
    return key, record[1:]

def size_record(record):
    return sys.getsizeof(record[0]) + sum(sys.getsizeof(x) for x in record[1])

def str_record(record):
    if isinstance(record, tuple):
        return f"{record[0]}:{record[1]}"
    return "No key found." if record is not None else "Invalid record."

def get_key(record):
    return record[0]

# Criação de bucket
def create_bucket(size=1024, depth=2):
    return {
        'depth': depth,
        'size': size,
        'records': []
    }

def str_bucket(bucket):
    records_str = ", ".join(str_record(r) for r in bucket['records'])
    return f"| Depth: {bucket['depth']} | {records_str} |"

def size_bucket(bucket):
    return sum(size_record(r) for r in bucket['records'])

def is_empty(bucket):
    return not bucket['records']

def is_full(bucket):
    return size_bucket(bucket) >= bucket['size']

def insert_into_bucket(bucket, element):
    if not is_full(bucket):
        bucket['records'].append(element)
    else:
        bucket['records'].append(element)
        bucket['depth'] += 1
        new_bucket = create_bucket(bucket['size'], bucket['depth'])
        return new_bucket
    return None

# Criação do hash extensível
def create_hash_extensible(bucket_size=1024):
    global_depth = 2
    buckets = [create_bucket(bucket_size) for _ in range(2 ** global_depth)]
    return {
        'global_depth': global_depth,
        'bucket_size': bucket_size,
        'buckets': buckets
    }

def search_hash(hash_table, key):
    index = key % (2 ** hash_table['global_depth'])
    bucket = hash_table['buckets'][index]
    for pos, record in enumerate(bucket['records']):
        if get_key(record) == key:
            return pos, bucket
    return None, None

def remove_from_hash(hash_table, key):
    pos, bucket = search_hash(hash_table, key)
    if pos is not None:
        return bucket['records'].pop(pos)
    return None

def insert_into_hash(hash_table, record):
    key = get_key(record)
    index = key % (2 ** hash_table['global_depth'])
    bucket = hash_table['buckets'][index]
    new_bucket = insert_into_bucket(bucket, record)

    if new_bucket:
        if new_bucket['depth'] > hash_table['global_depth']:
            hash_table['global_depth'] += 1
            buckets = hash_table['buckets']
            hash_table['buckets'] = buckets + buckets

        rehash(bucket, hash_table)

def rehash(bucket, hash_table):
    for record in bucket['records']:
        key = get_key(record)
        index = key % (2 ** hash_table['global_depth'])
        insert_into_bucket(hash_table['buckets'][index], record)
    bucket['records'].clear()

def display_hash_table(hash_table):
    return "\n".join(f"Index {i}: {str_bucket(bucket)}" for i, bucket in enumerate(hash_table['buckets']))

# Leitura de argumentos de entrada
def parse_arguments():
    import argparse
    parser = argparse.ArgumentParser(description='Hash Extensível')
    parser.add_argument('-p', '--page_size', type=int, default=SIZE_PAGE, help='Tamanho máximo da página')
    parser.add_argument('-f', '--file', type=str, default=FILE_NAME, help='Arquivo de entrada')
    return parser.parse_args()

# Função principal
if __name__ == '__main__':
    args = parse_arguments()
    with open(args.file, 'r') as file:
        reader = csv.reader(file)
        hash_table = create_hash_extensible(args.page_size)

        for row in reader:
            op, *values = row
            if op == '+':
                record = create_record([int(v) for v in values])
                insert_into_hash(hash_table, record)
            elif op == '-':
                remove_from_hash(hash_table, int(values[0]))

    print(display_hash_table(hash_table))
