import discord
import requests


async def on_message_api_lol(client, message, summoner_name):
    API_KEY = 'RGAPI-ca179024-ecbb-490d-92bf-4d8480d4736e'
    API_URL = f'https://br1.api.riotgames.com/lol/summoner/v4/summoners/by-name/{summoner_name}?api_key={API_KEY}'

    response = requests.get(API_URL)
    print(response.status_code)
    if response.status_code != 200:
        exit('ERROR - ' + response.json()['message'])
    if response.status_code != 200:
        return await message.channel.send(
            'Não foi possível obter informações sobre este jogador. Verifique se o nome está correto.')

    summoner_info = response.json()
    summoner_id = summoner_info['id']

    API_URL = f'https://br1.api.riotgames.com/lol/league/v4/entries/by-summoner/{summoner_id}?api_key={API_KEY}'
    response = requests.get(API_URL)
    print(response.status_code)
    if response.status_code != 200:
        exit('ERROR - ' + response.json()['message'])
    if response.status_code != 200:
        return await message.channel.send('Não foi possível obter informações sobre o ranking deste jogador.')

    league_entries = response.json()

    solo_queue_entry = None
    for entry in league_entries:
        print(entry)
        if entry['queueType'] == 'RANKED_SOLO_5x5':
            solo_queue_entry = entry
            break

    if solo_queue_entry is None:
        return await message.channel.send(f'{summoner_name} não está jogando Ranked Solo no momento.')
    summoner_level = summoner_info['summonerLevel']
    rank = solo_queue_entry['rank']
    tier = solo_queue_entry['tier']
    wins = solo_queue_entry['wins']
    losses = solo_queue_entry['losses']
    win_ratio = wins / (wins + losses) * 100

    embed = discord.Embed(title=summoner_name, description='Informações do jogador', color=0x00ff00)
    embed.add_field(name='Ranking Solo', value=f'{tier} {rank}')
    embed.add_field(name='Vitórias', value=wins)
    embed.add_field(name='Derrotas', value=losses)
    embed.add_field(name='Taxa de vitórias', value=f'{win_ratio:.2f}%')
    embed.add_field(name='Nível do invocador', value=summoner_level)
    await message.channel.send(embed=embed)