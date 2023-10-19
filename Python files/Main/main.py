import asyncio
import json
import os

import aiohttp
import openai
import discord
import requests
import datetime
import time
import tokenization
#from datetime import datetime
import connect_db
import apiLol
from discord import app_commands
from ast import literal_eval
from discord import NotFound
from discord.ext import commands

openai.api_key = ""
id_do_servidor =

authorized_users_list = []  # list of authorized user's Admin
authorized_administrator = []
banned_words = []


class DiscordClient:
    def __init__(self):
        intents = discord.Intents.all()
        intents.members = True
        self.client = discord.Client(intents=intents)


start = DiscordClient()
client = start.client

client = commands.Bot(command_prefix='#', intents=discord.Intents.all())

role_name = '[⚡] Bumper'
botBump = 302050872383242240  # id aqui
channelBumpId = # id aqui
serverMemberJoin = # id aqui
channelMemberJoin = # id aqui


@client.event
async def on_ready_slash():
    print(f'{client.user} has connected to Discord Slash!')  # validando se o bot se conectou ao discord
    try:
        synced = await client.tree.sync()
        print(f'synced {len(synced)} command(s)')
    except Exception as e:
        print(e)


@client.hybrid_command()
async def criador(message):
    await message.send("Meu criador é o Rafael!")


@client.hybrid_command()
async def hello(ctx):
    author_id = ctx.author.id
    await ctx.send(f'O seu ID é: {author_id}')

@client.event
async def update_hours():
    # Obter a hora atual
    hora_atual = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    print("Hora atual:", hora_atual)

    # Adicionar 2 horas à hora atual
    hora_futura = (datetime.datetime.now() + datetime.timedelta(hours=2)).strftime("%Y-%m-%d %H:%M:%S")
    print("Hora futura:", hora_futura)

    await connect_db.db_connect(f"UPDATE get_hour SET data_hora = '{hora_futura}' WHERE id = 1;")
    print(f'realizado o Update da HF: {hora_futura}')


@client.event
async def on_ready_hours():
    channel = client.get_channel(channelBumpId)
    role = discord.utils.get(channel.guild.roles,
                             name=role_name)  # Substitua "nome_do_cargo" pelo nome do cargo desejado

    # Loop para verificar se já passaram 2 horas
    while True:
        hora_atual = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        hora_atual = datetime.datetime.strptime(hora_atual, "%Y-%m-%d %H:%M:%S")
        #hora_atual = datetime.datetime.strptime(hora_atual, "%Y-%m-%d %H:%M:%S")
        resultquery = await connect_db.db_connect(f'select data_hora from get_hour where id = 1;')
        print(f'realizado consulta do horário')
        # print(resultquery)
        for hora in resultquery:
            hora_futura = list(hora)
            hora_futura = hora_futura[0]
            hora_futura = str(hora_futura)
            hora_futura = datetime.datetime.strptime(hora_futura, "%Y-%m-%d %H:%M:%S")
            print(f'Próximo bump em: {hora_futura}')
        if hora_atual >= hora_futura:
            await channel.send(f"{role.mention} use o BUMP!")
            break
        else:
            await asyncio.sleep(60)


@client.event
async def on_ready():
    print(f'{client.user} has connected to Discord prefix!')  # validando se o bot se conectou ao discord
    await on_ready_slash()
    await on_ready_hours()
    # await tokenization.on_ready_token()


@client.event
async def on_member_join(member):
    server = member.guild
    if server.id == serverMemberJoin:
        channel = client.get_channel(channelMemberJoin)  # substitua pelo ID do canal que você deseja enviar a mensagem
        role = discord.utils.get(channel.guild.roles,
                                 name="[😉] Recepção")  # Substitua "nome_do_cargo" pelo nome do cargo desejado
        descricao = f"Bem-vindo(a) ao servidor, {member.mention}!"
        embed = discord.Embed(title='', description=descricao, color=0x0080ff)
        await channel.send(f'{role.mention}')
        await channel.send(embed=embed)


@client.event
async def get_username(user_id):
    user = await client.fetch_user(user_id)
    # user.descriminator, antigos Hash
    return f'{user.name}'


