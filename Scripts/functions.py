import re
import asyncio
import csv

command_file = 'command_list.csv'
admin_file = 'admins_list.csv'
command_dictionary = {}


async def printText(arguments):
  """
  Prints everything after the command

  Parameters:
  tuple:
    channel: channel to send message in
    list: list for printing

  Output:
  Sends the text as a message
  """

  channel = arguments.channel
  arg_list = arguments.arguments

  arguments_as_string = ""
  for item in arg_list:
    arguments_as_string += item
    arguments_as_string += " "
  arguments_as_string = arguments_as_string[:-1]
  
  await channel.send(arguments_as_string)
  return True

async def delayedPrint(arguments):
  """
  Prints text after delay in same message channel.

  Parameters:
  tuple:
    channel: channel to send message in
    list: arguments after initial command
      text (string): Text.
      delay (float): Delay.

  Output:
  Send text as message after delay in seconds.
  """

  channel = arguments.channel
  arg_list = arguments.arguments
  if(len(arg_list) > 1):
    print(arg_list)
    quotes_found = 0
    for item in arg_list:
        if('"' in item):
          quotes_found += 1
    text, remaining_list = list_find_first_string(arg_list)
    if(remaining_list[0] == ""):
        remaining_list = remaining_list[1:]
    if(len(remaining_list) > 1):
      await channel.send(f"Wrong amount of arguments! 2 expected. Found: {len(remaining_list) + 1}")
      return
    print(f"text: {text} remaining_list: {remaining_list}")
    await asyncio.sleep(float(remaining_list[0]))
    await channel.send(text)
    return True
  elif(channel):
    await channel.send(f"Wrong amount of arguments! 2 expected. Found: {len(arguments)}")
  else:
    print("ValueError")

def list_find_first_string(arguments: list):
  """
  Accepts a list and builts it into a string, finds first text within quotes and returns that with remainings as list.

  Parameters:
  text (string): Text.
  delay (float): Delay.

  Return:
  str: string within quotes
  list: leftovers as a list
  """

  if(arguments):
    arguments_as_string = ""
    arguments_as_string = " ".join(arguments)
    match = re.search('"([^"]*)"', arguments_as_string)
    found_text = ""
    remaining_list = arguments_as_string
    try:
      if(match):
          found_text = match.group(1)
          remaining_list = arguments_as_string.replace('"' + found_text + '"', "").split(" ")
      return found_text, remaining_list
    except ValueError:
      return found_text, remaining_list
  else:
      return found_text, remaining_list
  
async def reloadCommandList(arguments):
  """
  Reloads command list from .csv file

  Parameters:
  None

  Output:
  Message: Showing count of commands
  """
  
  channel = arguments.channel

  with open(command_file, 'r', newline='') as file:
    reader = csv.DictReader(file)
    command_dictionary = {row['command']: row['function'] for row in reader}

  reload_message = f"Reloaded {len(command_dictionary)} commands"

  if(channel):
    await channel.send(reload_message)

  print(f"reload: {command_dictionary}")

  return command_dictionary

async def helpCommandList(arguments):
  """
  Shows a list of available commands

  Parameters:
  None

  Output:
  Message: Available commands
  """

  channel = arguments.channel
  global command_dictionary
  help_message = "Available commands: "

  print(f"help: {command_dictionary}")
  
  for key in command_dictionary:
    help_message += "'" + key + "'"
    help_message += ", "

  help_message = help_message[:-2]

  await channel.send(help_message)

def get_admin_ids():
    """
    Gets admins from CSV file and returns a list of admin id's
    Parameters:
    none
    Return:
    list: list of admin id's
    """
    
    admin_ids = []

    with open(admin_file, mode='r') as csv_file:
        csv_reader = csv.DictReader(csv_file)
        for row in csv_reader:
            admin_ids.append(row['discord_id'])
    
    print("Loaded ", len(admin_ids), " from ", admin_file)

    return admin_ids

async def messageReaction(arguments):
  """
  Generates 'Say hello!' message, that you can react to. It will say 'Hello {user.name}!' back.
  Parameters:
  none
  Return:
  Message: Message that triggers on react
  """

  channel = arguments.channel
  client = arguments.client
  await channel.send('Say hello!')
  response_data = await client.wait_for('reaction_add')
  user = response_data[1]
  await channel.send(f'Hello {user.name}!')

