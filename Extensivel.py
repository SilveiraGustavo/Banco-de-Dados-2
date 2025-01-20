# -*- coding: utf-8 -*-
# Final Project for Database Course
# Professor: Marcos Roberto Ribeiro

import sys
import csv
import time

PAGE_SIZE_DEFAULT = 4096  # Change the page size here
FILE_DEFAULT = "output.csv"  # Change the test file here

class Record:
    def __init__(self, key, fields=None):
        self.key = key
        self.fields = fields or []

    def size(self):
        return sys.getsizeof(self.key) + sum(sys.getsizeof(field) for field in self.fields)

    def __str__(self):
        return f"{self.key}:{self.fields}"


class Bucket:
    def __init__(self, bucket_size=1024, depth=2):
        self.depth = depth
        self.bucket_size = bucket_size
        self.records = []

    def is_empty(self):
        return not self.records

    def is_full(self):
        return self.bucket_size - self.size() < self.records[0].size() if self.records else False

    def size(self):
        return sum(record.size() for record in self.records)

    def insert(self, record, ignore_overflow=False):
        if not self.is_full():
            self.records.append(record)
            return None
        else:
            if not ignore_overflow:
                self.depth += 1
                return Bucket(self.bucket_size, self.depth)
            return None

    def remove(self, key):
        for i, record in enumerate(self.records):
            if record.key == key:
                return self.records.pop(i)
        return None

    def __str__(self):
        return f"|Depth:{self.depth} " + ", ".join(str(record) for record in self.records) + "|"


class ExtendibleHash:
    def __init__(self, bucket_size=1024):
        self.global_depth = 2
        self.bucket_size = bucket_size
        self.bucket_list = [Bucket(bucket_size) for _ in range(2 ** self.global_depth)]

    def _get_hash_key(self, key, depth=None):
        depth = depth if depth is not None else self.global_depth
        return key % (2 ** depth)

    def insert(self, record):
        hash_key = self._get_hash_key(record.key)
        new_bucket = self.bucket_list[hash_key].insert(record)

        if new_bucket:
            self._split_bucket(hash_key, record, new_bucket)

    def _split_bucket(self, hash_key, record, new_bucket):
        if new_bucket.depth > self.global_depth:
            self._double_directory()

        prev_depth = new_bucket.depth - 1
        first_index = self._get_hash_key(record.key, prev_depth) + (2 ** prev_depth)
        self.bucket_list[first_index] = new_bucket
        step = 2 ** (self.global_depth - new_bucket.depth)

        for i in range(1, step):
            self.bucket_list[first_index + i * (2 ** new_bucket.depth)] = new_bucket

        overflow_records = self.bucket_list[hash_key].records[:]
        self.bucket_list[hash_key].records = []
        self._handle_overflow(overflow_records)

    def _double_directory(self):
        self.global_depth += 1
        self.bucket_list.extend(self.bucket_list[:])

    def _handle_overflow(self, records):
        for record in records:
            new_hash_key = self._get_hash_key(record.key)
            self.bucket_list[new_hash_key].insert(record, ignore_overflow=True)

    def remove(self, key):
        hash_key = self._get_hash_key(key)
        return self.bucket_list[hash_key].remove(key)

    def search(self, key):
        hash_key = self._get_hash_key(key)
        for record in self.bucket_list[hash_key].records:
            if record.key == key:
                return record
        return None

    def __str__(self):
        return "\n".join(f"Index {i} --> {bucket}" for i, bucket in enumerate(self.bucket_list))


if __name__ == '__main__':
    start_time = time.time()
    with open(FILE_DEFAULT) as file:
        data_reader = csv.DictReader(file)
        main_hash = ExtendibleHash(PAGE_SIZE_DEFAULT)

        for row in data_reader:
            operation = list(row.values())
            if operation[0] == "+":
                values = [int(v) for v in operation[1:]]
                record = Record(values[0], values[1:])
                main_hash.insert(record)
            elif operation[0] == "-":
                main_hash.remove(int(operation[1]))

    elapsed_time = time.time() - start_time
    print('Operations completed in {:.4f} seconds'.format(elapsed_time))

    while True:
        choice = int(input("--- Menu ---\n1) Search Element\n2) Remove Element\n3) Show Hash\n4) Exit\n"))
        if choice == 1:
            key = int(input("Enter key to search: "))
            record = main_hash.search(key)
            print(f"Found: {record}" if record else "Element not found!")
        elif choice == 2:
            key = int(input("Enter key to remove: "))
            removed = main_hash.remove(key)
            print(f"Removed: {removed}" if removed else "Element not found!")
        elif choice == 3:
            print("\n--- Extendible Hash ---\n", main_hash)
        elif choice == 4:
            break
        else:
            print("Invalid option! Try again!")