@client.event
async def on_message(message):
    banned_words = ["sexo", "transar", "transa", "criador", "engine", "chatgpt", "everyone", "here", "@everyone",
                    "@here", "Everyone", "Here"]

    # if message.guild is None:  # aqui código limita seu funcionamento apenas a chats publicos.
    # return

    if message.author == client.user:  # evita que o bot responda a si mesmo
        return

    if message.content.startswith('!ping'):
        await message.channel.send('pong!')

    if message.author.id == botBump:  # SCRIPT DE BUMP REMEMBER // Verifica se o autor da mensagem é um bot
        print('Validou o Bot Disboard')
        if message.channel.id == channelBumpId:  # ID DO CANAL A SER VERIFICADO
            print('validou o canal de comandos')
            if message.embeds:
                embed = message.embeds[0]
                if "Bump done!" in embed.description:
                    if message.type == discord.MessageType.chat_input_command:
                        user_id = message.interaction.user.id
                        user_name = await get_username(user_id)  # NOME DE QUEM DEU BUMP
                        print(f'o usuário {user_name} deu bump')
                        resultquery = await connect_db.db_connect('SELECT user_id FROM bumpers_count;')
                        list_id_bd = list()
                        for user in resultquery:
                            user_id_bd = list(user)
                            list_id_bd.append(user_id_bd[0])
                        if user_id in list_id_bd:
                            print('O usuário já está na lista')
                            await connect_db.db_connect(f'UPDATE bumpers_count SET '
                                                        f'contador = contador + 1 '
                                                        f'WHERE user_id = {user_id};')
                            print('Realizado o comando UPDATE')

                            resultquery = await connect_db.db_connect(f'SELECT user_id, contador FROM bumpers_count '
                                                                      f'WHERE user_id = {user_id};')
                            print(resultquery)  # user_id[0] = nome // user_id[1] = número de contagens
                            for user in resultquery:
                                user_id = list(user)  # transformando a tupla em lista
                                try:
                                    user_name = await get_username(user_id[0])
                                except NotFound:
                                    await message.channel.send(f'O usuário com ID {user_id} não foi encontrado')
                            descricao = f'**{user_name} está com um total de {user_id[1]} Bumps**'
                            embed = discord.Embed(title='', description=descricao, color=0x0080ff)
                            await message.channel.send(embed=embed)
                            # await message.channel.send(f'{user_name} está com um total de {user_id[1]} Bumps')

                        elif user_id not in list_id_bd:
                            await connect_db.db_connect(f'INSERT INTO bumpers_count (contador, user_id) '
                                                        f'VALUES (1, {user_id});')
                            print('Realizado o comando de INSERT')
                            try:
                                user_name = await get_username(user_id)
                            except NotFound:
                                await message.channel.send(f'O usuário com ID {user_id} não foi encontrado')
                            descricao = f'**{user_name} está com um total de 1 bump**'
                            embed = discord.Embed(title='', description=descricao, color=0x0080ff)
                            await message.channel.send(embed=embed)
                            # await message.channel.send(f'{user_name} está com um total de 1 bump')
                    await update_hours()
                    descricao = f'**Te avisarei sobre o BUMP daqui 2 horas novamente!**'
                    embed = discord.Embed(title='', description=descricao, color=0x0080ff)
                    await message.channel.send(embed=embed)
                    # await message.channel.send(f"Te avisarei sobre o BUMP daqui 2 horas novamente!")
                    await on_ready_hours()

    if message.author.id in authorized_administrator and message.content.startswith('!invite'):

        server_id, channel_id = message.content.split()[1:]

        # Obtém o objeto do servidor pelo ID
        server = client.get_guild(int(server_id))

        if server is None:
            await message.channel.send("Não foi possível encontrar o servidor com esse ID.")
            return

        # Obtém o objeto do canal pelo ID
        channel = server.get_channel(int(channel_id))

        if channel is None:
            await message.channel.send("Não foi possível encontrar o canal com esse ID.")
            return

        try:
            invite = await channel.create_invite()
            await message.channel.send(f"Aqui está o convite para {channel.mention}: {invite.url}")
        except discord.Forbidden:
            await message.channel.send("Não tenho permissão para criar convites neste canal.")

    if message.author.id in authorized_administrator and message.content.startswith('!settings'):
        name_bot = await get_username(botBump)
        channel = client.get_channel(channelBumpId)
        servidor = client.get_guild(serverMemberJoin)
        channel_join = client.get_channel(channelMemberJoin)
        print(f'Bot Bump: {name_bot}\n'
              f'Channel Bump: {channel}\n'
              f'Servidor Member Join: {servidor}\n'
              f'Channel Member Join: {channel_join}')

    if message.author.id in authorized_administrator and message.content.startswith('!quit'):
        server_id = message.content[6:]
        server_id = int(server_id)
        print(type(server_id))
        servidor = client.get_guild(server_id)
        # removendo o bot do servidor
        await servidor.leave()
        await message.channel.send(f"Bot removido do servidor! {servidor.name}")

    if message.content.startswith('!lead'):
        c = 0
        resultquery = await connect_db.db_connect('SELECT user_id, contador FROM bumpers_count ORDER BY contador DESC;')
        print(resultquery)
        list_lead = list()
        list_bumps = list()
        for user in resultquery:
            user_id = list(user)
            try:
                username = await get_username(user_id[0])
                list_lead.append(f'{username}')
                list_bumps.append(f'{user_id[1]}')
                # print(f'{user_id[0]} | {user_id[1]}') Log do ID e counts
            except NotFound:
                await message.channel.send(f'O usuário com ID {user_id} não foi encontrado')
        print(f'Lista: {list_lead}')
        print(len(list_lead))
        descricao = ''
        while len(list_lead) > c:
            descricao += f'**#{c + 1} |** {list_lead[c]} **Bumps:** {list_bumps[c]}\n'
            c = c + 1
            if c > 9:
                break
        embed = discord.Embed(title='**Top 10**| Leaderboard', description=descricao, color=0x0080ff)
        await message.channel.send(embed=embed)

    if message.content.startswith('!lol'):
        user_message = message.content[4:]
        user_message = user_message.lower().strip()
        summoner_name = user_message
        await apiLol.on_message_api_lol(client, message, summoner_name)

    if message.content.startswith('!video'):
        url = message.content[6:]
        shortcode = url.split('/')[-2]

        response = requests.get(
            url='https://www.instagram.com/graphql/query/?query_hash={query}&variables={variables}'.format(
                query='b3055c01b4b222b8a47dc12b090e4e64', variables=json.dumps({'shortcode': shortcode})
            ),
        )

        print(response.status_code)
        if response.status_code != 200:
            exit('ERROR - ' + response.json()['message'])

        data = response.json()['data']['shortcode_media']
        if not 'video_url' in data:
            exit('Check URL')

        video_url = data['video_url']
        response = requests.get(video_url)

        with open("video.mp4", "wb") as file:
            file.write(response.content)
        await message.channel.send(file=discord.File('video.mp4'))

    if message.author.id in authorized_administrator and message.content.startswith('!servidores'):
        print(f'Estou conectado em {len(client.guilds)} servidores:')
        for guild in client.guilds:
            await message.channel.send(f'{guild.name} (id: {guild.id})')
            print(f'{guild.name} | {guild.id}')
            for channel in guild.text_channels:
                print(f'{channel} | {channel.id}')

    if message.author.id in authorized_administrator and message.content.startswith('!add'):
        # adicionar ID na lista de autorizados
        # validando as variaveis para receber um valor correto.
        user_message = message.content[4:]
        user_message = user_message.lower().strip()
        try:
            user_message = literal_eval(user_message)
        except (SyntaxError, ValueError):
            print("Erro de sintaxe")
        if not isinstance(user_message, int):
            await message.channel.send("Um ID Válido é constituido de apenas números, digite novamente")
            return
        # ============
        user_id = user_message
        resultquery = await connect_db.db_connect('SELECT user_id FROM authorized_users_ia;')
        list_id_bd = list()
        for user in resultquery:
            user_id_bd = list(user)
            list_id_bd.append(user_id_bd[0])
        if user_id in list_id_bd:
            print('\033[30:42m user_id é igual user_id_bd: \n Este usuário já esta na lista \033[m')
            await message.channel.send('Este usuário já está na lista')
        else:
            try:
                user_id = user_message
                username = await get_username(user_id)  # transforma o ID em nome
                await connect_db.db_connect(
                    f'INSERT INTO authorized_users_ia (user_id) VALUES ({user_id});')
                print('Realizado o comando de INSERT')
                resultquery = await connect_db.db_connect('SELECT user_id FROM authorized_users_ia;')
                list_id_bd2 = list()
                for user in resultquery:
                    user_id_bd = list(user)
                    list_id_bd2.append(user_id_bd[0])
                print(list_id_bd2)
                if user_id in list_id_bd2:
                    await message.channel.send(
                        f'{username}, adicionado a lista de usuários permitidos para utilização da IA')
                if user_id not in list_id_bd2:
                    await message.channel.send('Erro')
            except NotFound:
                await message.channel.send('Este usuário não existe')
                return

    if message.author.id in authorized_administrator and message.content.startswith('!remove'):
        user_message = message.content[7:]
        user_message = user_message.lower().strip()
        try:
            user_message = literal_eval(user_message)
        except (SyntaxError, ValueError):
            print("Erro de sintaxe")
        if not isinstance(user_message, int):
            await message.channel.send("Um ID Válido é constituido de apenas números, digite novamente")
            print(type(user_message))
            return
        # final da validação de inserção de número inteiro

        user_id = user_message
        try:
            username = await get_username(user_id)  # transforma o ID em nome
        except NotFound:
            await message.channel.send("Este usuário não existe")
            return
        resultquery = await connect_db.db_connect('SELECT user_id FROM authorized_users_ia;')
        list_id_bd = list()
        for user in resultquery:
            user_id_bd = list(user)
            list_id_bd.append(user_id_bd[0])
        if user_id in list_id_bd:
            print('\033[30:42m user_id é igual user_id_bd \033[m')
            await connect_db.db_connect(f'DELETE FROM authorized_users_ia WHERE user_id = {user_id};')
            resultquery = await connect_db.db_connect('SELECT user_id FROM authorized_users_ia;')
            list_id_bd = list()
            for user in resultquery:
                user_id_bd = list(user)
                list_id_bd.append(user_id_bd[0])
            if user_id not in list_id_bd:
                await message.channel.send(f'{username} foi removido da lista')
        else:
            await message.channel.send(f'{username} não está na lista')

        # else:
        #    await message.channel.send(f'{username} não está na lista')

    if message.author.id in authorized_administrator and message.content.startswith('!list'):
        # comando para listar os ID's que estão na lista de Administradores autorizados
        resultquery = await connect_db.db_connect('SELECT user_id FROM authorized_users_ia;')
        print('Lista de usuários permitidos abaixo:')
        await message.channel.send(f'Lista de usuários permitidos abaixo:')
        for user in resultquery:
            user_id = list(
                user)  # o comando List transforma o objeto tupla em lista, portando user_id agora é uma lista
            try:
                username = await get_username(user_id[0])
                await message.channel.send(f'{username} | ID: ({user_id[0]})')
                print(f'{user_id[0]} | {username}')
            except NotFound:
                await message.channel.send(f'O usuário com ID {user_id} não foi encontrado')
        print('=' * 30)

    if message.content.startswith("!iron"):
        resultquery = await connect_db.db_connect('SELECT user_id FROM authorized_users_ia;')
        list_id_bd = list()
        for user in resultquery:
            user_id_bd = list(user)
            list_id_bd.append(user_id_bd[0])
        if message.author.id not in list_id_bd:
            await message.channel.send('Você não está na lista de usuários permitidos!')
            return
        if message.author.id in list_id_bd:  # verifica se o ID do usuário está na lista
            await message.channel.typing()
            user_message = message.content[5:]  # Recuperando a mensagem enviada pelo usuário
            user_message = user_message.lower().strip()
            if len(user_message) == 0:
                await message.channel.send(
                    'Digite alguma coisa')
                return
            for words in banned_words:
                if words in user_message:
                    await message.channel.send(
                        'Não posso falar sobre esse assunto, devido as diretrizes definidas por Stealth.')
                    return
            # Fazendo uma requisição ao ChatGPT
            print('Executando requisição ao chatgpt')
            response = openai.Completion.create(
                engine="text-davinci-003",
                prompt=f"{user_message}" + ", me responda em pt-br",
                stop=["here", "everyone", "@everyone", "@here"],
                max_tokens=1900,
                n=1,
                temperature=0.5
            )

            # Enviando a resposta do ChatGPT para o canal
            await message.channel.send(response["choices"][0]["text"])


@client.tree.command(name='iron')
@app_commands.describe(texto='Digite um texto')
async def iron(interaction: discord.Interaction, texto: str):
    user_id = interaction.user.id
    print(user_id)
    resultquery = await connect_db.db_connect('SELECT user_id FROM authorized_users_ia;')
    list_id_bd = list()
    for user in resultquery:
        user_id_bd = list(user)
        list_id_bd.append(user_id_bd[0])
    if user_id not in list_id_bd:
        await interaction.response.send_message('Você não está na lista de usuários permitidos!')
        return
    if user_id in list_id_bd:  # verifica se o ID do usuário está na lista
        user_message = texto
    print(user_message)
    # Fazendo uma requisição ao ChatGPT
    response = openai.Completion.create(
        engine="text-davinci-003",
        prompt=f"{user_message}" + " pt-br",
        stop=["here", "everyone", "@everyone", "@here"],
        max_tokens=1900,
        n=1,
        temperature=0.5
    )

    # Enviando a resposta do ChatGPT para o canal
    await interaction.response.send_message(response["choices"][0]["text"])


#  Beta
client.run('')
