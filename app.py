from __future__ import annotations


import os
import random
import re
import discord
from dotenv import load_dotenv
import requests

from open_ai_util import MensagemAniversario
from persistencia import Aniversario, Aniversarios, Data, dataFile
from discord.ext import tasks, commands

load_dotenv()

discord_token = os.getenv("DISCORD_TOKEN")
tenor_key = os.getenv("TENOR_GOOGLE_KEY")
google_app_name = os.getenv("GOOGLE_APP_NAME")

if discord_token is None:
    print("Discord token not found")
    exit(1)

if tenor_key is None or google_app_name is None:
    print("Tenor key or google app name not found, gif will not be fetched")


def getTenorGifUrl(search: str) -> str:
    if tenor_key is None or google_app_name is None:
        raise Exception("Tenor key or google app name not found")
    url = (
        "https://tenor.googleapis.com/v2/search?q=%s&key=%s&client_key=%s&limit=%s"
        % (search, tenor_key, google_app_name, 5)
    )
    response = requests.get(url)
    if response.status_code == 200:
        return response.json()["results"][
            random.randint(0, len(response.json()["results"]) - 1)
        ]["media_formats"]["gif"]["url"]
    else:
        raise Exception(
            f"Error getting gif from tenor: {response.status_code} {response.text}"
        )


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
        self.birthday_channel = None

    async def on_ready(self):
        print(f"Logged on as {self.user}!")
        self.birthDayChecker = BirthDayChecker(self)

        channel_id = self.aniversarios.discord_channel
        if channel_id:
            self.birthday_channel = self.get_channel(channel_id)
            if self.birthday_channel:
                print(f"Found birthday channel {self.birthday_channel.name}")
                await self.birthday_channel.send("Bot iniciado")
            else:
                print(f"Birthday channel not found")

    async def verifyEachBirthday(self, aniversarios):
        if self.birthday_channel:
            print(f"Found {len(aniversarios)} birthdays")
            # typing
            async with self.birthday_channel.typing():
                for aniversario in aniversarios:
                    print(f"Found birthday for {aniversario.nome}")
                    try:
                        msg = MensagemAniversario(aniversario.nome, aniversario.data)
                    except Exception as e:
                        print(f"Error generating message: {e}")
                        msg = f"Parabéns {aniversario.nome}!"
                    await self.birthday_channel.send(msg)
                    try:
                        gif = getTenorGifUrl("happy birthday".replace(" ", "_"))
                        await self.birthday_channel.send(gif)
                    except Exception as e:
                        print(f"Error getting gif: {e}")
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
            match command:
                # Adicionar
                case "add":
                    await self.adicionar_command(message)
                # Listar todos
                case "list":
                    await self.listar_command(message)
                # Remover
                case "del":
                    await self.remover_command(message)
                # Busca por nome
                case "b":
                    await self.buscar_command(message)
                # Busca por mes
                case "bmes":
                    await self.buscar_mes_command(message)
                # Proximos
                case "next":
                    await self.próximos_command(message)
                # Hoje
                case "hoje":
                    await self.hoje_command(message)
                # Mensagem
                case "msg":
                    await self.mensagem_command(message)
                # Setup
                case "setup":
                    await self.setup_command(message)
                # Ajudar
                case "ajuda":
                    await self.ajuda_command(message)
                case _:
                    await message.channel.send(
                        f"""Comando inválido {message.author.mention}
Digite {self.command_prefix}ajuda para ver os comandos disponíveis"""
                    )

    async def setup_command(self, message):
        # get current channel
        self.birthday_channel = message.channel
        self.aniversarios.setDiscord_channel(message.channel.id)
        await message.channel.send(
            f"Canal de aniversários definido!\n {message.channel.mention}"
        )

    async def ajuda_command(self, message):
        await message.channel.send(
            f"""
                    Comandos:
```markdown
+ {self.command_prefix}add - Adiciona um aniversário
+ {self.command_prefix}list - Lista todos os aniversários
+ {self.command_prefix}del - Remove um aniversário
+ {self.command_prefix}b - Busca um aniversário por nome
+ {self.command_prefix}bmes - Busca um aniversário por mês
+ {self.command_prefix}next - Busca os aniversarios nos próximos 30 dias 
+ {self.command_prefix}hoje - Busca os aniversariante de hoje
+ {self.command_prefix}msg - gera uma mensagem de aniversário para um aniversariante
+ {self.command_prefix}ajuda - Mostra essa mensagem
+ {self.command_prefix}setup - Define o atual canal de aniversários
```
"""
        )

    async def buscar_mes_command(self, message):
        await message.channel.send("Digite o mês que deseja buscar, EX: 01, 4, 12 ... ")
        mes = await self.wait_for("message", check=lambda m: m.author == message.author)
        try:
            mes = mes.content
            aniversarios = self.aniversarios.buscarPorMês(int(mes))
            mensagem = ""
            for aniversario in aniversarios:
                mensagem += f"{aniversario.nome} - {aniversario.data}\n"
            print(f"Found {len(aniversarios)} birthdays on {mes} month")
            await message.channel.send(mensagem)
        except Exception as e:
            await message.channel.send(f"Erro ao buscar aniversário: {e}")

    async def buscar_command(self, message):
        await message.channel.send("Digite o nome que deseja buscar")
        nome = await self.wait_for(
            "message", check=lambda m: m.author == message.author
        )
        try:
            nome = nome.content
            aniversarios = self.aniversarios.buscarPorNome(nome)
            mensagem = ""
            # typing
            async with message.channel.typing():
                for aniversario in aniversarios:
                    mensagem += f"{str(aniversario)} \n"
                print(f"Found {len(aniversarios)} birthdays with {nome} name")
                await message.channel.send(mensagem)
        except Exception as e:
            await message.channel.send(f"Erro ao buscar aniversário: {e}")

    async def remover_command(self, message):
        await message.channel.send("Digite o nome do aniversariante")
        nome = await self.wait_for(
            "message", check=lambda m: m.author == message.author
        )
        try:
            # typing
            async with message.channel.typing():
                nome = nome.content
                self.aniversarios.remover(nome)
                print(f"Removed birthday of {nome}")
                await message.channel.send("Aniversário removido com sucesso!")
        except Exception as e:
            await message.channel.send(f"Erro ao remover aniversário: {e}")

    async def listar_command(self, message):
        aniversarios = ""
        # typing
        async with message.channel.typing():
            for aniversario in self.aniversarios.aniversarios:
                aniversarios += f"{str(aniversario)} \n"
            await message.channel.send(aniversarios)

    async def adicionar_command(self, message):
        await message.channel.send("Digite o nome:")
        nome = await self.wait_for(
            "message", check=lambda m: m.author == message.author
        )
        await message.channel.send("Digite a data de nascimento: Ex: 30/04/2000")
        data = await self.wait_for(
            "message", check=lambda m: m.author == message.author
        )
        dateRegex = re.compile(r"\d{1,2}/\d{1,2}/\d{4}")
        if not dateRegex.match(data.content):
            await message.channel.send("Data inválida!")
            return
        dia = data.content.split("/")[0]
        mes = data.content.split("/")[1]
        ano = data.content.split("/")[2]
        try:
            # typing
            async with message.channel.typing():
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

    async def próximos_command(self, message):
        # Busca os aniversarios nos próximos 30 dias
        aniversarios = self.aniversarios.buscarProximos()
        mensagem = ""
        if len(aniversarios) == 0:
            await message.channel.send(
                "Nem um aniversario acontecera nos próximos 30 dias"
            )
            return
        # typing
        async with message.channel.typing():
            for aniversario in aniversarios:
                mensagem += f"Aniversario de {aniversario.nome} sera em {aniversario.diasAteProximo()} dia(s), estará fazendo {aniversario.idade()} anos \n"
            await message.channel.send(mensagem)

    async def hoje_command(self, message):
        # Busca os aniversarios nos próximos 30 dias
        mensagem = ""
        hoje = Data.today()
        aniversarios = self.aniversarios.buscarPorMêsDia(hoje.mes, hoje.dia)
        if len(aniversarios) == 0:
            await message.channel.send("Nem um aniversario acontecera hoje")
            return
        # typing
        async with message.channel.typing():
            for aniversario in aniversarios:
                mensagem += f"Parabéns {aniversario.nome} \n"
            await message.channel.send(mensagem)

    async def mensagem_command(self, message):
        await message.channel.send("Digite o nome do aniversariante")
        nome = await self.wait_for(
            "message", check=lambda m: m.author == message.author
        )
        try:
            aniversario = self.aniversarios.buscarPorNomeExato(nome.content)
            # typing
            async with message.channel.typing():
                message_str = MensagemAniversario(aniversario.nome, aniversario.data)
            await message.channel.send(message_str)
        except Exception as e:
            await message.channel.send(f"Erro ao buscar aniversário: {e}")
            return


intents = discord.Intents.default()
intents.message_content = True
intents.members = True

client = MyClient(intents=intents)
client.run(discord_token)
