from __future__ import annotations
import json
import os
import re

dataFile = "aniversarios.json"


class Data:
    def __init__(self, dia: int, mes: int, ano: int):
        self.dia = dia
        self.mes = mes
        self.ano = ano
        if not self.isValid():
            raise Exception("Data inválida")

    def isValid(self):
        return self.dia > 0 and self.dia <= 31 and self.mes > 0 and self.mes <= 12

    def __str__(self):
        return f"{self.dia}/{self.mes}/{self.ano}"


class Aniversario:
    def __init__(self, nome: str, data: Data):
        self.nome = nome
        self.data = data


class Aniversarios:
    def __init__(self):
        self.aniversarios = []

    # Método estático para carregar aniversários
    @staticmethod
    def carregar(path: str) -> Aniversarios:
        aniversarios = Aniversarios()
        with open(path, "r") as f:
            data = json.loads(f.read())
            for aniversario in data["aniversarios"]:
                data = Data(
                    int(aniversario["data"]["dia"]),
                    int(aniversario["data"]["mes"]),
                    int(aniversario["data"]["ano"]),
                )
                nome = aniversario["nome"]
                aniversario = Aniversario(nome, data)
                aniversarios.aniversarios.append(aniversario)
        return aniversarios

    # Método estático para salvar aniversários
    @staticmethod
    def salvar(aniversarios: Aniversarios, path: str):
        with open(path, "w") as f:
            f.write(aniversarios.toJSON())

    # persist in json
    def toJSON(self):
        return json.dumps(self, default=lambda o: o.__dict__, sort_keys=True, indent=4)

    # Buscar por nome
    def buscarPorNome(self, nome: str) -> list[Aniversario]:
        nomes = nome.split(" ")
        regex = re.compile(".*".join(nomes), re.IGNORECASE)
        aniversarios = []
        for aniversario in self.aniversarios:
            if regex.match(aniversario.nome):
                aniversarios.append(aniversario)
        return aniversarios

    def buscarPorMês(self, mes: int):
        aniversarios = []
        for aniversario in self.aniversarios:
            if aniversario.data.mes == mes:
                aniversarios.append(aniversario)
        return aniversarios

    def adicionar(self, aniversario: Aniversario):
        self.aniversarios.append(aniversario)
        Aniversarios.salvar(self, dataFile)

    def remover(self, nome: str):
        for aniversario in self.aniversarios:
            if aniversario.nome == nome:
                self.aniversarios.remove(aniversario)
                Aniversarios.salvar(self, dataFile)
                return
        raise Exception("Aniversario não encontrado")


if __name__ == "__main__":

    def adicionar():
        nome = input("Nome: ")
        dia = int(input("Dia: "))
        mes = int(input("Mês: "))
        ano = int(input("Ano: "))
        aniversario = Aniversario(nome, Data(dia, mes, ano))
        aniversarios.adicionar(aniversario)
        print(f"Aniversario de {nome} adicionado com sucesso")

    def remover():
        nome = input("Nome: ")
        aniversarios.remover(nome)
        print(f"Aniversario de {nome} removido com sucesso")

    def buscarPorNome():
        nome = input("Nome: ")
        lista = aniversarios.buscarPorNome(nome)
        if len(lista) == 0:
            print(f"Aniversario de {nome} não encontrado")
        else:
            for aniversario in lista:
                print(f"Aniversario de {aniversario.nome} é dia {aniversario.data}")

    def buscarPorMês():
        mes = int(input("Mês: "))
        aniversarios = aniversarios.buscarPorMês(mes)
        if len(aniversarios) == 0:
            print(f"Nenhum aniversario encontrado para o mês {mes}")
        else:
            for aniversario in aniversarios:
                print(f"Aniversario de {aniversario.nome} é dia {aniversario.data}")

    def listarTodos():
        for aniversario in aniversarios.aniversarios:
            print(f"Aniversario de {aniversario.nome} é dia {aniversario.data}")

    aniversarios = None
    # Carregar ou criar novo caso não exista
    if os.path.exists(dataFile):
        # aniversarios = Aniversarios.carregar(dataFile)
        try:
            aniversarios = Aniversarios.carregar(dataFile)
        except Exception as e:
            aniversarios = Aniversarios()
            print(f"Erro ao carregar aniversarios, criando novo arquivo.Erro: {e}")
    else:
        aniversarios = Aniversarios()

    while True:
        op = input(
            """
    Modo teste, escolha uma opção:
    1 - Adicionar
    2 - Remover
    3 - Buscar por nome
    4 - Buscar por mês
    5 - Listar todos
    6 - Sair
    """
        )
        if op == "1":
            adicionar()
        if op == "2":
            remover()
        if op == "3":
            buscarPorNome()
        if op == "4":
            buscarPorMês()
        if op == "5":
            listarTodos()
        if op == "6":
            break
    print("Saindo do programa")
