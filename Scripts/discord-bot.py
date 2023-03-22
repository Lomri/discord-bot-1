import os
from dotenv import load_dotenv
import discord
from functions import *

load_dotenv()

TOKEN = os.getenv("DISCORD_TOKEN")

prefix = '!'

command_dictionary = {
  'print': printText,
  'dprint': delayedPrint
}

class MyClient(discord.Client):
  async def on_ready(self):
    print('Logged on as {0}!'.format(self.user))

  async def on_message(self, message):
    if message.author == self.user:
      return
    for key in command_dictionary:
        prefix_with_command = prefix + key
        key_with_space_found = message.content.startswith(prefix_with_command + " ")
        only_key_found = message.content == prefix_with_command
        if key_with_space_found or only_key_found:
            arguments = message.content.split(" ")
            if(len(arguments) > 1 ):
               arguments = arguments[1:]
            else:
               arguments = "No arguments"
            selected_channel = message.channel
            response_message = await command_dictionary[key](selected_channel, arguments)

intents = discord.Intents.default()
intents.message_content = True


client = MyClient(intents=intents)
client.run(TOKEN)