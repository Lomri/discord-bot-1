import os
from dotenv import load_dotenv
import discord
import re
import datetime
import asyncio

load_dotenv()

TOKEN = os.getenv("DISCORD_TOKEN")

prefix = '!'

def meme(*arguments):
  return "Hello world!"

def printText(*arguments):
    arguments_as_string = "".join(list(arguments))
    return arguments_as_string

async def delayedPrint(*arguments):
    try:
        if(len(arguments) == 2):
            text, delay = arguments
            await delayInSeconds(float(delay))
            return text
    except ValueError:
        return "Function used incorrectly"

async def delayInSeconds(time_in_seconds):
    loop = asyncio.get_running_loop()
    end_time = loop.time() + time_in_seconds
    while True:
        print(datetime.datetime.now())
        if (loop.time() + 1.0) >= end_time:
            break
        await asyncio.sleep(1)

def find_first_string(arguments):
    arguments_as_string = "".join(list(arguments))
    match = re.search('"([^"]*)"', arguments_as_string)
    try:
      if(match):
          return match.group(1)
    except ValueError:
       return "No message to print"

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
            arguments = message.content.split(" ")[1:]
            response_message = await command_dictionary[key](arguments)
            await message.channel.send(response_message)

intents = discord.Intents.default()
intents.message_content = True


client = MyClient(intents=intents)
client.run(TOKEN) # Replace with your own token