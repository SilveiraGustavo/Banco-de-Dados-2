# Trabalho Final da disciplina de Banco de Dados 2
# Professor: Marcos Roberto Ribeiro
# Aluno: Gustavo Silveira Dias 


import sys
import csv
import numpy as np
import time
import argparse

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
        for x in page['key']:
            pos += 1
            if key < x:
                return page['children'][pos]
        return page['children'][pos + 1]
    else: 
        return None

def insert_page(page, element):
    if sheet (page):
        if not is_full(page):
            page['record'].append(element)
            page['record'].sort(key=lambda x: x.getKey())

def minimum_occupancy(page):
    return (size_page(page) / page['size_page']) >= 0.50

def to_lan(page):
    if sheet(page):
        return ((size_page(page) - sys.getsizeof(page['record'] [0])) / page['size_page']) >= 0.50
    else:
        return ((size_page(page) - sys.getsizeof(page['key'])) / page['size_page']) >= 0.50

def search_no(pag, k):
    if sheet(pag):
        return pag
    return search_no(search_children(pag,k),k)

def search_interval(tree, k1,k2):
    pag = search_no(tree['source'], k1)
    out_of_range = False
    vet_interval = []

    while not out_of_range:
        for x in pag['record']:
            if 'getKey' in x and k1 <= x['getKey']() <= k2:
                vet_interval.append(x['getkey']())
       
        if not out_of_range:
            pag = pag['page_right']
        if pag is None:
            break
    return vet_interval

def serach_record(tree, k):
    pag = search_no(tree['source'], k)
    reg = None

    for x in pag['record']:
        if 'getKey' in x and x['getKey']() == k:
            reg = x
    return reg, pag

def insert_sheet(N, element, size_page):
    if len(N['record']) >= size_page:
        M = {'sheet': True, 'size_page': size_page}
        M['record'] = N['record'][(len(N['record']) // 2):]
        N['record'] = N['record'][:(len(N['record']) // 2)]
        M['page_right'] = None
        M['page_left'] = None
        KM = M['record'][0]['getKey']()

        if element['record'][0]['getKey']() < KM:
            N['record'].append(element)
        else:
            M['record'].append(element)

        return KM, M
    
    else:
        N['record'].append(element)
        N['record'].sort(key=lambda x: x.get('getKey', 0))

        return None, None
def insert(tree, pag,element):
    if pag['sheet']:
        cha, pag = insert_sheet(N=pag, element=element, size_page=args.size_page)
        return cha, pag
    else:
        F = pag['search_children'](element['getKey']())
        key , children_right = insert(tree,F, element)
    
    if key is not None and children_right is not None:
        if not pag['is_full']():
            aux = -1 
            for x in pag['key']:
                aux += 1
                if key < x:
                    pag['key'].insert(aux, key)
                    pag['children'].insert(aux + 1, children_right)
                    return None, None
            pag['key'].insert(aux + 1, key)
            pag['children'].insert(aux + 2, children_right)
            return None, None
        
        else:
            if len(pag['key']) % 2 == 0:
                metade = (len(pag['children']) // 2) + 1
            else:
                metade = len(pag['children']) // 2

            M = {'sheet': False, 'size_page': tree['size_page']}
            M['key'] = pag['key'][(len(pag['key']) // 2):]
            KM = M['key'].pop(0)
            M['children'] = pag['children'][metade:]
            pag['key'] = pag['key'][:(len(pag['key']) // 2)]
            pag['children'] = pag['children'][:metade]

            return KM, M
    return None, None

def insert_source(tree, element):
    cha, pag = insert(tree, pag=tree ['source'], element=element)
    
    if cha is not None and pag is not None:
        new_source = {'sheet': False, 'size_page': tree['size_page']}
        new_source['key'] = [cha]
        new_source['clildren'] = [tree['source'], pag]
        tree['source'] =  new_source
        print("Nova raiz Criada\n")


def get_arguments(print_help=False):  

    parser = argparse.ArgumentParser('BMais')
    parser.add_argument('-tp', '--size_page', action='store', type=int,
                        default=size_page,
                        help='Maximum page size (default: ' +
                             str(size_page) + ')')
    parser.add_argument('-f', '--filename', action='store', type=str,
                        default=file,
                        help='Input filename (default: ' +
                             file + ')')
    args = parser.parse_args()
    if print_help:
        parser.print_help()
    return args


if __name__ == '__main__':
    args = get_arguments()
    file = open(args.filename)
    dados = csv.DictReader(file)
    Bmais = {'raiz': create_page(sheet==True, size_page=args.tamPagina)}

    quantidade = 0
    for data in dados:
        operacao = list(data.values())
        if operacao[0] == "+":
            quantidade += 1
            aux = [int(a) for a in operacao[1:]]
            aux = {'record': [aux]}
            cha, pag = insert(Bmais, pag=Bmais['raiz'], elemento=aux)

            if quantidade == 1072:
                print(quantidade)
                
    end_time = time.time()
    
    elapsed_time = end_time - start_time
    
    print('As operações demoraram {} segundos'.format(elapsed_time))

    print("\nArvore criada com sucesso!Selecione uma alternativa do menu: ")

    while True:
        
        entrada = int(input(
            "---Menu:---\n1) Buscar Elemento.\n2) Buscar intervalo.\n3) Mostrar árvore.\n4) Sair.\n"))
        if entrada == 1:
            chave_busca = int(input("Digite a chave que deseja buscar: "))
            resultado, pagina = serach_record(Bmais, chave_busca)
            if resultado:
                print("Registro encontrado: ", serach_record(Bmais, chave_busca) )
            else:
                print("Elemento não encontrado.")
        elif entrada == 2:
            k1 = int(input("Digite o valor inicial do intervalo: "))
            k2 = int(input("Digite o valor final do intervalo: "))
            resultados = search_interval(Bmais, k1, k2)
            if resultados:
                print("Elementos no intervalo: ", search_interval(Bmais, k1, k2))
            else:
                print("Nenhum elemento encontrado no intervalo.")
        elif entrada == 3:
            print("\n------------ B+ -------------\n\n", Bmais['raiz'])
        elif entrada == 4:
            break
        else:
            print("Tentativa invalida! Tente novamente!")

