from __future__ import annotations

import json
import os
import re
from datetime import date, datetime, timedelta

dataFile = "aniversarios.json"

MESES_TABLE = {
    "1": "Janeiro",
    "2": "Fevereiro",
    "3": "Março",
    "4": "Abril",
    "5": "Maio",
    "6": "Junho",
    "7": "Julho",
    "8": "Agosto",
    "9": "Setembro",
    "10": "Outubro",
    "11": "Novembro",
    "12": "Dezembro",
}


class Data:
    def __init__(self, dia: int, mes: int, ano: int):
        self.dia = dia
        self.mes = mes
        self.ano = ano
        if not self.isValid():
            raise Exception("Data inválida")

    def isValid(self) -> bool:
        # try to create a datetime object
        try:
            datetime(self.ano, self.mes, self.dia)
            return True
        except ValueError:
            return False
        
    def __str__(self) -> str:
        return f"{self.dia}/{self.mes}/{self.ano}"

    def __ge__(self, other) -> bool:
        # ignore ano
        return (self.ano == other.ano and self.mes > other.mes) or (
            self.mes == other.mes and self.dia >= other.dia
        )

    def __gt__(self, other) -> bool:
        return (self.ano == other.ano and self.mes > other.mes) or (
            self.mes == other.mes and self.dia > other.dia
        )

    def __eq__(self, other) -> bool:
        return self.mes == other.mes and self.dia == other.dia

    def copy(self) -> Data:
        return Data(self.dia, self.mes, self.ano)

    def toDatetime(self) -> datetime:
        return datetime(self.ano, self.mes, self.dia)

    # métodos estáticos
    @staticmethod
    def today() -> Data:
        today = date.today()
        return Data(today.day, today.month, today.year)


class Aniversario:
    def __init__(self, nome: str, data: Data):
        self.nome = nome
        self.data = data

    def __repr__(self) -> str:
        return f"{self.nome} - {self.data.dia} de {MESES_TABLE[str(self.data.mes)]} - em {self.diasAteProximo()} dia(s)"

    def diasAteProximo(self) -> int:
        today = Data.today()
        data_nasci = self.data.copy()
        # mover data_nasci para ano atual
        data_nasci.ano = today.ano
        # se ja passou mover para ano seguinte
        if today > data_nasci:
            data_nasci.ano += 1
        return (data_nasci.toDatetime() - today.toDatetime()).days


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
    
    def buscarPorNomeExato(self, nome: str) -> Aniversario:
        for aniversario in self.aniversarios:
            if aniversario.nome == nome:
                return aniversario
        raise Exception("Aniversário não encontrado")
    


    def buscarPorMês(self, mes: int) -> list[Aniversario]:
        aniversarios = []
        for aniversario in self.aniversarios:
            if aniversario.data.mes == mes:
                aniversarios.append(aniversario)
        return aniversarios

    def buscarPorMêsDia(self, mes: int, dia: int) -> list[Aniversario]:
        niver_no_dia = []
        for aniversario in self.aniversarios:
            if aniversario.data.mes == mes and aniversario.data.dia == dia:
                niver_no_dia.append(aniversario)
        return niver_no_dia

    def buscarProximos(self) -> list[Aniversario]:
        aniversarios = []
        for aniversario in self.aniversarios:
            if aniversario.diasAteProximo() <= 30:
                aniversarios.append(aniversario)
        return sorted(
            aniversarios, key=lambda aniversario: aniversario.diasAteProximo()
        )

    def adicionar(self, aniversario: Aniversario) -> None:
        self.aniversarios.append(aniversario)
        Aniversarios.salvar(self, dataFile)

    def remover(self, nome: str) -> None:
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
