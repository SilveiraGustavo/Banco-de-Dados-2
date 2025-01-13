# -*- coding: utf-8 -*-
# Final Project for Database Course
# Professor: Marcos Roberto Ribeiro

# Application: Extendible Hashing

import sys
import csv
import numpy as np
import time

start_time = time.time()

PAGE_SIZE_DEFAULT = 4096  # Change the page size here
FILE_DEFAULT = "arquivo1.csv"  # Change the test file here

# ---------------------------------------------------------------------------------------
# Record implementation
def create_record(fields=None):
    if fields is None:
        fields = [[], []]
    key = int(fields[0])
    fields = fields[1:]
    return key, fields

def record_size(record):
    return sys.getsizeof(record[0]) + sum(sys.getsizeof(x) for x in record[1])

def record_to_str(record):
    if record is not None and isinstance(record, tuple):
        return "{k}:{c}".format(k=record[0], c=record[1])
    elif record is not None and isinstance(record, int):
        return str(record)
    else:
        return "Key not found!"

def get_key(record):
    return record[0]

def get_record(record):
    return record

# ---------------------------------------------------------------------------------------
# Bucket implementation
def create_bucket(bucket_size=1024, depth=2):
    return {
        'depth': depth,
        'bucket_size': bucket_size,
        'records': []
    }

def bucket_to_str(bucket):
    aux = "|Depth:{} ".format(bucket['depth'])
    for x in bucket['records']:
        aux += "(" + record_to_str(x) + ") , "
    return aux + "| "

def bucket_size(bucket):
    return sum(sys.getsizeof(x) for x in bucket['records'])

def is_empty(bucket):
    return not bucket['records']

def is_full(bucket):
    if is_empty(bucket):
        return False
    else:
        return (bucket['bucket_size'] - bucket_size(bucket)) < record_size(bucket['records'][0])

def insert_into_bucket(bucket, element, ignore=False):
    if not is_full(bucket):
        bucket['records'].append(element)
        return None
    else:
        bucket['records'].append(element)
        if not ignore:
            bucket['depth'] += 1
            new_bucket = create_bucket(bucket['bucket_size'], bucket['depth'])
            return new_bucket
        return None

# ---------------------------------------------------------------------------------------
# Extendible Hash implementation
def create_extendible_hash(bucket_size=1024):
    global_depth = 2
    bucket_list = [create_bucket(bucket_size) for _ in range(2 ** global_depth)]

    return {
        'global_depth': global_depth,
        'bucket_size': bucket_size,
        'bucket_list': bucket_list
    }

def remove_from_hash(ext_hash, key):
    pos, target_bucket = search_in_hash(ext_hash, key)
    if pos is not None and target_bucket is not None:
        return target_bucket['records'].pop(pos)
    else:
        return None

def search_in_hash(ext_hash, key):
    hash_key = key % (2 ** ext_hash['global_depth'])
    prev_depth = ext_hash['global_depth']
    current_depth = ext_hash['bucket_list'][hash_key]['depth']

    while prev_depth > current_depth:
        prev_depth = current_depth
        hash_key = key % (2 ** current_depth)
        current_depth = ext_hash['bucket_list'][hash_key]['depth']

    target_bucket = ext_hash['bucket_list'][hash_key]
    position = next((i for i, record in enumerate(target_bucket['records']) if get_key(record) == key), None)
    return position, target_bucket if position is not None else (None, None)

def insert_into_hash(ext_hash, element):
    hash_key = get_key(element) % (2 ** ext_hash['global_depth'])
    new_bucket = insert_into_bucket(ext_hash['bucket_list'][hash_key], element)

    if new_bucket is not None:
        if new_bucket['depth'] > ext_hash['global_depth']:
            ext_hash['global_depth'] += 1
            prev_divisor = 2 ** (ext_hash['global_depth'] - 1)
            curr_divisor = 2 ** ext_hash['global_depth']
            ext_hash['bucket_list'].extend(ext_hash['bucket_list'][:prev_divisor])

            prev_depth = new_bucket['depth'] - 1
            first_index = get_key(element) % (2 ** prev_depth) + (2 ** prev_depth)
            ext_hash['bucket_list'][first_index] = new_bucket
            step = 2 ** (ext_hash['global_depth'] - new_bucket['depth'])

            for i in range(1, step):
                ext_hash['bucket_list'][first_index + i * (2 ** new_bucket['depth'])] = new_bucket

            overflow_records = ext_hash['bucket_list'][hash_key]['records'][:]
            ext_hash['bucket_list'][hash_key]['records'] = []
            handle_overflow(ext_hash, overflow_records)

def handle_overflow(ext_hash, records):
    mod_value = 2 ** ext_hash['global_depth']
    for record in records:
        new_hash_key = get_key(record) % mod_value
        insert_into_bucket(ext_hash['bucket_list'][new_hash_key], record, ignore=True)

def extendible_hash_to_str(ext_hash):
    result = ""
    for idx, bucket in enumerate(ext_hash['bucket_list']):
        result += "Index {} --> {}\n".format(idx, bucket_to_str(bucket))
    return result

def get_arguments(show_help=False):
    import argparse
    parser = argparse.ArgumentParser('ExtendibleHash')
    parser.add_argument('-p', '--pageSize', type=int, default=PAGE_SIZE_DEFAULT, help=f'Page size (default: {PAGE_SIZE_DEFAULT})')
    parser.add_argument('-f', '--filename', type=str, default=FILE_DEFAULT, help=f'Input file (default: {FILE_DEFAULT})')
    args = parser.parse_args()
    if show_help:
        parser.print_help()
    return args

if __name__ == '__main__':
    args = get_arguments()
    with open(args.filename) as file:
        data_reader = csv.DictReader(file)
        main_hash = create_extendible_hash(args.pageSize)
        op_count = 0

        for row in data_reader:
            operation = list(row.values())
            if operation[0] == "+":
                op_count += 1
                values = [int(v) for v in operation[1:]]
                record = create_record(values)
                insert_into_hash(main_hash, record)
            elif operation[0] == "-":
                op_count += 1
                remove_from_hash(main_hash, int(operation[1]))

    elapsed_time = time.time() - start_time
    print('Operations completed in {:.4f} seconds'.format(elapsed_time))

    while True:
        choice = int(input("--- Menu ---\n1) Search Element\n2) Remove Element\n3) Show Hash\n4) Exit\n"))
        if choice == 1:
            key = int(input("Enter key to search: "))
            record, bucket = search_in_hash(main_hash, key)
            if record is not None:
                print(f"Found element: {record_to_str(bucket['records'][record])} in bucket {bucket}")
            else:
                print("Element not found!")
        elif choice == 2:
            key = int(input("Enter key to remove: "))
            removed = remove_from_hash(main_hash, key)
            if removed:
                print(f"Removed element: {record_to_str(removed)}")
            else:
                print("Element not found!")
        elif choice == 3:
            print("\n--- Extendible Hash ---\n", extendible_hash_to_str(main_hash))
        elif choice == 4:
            break
        else:
            print("Invalid option! Try again!")
