import asyncio
import json
import discord
import requests
from discord.ext import commands
from discord_webhook import DiscordWebhook

with open('config.json') as f:
    config = json.load(f)

description = '''Interconnects with the Discord API and Discord.Py for share messages between two Discord servers.'''
intents = discord.Intents.default()
intents.message_content = True
intents.members = True

bot = commands.Bot(command_prefix='!', description=description, intents=intents)

SERVER1_ID = config['SERVER_ONE']['ID']
SERVER2_ID = config['SERVER_TWO']['ID']

CHANNEL_ID = config['SERVER_ONE']['CHANNEL_ID']
CHANNEL2_ID = config['SERVER_TWO']['CHANNEL_ID']

SERVER2_URL = config['SERVER_TWO']['WEBHOOK_URL']
SERVER1_URL = config['SERVER_ONE']['WEBHOOK_URL']

server1 = bot.get_guild(SERVER1_ID)
server2 = bot.get_guild(SERVER2_ID)

@bot.event
async def on_ready():
    print('Logged in as')
    print(bot.user.name)
    print(bot.user.id)
    print('------')

    await bot.get_guild(SERVER1_ID).me.edit(nick="La Taverne")
    await bot.get_guild(SERVER2_ID).me.edit(nick="La Cour des Miracles")

@bot.event
async def on_typing(channel, user, when):
    if user.bot:
        return

    if channel.id == CHANNEL_ID:
        DEST_TYPING = CHANNEL2_ID
    elif channel.id == CHANNEL2_ID:
        DEST_TYPING = CHANNEL_ID
    else:
        return

    async with bot.get_channel(DEST_TYPING).typing():
        await asyncio.sleep(0.3)


@bot.event
async def on_message(message):
    try:
        if message.content.startswith("@everyone") or message.content.startswith("@here"):
            return
        a = message.content
        if a.contains("@everyone") or a.contains("@here"):
            return
    except:
        pass
    if message.author.bot:
        return

    if message.channel.id == CHANNEL_ID:
        DEST_MESSAGE = SERVER2_URL
    elif message.channel.id == CHANNEL2_ID:
        DEST_MESSAGE = SERVER1_URL
    else:
        return

    if len(message.attachments) > 0:
        for attachment in message.attachments:
            webhook = DiscordWebhook(url=DEST_MESSAGE, content=message.content, username=message.author.name, avatar_url=message.author.avatar.url)
            r = requests.get(attachment.url)
            webhook.add_file(file=r.content, filename=attachment.filename)
            webhook.execute()
    else:
        webhook = DiscordWebhook(url=DEST_MESSAGE, content=message.content, username=message.author.name, avatar_url=message.author.avatar.url)
        webhook.execute()


bot.run(config['d_token'])