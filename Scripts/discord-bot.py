import os
from dotenv import load_dotenv
import discord
import re
import datetime
import asyncio
from functions import *

load_dotenv()

TOKEN = os.getenv("DISCORD_TOKEN")

prefix = '!'

def meme(*arguments):
  return "Hello world!"

#def printText(*arguments: list):
    #arguments_as_string = ""
    #for list in arguments:
      #for item in list:
        #arguments_as_string += item
        #arguments_as_string += " "
    #arguments_as_string = arguments_as_string[:-1]
    #return arguments_as_string

async def delayedPrint(*arguments):
    try:
        if(len(arguments) == 2):
            text, delay = arguments
            #await async.sleep(float(delay))
            return text
    except ValueError:
        return "Function used incorrectly"


command_dictionary = {
  'meme': meme,
  'print': printText,
  'delayedprint': delayedPrint
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
            response_message = command_dictionary[key](arguments)
            await message.channel.send(response_message)

intents = discord.Intents.default()
intents.message_content = True


client = MyClient(intents=intents)
client.run(TOKEN) # Replace with your own token