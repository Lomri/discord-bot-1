import os
from dotenv import load_dotenv
import discord
from discord.ext import commands
import asyncio

load_dotenv()

TOKEN = os.getenv("DISCORD_TOKEN")

prefix = '!'

class MyClient(discord.Client):
  async def on_ready(self):
    print('Logged on as {0}!'.format(self.user))

intents = discord.Intents.default()
intents.message_content = True

bot = commands.Bot(command_prefix=prefix, intents=intents)
asyncio.run(bot.load_extension("functions"))
bot.run(TOKEN)
