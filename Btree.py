# Implementação de Árvore B+
# Disciplina: Banco de Dados 2
# Alunos: Gustavo Silveira Dias e Bruno Augusto de Oliveira
# Curso: Engenharia de Computação
# Professor: Marcos Roberto

import sys
import csv
import time
import argparse

PAGE_SIZE_DEFAULT = 4096  # Tamanho da página
FILE_DEFAULT = "output.csv"  # Arquivo padrão de teste

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

    def __repr__(self):
        if self.is_leaf():
            records = [r.get_key() for r in self.records]
            return f"LeafPage(keys={records}, right_sibling={'None' if self.right_sibling is None else 'Exists'})"
        else:
            keys = self.keys
            children = len(self.children)
            return f"InternalPage(keys={keys}, children_count={children})"


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

    def remove(self, page, key):
        if page.is_leaf():
            # Remove o elemento na página folha
            for i, record in enumerate(page.records):
                if record.get_key() == key:
                    page.records.pop(i)
                    return True
            return False  # Chave não encontrada
        else:
            # Localiza o filho correto e tenta remover o elemento
            child = page.find_child(key)
            removed = self.remove(child, key)
            if removed and len(child.records) < self.page_size // 2:
                self.rebalance(page, child)
            return removed

    def rebalance(self, parent, child):
        index = parent.children.index(child)

        # Tenta redistribuir com o irmão esquerdo
        if index > 0:
            left_sibling = parent.children[index - 1]
            if len(left_sibling.records) > self.page_size // 2:
                # Redistribui um elemento do irmão esquerdo
                child.records.insert(0, left_sibling.records.pop())
                parent.keys[index - 1] = child.records[0].get_key()
                return

        # Tenta redistribuir com o irmão direito
        if index < len(parent.children) - 1:
            right_sibling = parent.children[index + 1]
            if len(right_sibling.records) > self.page_size // 2:
                # Redistribui um elemento do irmão direito
                child.records.append(right_sibling.records.pop(0))
                parent.keys[index] = right_sibling.records[0].get_key()
                return

        # Caso não seja possível redistribuir, funde os nós
        if index > 0:
            left_sibling = parent.children[index - 1]
            left_sibling.records.extend(child.records)
            parent.children.pop(index)
            parent.keys.pop(index - 1)
        else:
            right_sibling = parent.children[index + 1]
            child.records.extend(right_sibling.records)
            parent.children.pop(index + 1)
            parent.keys.pop(index)

    def print_tree(self, page=None, level=0):
        if page is None:
            page = self.root
        indent = "  " * level
        if page.is_leaf():
            print(f"{indent}Leaf (keys: {[r.get_key() for r in page.records]})")
        else:
            print(f"{indent}Internal (keys: {page.keys})")
            for child in page.children:
                self.print_tree(child, level + 1)


if __name__ == '__main__':
    def get_arguments(print_help=False):
        parser = argparse.ArgumentParser('BPlusTree')
        parser.add_argument('-ps', '--page_size', action='store', type=int,
                            default=PAGE_SIZE_DEFAULT,
                            help='Tamanho máximo da página (padrão: ' +
                                 str(PAGE_SIZE_DEFAULT) + ')')
        parser.add_argument('-f', '--filename', action='store', type=str,
                            default=FILE_DEFAULT,
                            help='Arquivo de entrada (padrão: ' +
                                 FILE_DEFAULT + ')')
        args = parser.parse_args()
        if print_help:
            parser.print_help()
        return args

    args = get_arguments()
    with open(args.filename) as FILE_DEFAULT:
        data = csv.DictReader(FILE_DEFAULT)
        b_plus_tree = BPlusTree(page_size=args.page_size)

        for row in data:
            operation = list(row.values())
            if operation[0] == "+":
                aux = [int(a) for a in operation[1:]]
                aux = Record(fields=aux)
                b_plus_tree.insert_root(aux)

    print("\nÁrvore B+ criada com sucesso!")

    while True:
        opcao = int(input(
            "----------------- Menu -----------------\n1) Buscar Elemento. \n2) Buscar por Faixa. \n3) Mostrar Árvore.\n4) Remover Elemento.\n5) Sair.\n ----------------------------------\n Escolha uma das opções acima.\n"))
        if opcao == 1:
            chave_busca = int(input("Digite a chave para buscar: "))
            resultado, pagina = b_plus_tree.search_record(chave_busca)
            if resultado:
                print("Registro encontrado: ", resultado.format())
            else:
                print("Elemento não encontrado.")
        elif opcao == 2:
            k1 = int(input("Digite o valor inicial do intervalo: "))
            k2 = int(input("Digite o valor final do intervalo: "))
            resultados = b_plus_tree.search_range(k1, k2)
            if resultados:
                print("Elementos no intervalo: ", resultados)
            else:
                print("Nenhum elemento encontrado no intervalo.")
        elif opcao == 3:
            print("\n------------ Árvore B+ -------------\n")
            b_plus_tree.print_tree()
        elif opcao == 4:
            chave_remover = int(input("Digite a chave do elemento a ser removido: "))
            removido = b_plus_tree.remove(b_plus_tree.root, chave_remover)
            if removido:
                print("Elemento removido com sucesso!")
            else:
                print("Elemento não encontrado para remoção.")
        elif opcao == 5:
            break
        else:
            print("Opção inválida! Tente novamente!")
