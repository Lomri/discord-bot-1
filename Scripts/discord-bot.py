import os
from dotenv import load_dotenv
import discord
from functions import *
#from functions import command_dictionary

load_dotenv()

TOKEN = os.getenv("DISCORD_TOKEN")

prefix = '!'

#command_dictionary = {}

class MyClient(discord.Client):
  async def on_ready(self):
    print('Logged on as {0}!'.format(self.user))

  async def on_message(self, message):
    global command_dictionary
    if message.author == self.user:
      return
    for command in command_dictionary:
        prefix_with_command = prefix + command
        key_with_space_found = message.content.startswith(prefix_with_command + " ")
        only_key_found = message.content == prefix_with_command
        selected_channel = message.channel
        if only_key_found and message.content == prefix + "reload":
          command_dictionary = await reloadCommandList(selected_channel)
          break
        if key_with_space_found or only_key_found:
            arguments = message.content.split(" ")
            if(len(arguments) > 1 ):
               arguments = arguments[1:]
            else:
               arguments = "No arguments"
            func_name = command_dictionary[command]
            function_worked = await globals()[func_name](selected_channel, arguments)

intents = discord.Intents.default()
intents.message_content = True

command_dictionary = asyncio.run(reloadCommandList())
client = MyClient(intents=intents)
client.run(TOKEN)