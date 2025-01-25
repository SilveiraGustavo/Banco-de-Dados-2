import sys
import csv
import time
import matplotlib.pyplot as plt

PAGE_SIZE_DEFAULT = 4096  # Tamanho da página padrão
FILE_DEFAULT = "arquivo3.csv"  # Arquivo de teste

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
        return "\n".join(f"Índice {i} --> {bucket}" for i, bucket in enumerate(self.bucket_list))


if __name__ == '__main__':
    start_time = time.time()
    
    # A lista que armazena o tempo total de execução
    tempos_execucao = []

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

    # Calcula o tempo total de execução
    tempo_total = time.time() - start_time
    tempos_execucao.append(tempo_total)

    print(f'Operações completadas em {tempo_total:.4f} segundos.')

    # Gera o gráfico com o tempo total de execução
    plt.bar(['Execução Completa'], tempos_execucao)
    plt.ylabel('Tempo (segundos)')
    plt.title('Tempo Total de Execução das Inserções')
    plt.show()

    while True:
        escolha = int(input("--- Menu ---\n1)Buscar Elemento.\n2) Remover Elemento,\n3) Mostrar Hash.\n4) Sair.\n"))
        if escolha == 1:
            chave = int(input("Digite a chave para buscar: "))
            registro = main_hash.search(chave)
            print(f"Encontrado: {registro}" if registro else "Elemento não encontrado!")
        elif escolha == 2:
            chave = int(input("Digite a chave para remover: "))
            removido = main_hash.remove(chave)
            print(f"Removido: {removido}" if removido else "Elemento não encontrado!")
        elif escolha == 3:
            print("\n--- Hash Expansível ---\n", main_hash)
        elif escolha == 4:
            break
        else:
            print("Opção inválida! Tente novamente!")
