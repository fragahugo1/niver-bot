from __future__ import annotations
import openai
import discord
import os
from dotenv import load_dotenv
from persistencia import Data, Aniversario, Aniversarios, dataFile

load_dotenv()

discord_token = os.getenv("DISCORD_TOKEN")

if discord_token is None:
    print("Discord token not found")
    exit(1)


class MyClient(discord.Client):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.aniversarios = Aniversarios.carregar(dataFile)
        self.command_prefix = "a!"

    async def on_ready(self):
        print(f"Logged on as {self.user}!")

    async def on_message(self, message):
        if message.author == self.user:
            return
        else:
            await self.process_message(message)

    async def process_message(self, message):
        if message.content.startswith(self.command_prefix):
            command = message.content[len(self.command_prefix) :]
            # Adicionar
            if command == "adicionar":
                await message.channel.send("Digite o nome do aniversariante")
                nome = await self.wait_for(
                    "message", check=lambda m: m.author == message.author
                )
                await message.channel.send("Digite o dia do aniversário")
                dia = await self.wait_for(
                    "message", check=lambda m: m.author == message.author
                )
                await message.channel.send("Digite o mês do aniversário")
                mes = await self.wait_for(
                    "message", check=lambda m: m.author == message.author
                )
                await message.channel.send("Digite o ano do aniversário")
                ano = await self.wait_for(
                    "message", check=lambda m: m.author == message.author
                )
                try:
                    dia = dia.content
                    mes = mes.content
                    ano = ano.content
                    nome = nome.content
                    data = Data(int(dia), int(mes), int(ano))
                    aniversario = Aniversario(nome, data)
                    self.aniversarios.aniversarios.append(aniversario)
                    Aniversarios.salvar(self.aniversarios, dataFile)
                    await message.channel.send(f"Aniversário de {nome} adicionado!")
                except Exception as e:
                    await message.channel.send(f"Erro ao adicionar aniversário: {e}")
            # Listar todos
            elif command == "listar":
                aniversarios = ""
                for aniversario in self.aniversarios.aniversarios:
                    aniversarios += f"{aniversario.nome} - {aniversario.data}\n"
                await message.channel.send(aniversarios)
            # Remover
            elif command == "remover":
                await message.channel.send("Digite o nome do aniversariante")
                nome = await self.wait_for(
                    "message", check=lambda m: m.author == message.author
                )
                try:
                    nome = nome.content
                    self.aniversarios.aniversarios.remove(nome)
                    Aniversarios.salvar(self.aniversarios, dataFile)
                    await message.channel.send("Aniversário removido com sucesso!")
                except Exception as e:
                    await message.channel.send(f"Erro ao remover aniversário: {e}")
            # Busca por nome
            elif command == "buscar":
                await message.channel.send("Digite o nome que deseja buscar")
                nome = await self.wait_for(
                    "message", check=lambda m: m.author == message.author
                )
                try:
                    nome = nome.content
                    aniversarios = self.aniversarios.buscarPorNome(nome)
                    mensagem = ""
                    for aniversario in aniversarios:
                        mensagem += f"{aniversario.nome} - {aniversario.data}\n"
                    await message.channel.send(mensagem)
                except Exception as e:
                    await message.channel.send(f"Erro ao buscar aniversário: {e}")
            # Busca por mes
            elif command == "buscarMes":
                await message.channel.send("Digite o mês que deseja buscar")
                mes = await self.wait_for(
                    "message", check=lambda m: m.author == message.author
                )
                try:
                    mes = mes.content
                    aniversarios = self.aniversarios.buscarPorMês(mes)
                    mensagem = ""
                    for aniversario in aniversarios:
                        mensagem += f"{aniversario.nome} - {aniversario.data}\n"
                    await message.channel.send(mensagem)
                except Exception as e:
                    await message.channel.send(f"Erro ao buscar aniversário: {e}")
            # Ajudar
            elif command == "ajuda":
                await message.channel.send(
                    f"""
                    Comandos:
-----------------------------------------
{self.command_prefix}adicionar - Adiciona um aniversário
{self.command_prefix}listar - Lista todos os aniversários
{self.command_prefix}remover - Remove um aniversário
{self.command_prefix}buscar - Busca um aniversário por nome
{self.command_prefix}buscarMes - Busca um aniversário por mês
{self.command_prefix}ajuda - Mostra essa mensagem
-----------------------------------------
                    """
                )
            else:
                await message.channel.send(
                    f"""
                    Comando inválido {message.author.mention}
Digite {self.command_prefix}ajuda para ver os comandos disponíveis
                    """
                )


intents = discord.Intents.default()
intents.message_content = True
intents.members = True

client = MyClient(intents=intents)
client.run(discord_token)
