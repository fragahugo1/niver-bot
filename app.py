from __future__ import annotations

import asyncio
import logging
import os

import discord
import openai
from dotenv import load_dotenv

from open_ai_util import MensagemAniversario
from persistencia import Aniversario, Aniversarios, Data, dataFile
from threading import Thread
from discord.ext import tasks, commands

load_dotenv()

discord_token = os.getenv("DISCORD_TOKEN")

if discord_token is None:
    print("Discord token not found")
    exit(1)


class BirthDayChecker(commands.Cog):
    def __init__(self, client):
        self.client = client
        self.checkBirthdaysLoops.start()

    # 24 hours
    @tasks.loop(hours=24)
    async def checkBirthdaysLoops(self):
        print("Checking birthdays")
        await self.checkBirthday()

    async def checkBirthday(self):
        print("Checking birthdays")
        self.today = Data.today()
        day = self.today.dia
        mes = self.today.mes
        aniversarios = self.client.aniversarios.buscarPorMêsDia(mes, day)
        if len(aniversarios) > 0:
            await self.client.verifyEachBirthday(aniversarios)
        else:
            print("No birthdays found")


class MyClient(discord.Client):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.aniversarios = Aniversarios.carregar(dataFile)
        self.command_prefix = "a!"
        self.lestCheckDate = None
        self.generalChannel = None

    async def on_ready(self):
        print(f"Logged on as {self.user}!")
        self.birthDayChecker = BirthDayChecker(self)

    async def verifyEachBirthday(self, aniversarios):
        if self.generalChannel:
            print(f"Found {len(aniversarios)} birthdays")
            for aniversario in aniversarios:
                print(f"Found birthday for {aniversario.nome}")
                try:
                    msg = MensagemAniversario(aniversario.nome, aniversario.data)
                except Exception as e:
                    print(f"Error generating message: {e}")
                    msg = f"Parabéns {aniversario.nome}!"
                await self.generalChannel.send(msg)
        else:
            print("General channel not found")
       

    async def on_message(self, message):
        print(f"Message from {message.author}: {message.content}")
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
                    print(f"Added birthday for {nome}")
                    await message.channel.send(f"Aniversário de {nome} adicionado!")
                except Exception as e:
                    print(f"Error adding birthday: {e}")
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
                    print(f"Removed birthday of {nome}")
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
                    print(f"Found {len(aniversarios)} birthdays with {nome} name")
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
                    print(f"Found {len(aniversarios)} birthdays on {mes} month")
                    await message.channel.send(mensagem)
                except Exception as e:
                    await message.channel.send(f"Erro ao buscar aniversário: {e}")
            # Setup
            elif command == "setup":
                # get current channel
                self.generalChannel = message.channel
                await message.channel.send("Canal de aniversários definido!")
            # Ajudar
            elif command == "ajuda":
                await message.channel.send(
                    f"""
                    Comandos:
```markdown
+ {self.command_prefix}adicionar - Adiciona um aniversário
+ {self.command_prefix}listar - Lista todos os aniversários
+ {self.command_prefix}remover - Remove um aniversário
+ {self.command_prefix}buscar - Busca um aniversário por nome
+ {self.command_prefix}buscarMes - Busca um aniversário por mês
+ {self.command_prefix}ajuda - Mostra essa mensagem
+ {self.command_prefix}setup - Define o atual canal de aniversários
```
"""
                )
            else:
                await message.channel.send(
                    f"""Comando inválido {message.author.mention}
Digite {self.command_prefix}ajuda para ver os comandos disponíveis"""
                )


intents = discord.Intents.default()
intents.message_content = True
intents.members = True

client = MyClient(intents=intents)
client.run(discord_token)
