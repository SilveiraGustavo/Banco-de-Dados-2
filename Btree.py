import sys
import csv
import time
import argparse

PAGE_SIZE_DEFAULT = 4096  # change page size here
FILE_DEFAULT = "arquivo1.csv"  # change test file here

class Record:
    def __init__(self, fields=None):
        if fields is None:
            fields = [[], []]
        self.key = int(fields[0])
        self.record_fields = fields[1:]

    def get_key(self):
        return self.key

    def size(self):
        key_size = sys.getsizeof(self.key)
        fields_size = sum(sys.getsizeof(x) for x in self.record_fields)
        return key_size + fields_size

    def format(self):
        return "{k}:{c}".format(k=self.key, c=self.record_fields)

    def get_record(self):
        return self.key, self.record_fields


class Page:
    def __init__(self, leaf=False, page_size=4096):
        self.leaf = leaf
        self.page_size = page_size
        self.records = []
        self.keys = []
        self.children = []
        self.right_sibling = None
        self.left_sibling = None

    def is_leaf(self):
        return self.leaf

    def page_size(self):
        if self.is_leaf():
            return sum(sys.getsizeof(x) for x in self.records)
        else:
            return sys.getsizeof(self.children) + sum(sys.getsizeof(x) for x in self.keys)

    def is_empty(self):
        if self.is_leaf():
            return not self.records
        else:
            return not self.keys

    def is_full(self):
        if not self.is_empty():
            if self.is_leaf():
                return (self.page_size - self.page_size()) < sys.getsizeof(self.records[0])
            else:
                free_space = self.page_size() - self.page_size()
                return free_space <= (sys.getsizeof(self.keys) / len(self.keys)) + sys.getsizeof(self.children) / len(self.children)

    def find_child(self, key):
        if not self.is_leaf():
            pos = -1
            for x in self.keys:
                pos += 1
                if key < x:
                    return self.children[pos]
            return self.children[pos + 1]
        else:
            return None

    def insert_in_page(self, element):
        if self.is_leaf():
            if not self.is_full():
                self.records.append(element)
                self.records.sort(key=lambda x: x.get_key())


class BPlusTree:
    def __init__(self, page_size=PAGE_SIZE_DEFAULT):
        self.root = Page(leaf=True, page_size=page_size)
        self.page_size = page_size

    def search_node(self, page, k):
        if page.is_leaf():
            return page
        return self.search_node(page.find_child(k), k)

    def search_range(self, k1, k2):
        page = self.search_node(self.root, k1)
        outside_range = False
        interval_list = []

        while not outside_range:
            for x in page.records:
                if k1 <= x.get_key() <= k2:
                    interval_list.append(x.get_key())

            if not outside_range:
                page = page.right_sibling

            if page is None:
                break

        return interval_list

    def search_record(self, k):
        page = self.search_node(self.root, k)
        record = None
        for x in page.records:
            if x.get_key() == k:
                record = x
        return record, page

    def insert_leaf(self, N, element):
        if len(N.records) >= self.page_size:
            M = Page(leaf=True, page_size=self.page_size)
            M.records = N.records[(len(N.records) // 2):]
            N.records = N.records[:(len(N.records) // 2)]
            M.right_sibling = None
            M.left_sibling = None
            KM = M.records[0].get_key()

            if element.get_key() < KM:
                N.records.append(element)
            else:
                M.records.append(element)

            return KM, M
        else:
            N.records.append(element)
            N.records.sort(key=lambda x: x.get_key())

            return None, None

    def insert(self, page, element):
        if page.is_leaf():
            key, new_page = self.insert_leaf(page, element)
            return key, new_page
        else:
            child = page.find_child(element.get_key())
            key, right_child = self.insert(child, element)

        if key is not None and right_child is not None:
            if not page.is_full():
                pos = -1
                for x in page.keys:
                    pos += 1
                    if key < x:
                        page.keys.insert(pos, key)
                        page.children.insert(pos + 1, right_child)
                        return None, None

                page.keys.insert(pos + 1, key)
                page.children.insert(pos + 2, right_child)
                return None, None
            else:
                mid = len(page.children) // 2 + 1 if len(page.keys) % 2 == 0 else len(page.children) // 2

                M = Page(leaf=False, page_size=self.page_size)
                M.keys = page.keys[(len(page.keys) // 2):]
                KM = M.keys.pop(0)
                M.children = page.children[mid:]
                page.keys = page.keys[:(len(page.keys) // 2)]
                page.children = page.children[:mid]

                return KM, M

        return None, None

    def insert_root(self, element):
        key, new_page = self.insert(self.root, element)

        if key is not None and new_page is not None:
            new_root = Page(leaf=False, page_size=self.page_size)
            new_root.keys = [key]
            new_root.children = [self.root, new_page]
            self.root = new_root



if __name__ == '__main__':
    

    def get_arguments(print_help=False):
        parser = argparse.ArgumentParser('BPlusTree')
        parser.add_argument('-ps', '--page_size', action='store', type=int,
                            default=PAGE_SIZE_DEFAULT,
                            help='Maximum page size (default: ' +
                                 str(PAGE_SIZE_DEFAULT) + ')')
        parser.add_argument('-f', '--filename', action='store', type=str,
                            default=FILE_DEFAULT,
                            help='Input filename (default: ' +
                                 FILE_DEFAULT + ')')
        args = parser.parse_args()
        if print_help:
            parser.print_help()
        return args

    args = get_arguments()
    with open(args.filename) as FILE_DEFAULT:
        data = csv.DictReader(FILE_DEFAULT)
        b_plus_tree = BPlusTree(page_size=args.page_size)

        count = 0
        for row in data:
            operation = list(row.values())
            if operation[0] == "+":
                count += 1
                aux = [int(a) for a in operation[1:]]
                aux = Record(fields=aux)
                b_plus_tree.insert_root(aux)

                if count == 1072:
                    print(count)

    print("\nTree successfully created! Select an option from the menu:")

    while True:
        choice = int(input(
            "---Menu:---\n1) Search Element.\n2) Search Range.\n3) Show Tree.\n4) Exit.\n"))
        if choice == 1:
            search_key = int(input("Enter the key to search: "))
            result, page = b_plus_tree.search_record(search_key)
            if result:
                print("Record found: ", result.format())
            else:
                print("Element not found.")
        elif choice == 2:
            k1 = int(input("Enter the start value of the range: "))
            k2 = int(input("Enter the end value of the range: "))
            results = b_plus_tree.search_range(k1, k2)
            if results:
                print("Elements in the range: ", results)
            else:
                print("No elements found in the range.")
        elif choice == 3:
            print("\n------------ B+ Tree -------------\n\n", b_plus_tree.root)
        elif choice == 4:
            break
        else:
            print("Invalid attempt! Try again!")
