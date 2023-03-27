import os
from dotenv import load_dotenv
import discord
from discord.ext import commands
import asyncio

load_dotenv()

TOKEN = os.getenv("DISCORD_TOKEN")

prefix = '!'

intents = discord.Intents.default()
intents.message_content = True

bot = commands.Bot(command_prefix=prefix, intents=intents)
asyncio.run(bot.load_extension("server_setup"))
asyncio.run(bot.load_extension("functions"))
bot.run(TOKEN)
