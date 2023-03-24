import re
import asyncio
import csv
import discord

command_file = 'command_list.csv'
admin_file = 'admins_list.csv'
signup_file = 'signup_list.csv'
command_dictionary = {}


async def printText(arguments):
  """
  Prints everything after the command

  Parameters:
  str: string to print

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
  str: string requires quotes
  float: delay in seconds

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
  global command_dictionary

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
    help_message += "**" + key + "**"
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
  None
  Output:
  Message: Message that triggers on react
  """

  channel = arguments.channel
  client = arguments.client
  await channel.send('Say hello!')
  response_data = await client.wait_for('reaction_add')
  user = response_data[1]
  await channel.send(f'Hello {user.name}!')

async def changeStatus(arguments):
  """
  Generates 'Say hello!' message, that you can react to. It will say 'Hello {user.name}!' back.
  Parameters:
  str: new_status
  str: status_message
  Return:
  Message: Message that triggers on react
  """

  client = arguments.client
  arg_list = arguments.arguments
  new_status = arg_list[0]
  status_message = " ".join(arg_list[1:])
  new_activity = discord.Game(name=status_message)
  print(new_status)
  print(status_message)
  if(new_status == "idle"):
    await client.change_presence(status=discord.Status.idle, activity=new_activity)
  elif(new_status == "online"):
    await client.change_presence(status=discord.Status.online, activity=new_activity)


async def signUp(arguments):
  """
  Writes your name and id to signup_list.csv.
  Parameters:
  None
  Output:
  Message: Message that tells you if you are signed up already or sign up worked.
  """

  channel = arguments.channel
  message = arguments.message
  
  current_list = {}

  username = message.author.name
  user_id = message.author.id

  with open(signup_file, 'r', newline='') as csv_file:
    reader = csv.DictReader(csv_file)
    current_list = {row['discord_id']: row['name'] for row in reader}

  if(str(user_id) not in current_list):
    with open(signup_file, 'a', newline='') as csv_file:
      csv_file.write('\n' + str(user_id) + ',' + username)
    await channel.send('Signed up!')
  else:
    await channel.send('You are already signed up!')

  
async def removeSignUp(arguments):
  """
  Removes your name and id from signup_list.csv.
  Parameters:
  None
  Output:
  Message: Message that tells you if your signup was removed or you were not in the list.
  """

  channel = arguments.channel
  message = arguments.message
  
  current_list = {}

  header = 'discord_id,name'
  user_id = message.author.id

  was_signed_up = False

  with open(signup_file, 'r', newline='') as csv_file:
    reader = csv.DictReader(csv_file)
    current_list = {row['discord_id']: row['name'] for row in reader}

  with open(signup_file, 'w', newline='') as csv_file:
    csv_file.write(header)
    for key in current_list:
      if(key == str(user_id) and not was_signed_up):
        was_signed_up = True
        await channel.send('Signup removed!')
      else:
        csv_file.write('\n' + key + ',' + current_list[key])
    if(not was_signed_up):
      await channel.send('You were not signed up.')


async def removeReaction(arguments):
  """
  Creates a message that removes reactions.
  Parameters:
  None
  Output:
  Message: Message that will have reactions removed.
  """

  channel = arguments.channel
  client = arguments.client
  msg_remove_reactions = (await channel.send('If you react to this message, I will remove it!'))
  @client.event
  async def on_reaction_add(reaction, user):
    if(reaction.message.id == msg_remove_reactions.id):
      await msg_remove_reactions.remove_reaction(reaction, user)
