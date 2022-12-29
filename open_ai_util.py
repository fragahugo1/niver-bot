from __future__ import annotations
import openai
import os
from dotenv import load_dotenv
from persistencia import Data
import datetime

load_dotenv()

openai_key = os.getenv("OPENAI_KEY")

openai_disable = False

if openai_key is None:
    openai_disable = True
    print("OpenAI key not found, disabling OpenAI")


def MensagemAniversario(nome: str, data: Data) -> str:
    def getResponseFromGPT(message: str):
        response = openai.Completion.create(
            model="text-davinci-003",
            prompt=message,
            temperature=1,
            max_tokens=256,
            top_p=1,
            frequency_penalty=0.5,
            presence_penalty=0.5,
        )
        return response["choices"][0]["text"]

    current_date = datetime.datetime.now()
    current_year = current_date.year
    instrucao = f"Escreva uma mensagem de aniversário para {nome} que acontece hoje no dia {data.dia} de {data.mes} de {current_year} faz {current_year - data.ano} anos {nome}."
    if openai_disable:
        raise Exception("OpenAI is disabled")
    return getResponseFromGPT(instrucao)


openai.api_key = openai_key

if __name__ == "__main__":
    print("Teste de mensagem de aniversário")
    nome = "Joe Doe"
    data = Data(30, 12, 1990)
    print(MensagemAniversario(nome, data))
