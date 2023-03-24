import os
from dotenv import load_dotenv
import discord
from functions import *

load_dotenv()

TOKEN = os.getenv("DISCORD_TOKEN")

prefix = '!'

class Argument:
  def __init__(self, client = None, channel = None, message = None, arguments = None) -> None:
    self.client = client
    self.channel = channel
    self.message = message
    self.arguments = arguments

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

            function_arguments = Argument(self, selected_channel, message, arguments)
            function_worked = await globals()[func_name](function_arguments)

intents = discord.Intents.default()
intents.message_content = True

function_arguments = Argument()
command_dictionary = asyncio.run(reloadCommandList(function_arguments))
admin_id_list = get_admin_ids()

client = MyClient(intents=intents)
client.run(TOKEN)