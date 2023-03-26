from discord.ext import commands
import re
import asyncio
import csv
import discord
from inspect import getsource
import string

command_file = 'command_list.csv'
admin_file = 'admins_list.csv'
signup_file = 'signup_list.csv'
settings_file = 'settings_list.csv'

command_dictionary = {}
setting_dictionary = {}

command_file = 'command_list.csv'

command_dictionary = {}

@commands.command()
async def hello(ctx):
    await ctx.send('Hello {0.display_name}.'.format(ctx.author))


@commands.command(name='print')
async def printText(ctx, *args):
  """
Prints everything after the command

Parameters:
  str: string to print

Output:
  Message: Sends the text as a message"""

  channel = ctx
  arguments = ' '.join(args)
  
  await channel.send(arguments)


@commands.command(name='dprint')
async def delayedPrint(ctx, *args):
  """
Prints text after delay in same message channel.

Parameters:
  str: string requires quotes
  float: delay in seconds

Output:
  Message: Send text as message after delay in seconds"""

  channel = ctx
  if(len(args) >= 2):
    message = args[0]
    delay = args[1]
    if(is_of_type('int', delay)):
      await asyncio.sleep(float(delay))
      await channel.send(message)


def list_find_first_string(arguments: list):
  """
Accepts a list and builts it into a string, finds first text within quotes and returns that with remainings as list.

Parameters:
  text (string): Text.
  delay (float): Delay.

Return:
  str: string within quotes
  list: leftovers as a list"""

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


@commands.command(name='reload')
async def reloadCommandList(ctx):
  """
Reloads command list from .csv file

Parameters:
  None

Output:
  Message: Showing count of commands"""
  
  channel = ctx
  global command_dictionary

  with open(command_file, 'r', newline='') as file:
    reader = csv.DictReader(file)
    command_dictionary = {row['command']: row['function'] for row in reader}

  reload_message = f"Reloaded {len(command_dictionary)} commands"

  if(channel):
    await channel.send(reload_message)

  print(f"reload: {command_dictionary}")

  return command_dictionary


def get_admin_ids():
    """
Gets admins from CSV file and returns a list of admin id's

Parameters:
  none

Return:
  list: list of admin id's"""

    admin_ids = []

    with open(admin_file, mode='r') as csv_file:
        csv_reader = csv.DictReader(csv_file)
        for row in csv_reader:
            admin_ids.append(row['discord_id'])
    
    print("Loaded ", len(admin_ids), " from ", admin_file)

    return admin_ids


@commands.command(name='reaction')
async def messageReaction(ctx):
  """
Generates 'Say hello!' message, that you can react to. It will say 'Hello {user.name}!' back.

Parameters:
  None

Output:
  Message: Message that triggers on react"""

  channel = ctx
  client = ctx.bot
  await channel.send('Say hello!')
  response_data = await client.wait_for('reaction_add')
  user = response_data[1]
  await channel.send(f'Hello {user.name}!')


@commands.command(name='changestatus')
async def changeStatus(ctx, *args):
  """
Changes bot status to idle or online and adds text to "Playing ..." status.

Parameters:
  str: idle or online
  str: status message

Output:
  Bot status: Bot status changes based on parameters"""

  client = ctx
  arg_list = args
  new_status = arg_list[0]
  status_message = " ".join(arg_list[1:])
  new_activity = discord.Game(name=status_message)
  print(new_status)
  print(status_message)
  if(new_status == "idle"):
    await client.change_presence(status=discord.Status.idle, activity=new_activity)
  elif(new_status == "online"):
    await client.change_presence(status=discord.Status.online, activity=new_activity)



@commands.command(name='signup')
async def signUp(ctx):
  """
Writes your name and id to signup_list.csv.

Parameters:
  None

Output:
  Message: Message that tells you if you are signed up already or sign up worked"""

  channel = ctx
  username = ctx.author.name
  user_id = ctx.author.id

  current_list = {}

  with open(signup_file, 'r', newline='') as csv_file:
    reader = csv.DictReader(csv_file)
    current_list = {row['discord_id']: row['name'] for row in reader}

  if(str(user_id) not in current_list):
    with open(signup_file, 'a', newline='') as csv_file:
      csv_file.write('\n' + str(user_id) + ',' + username)
    await channel.send('Signed up!')
  else:
    await channel.send('You are already signed up!')


@commands.command(name='removesignup')
async def removeSignUp(ctx):
  """
Removes your name and id from signup_list.csv.

Parameters:
  None

Output:
  Message: Message that tells you if your signup was removed or you were not in the list"""

  channel = ctx
  username = ctx.author
  user_id = ctx.author.id

  header = 'discord_id,name'
  current_list = {}

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


@commands.command(name='removereaction')
async def removeReaction(ctx):
  """
Creates a message that removes reactions.

Parameters:
  None

Output:
  Message: Message that will have reactions removed"""

  channel = ctx
  client = ctx.bot
  msg_remove_reactions = (await channel.send('If you react to this message, I will remove it!'))
  @client.event
  async def on_reaction_add(reaction, user):
    if(reaction.message.id == msg_remove_reactions.id):
      await msg_remove_reactions.remove_reaction(reaction, user)


@commands.command(name='loadsettings')
async def load_settings(ctx):
  """
Loads settings for bot behavior

Parameters:
  none

Return:
  list: list of settings"""

  global setting_dictionary

  with open(settings_file, mode='r') as csv_file:
      csv_reader = csv.DictReader(csv_file)
      setting_dictionary = {row['setting']: {'description':row['description'], 'value':row['value'], 'valuetype':row['valuetype']} for row in csv_reader}
  
  print("Settings loaded!")

  return setting_dictionary


@commands.command(name='changesetting')
async def changeSetting(ctx, *args):
  """
Takes settings name and value and changes it, if it exists.

Parameters:
  str: setting name
  str: setting value

Output:
  Message: Message that says what was changed to and from"""

  channel = ctx
  arg_list = args

  if(len(arg_list) < 2):
    await channel.send("Need arguments: setting, value")
    return

  setting_name = arg_list[0]
  setting_value = arg_list[1]

  
  current_list = {}

  header = 'setting,description,value,valuetype'

  if(setting_name in setting_dictionary):
    
    if(not is_of_type(setting_dictionary[setting_name]['valuetype'], setting_value)):
      await channel.send('Setting is not correct type')

    with open(settings_file, 'r', newline='') as csv_file:
      csv_reader = csv.DictReader(csv_file)
      current_list = {row['setting']: {'description':row['description'], 'value':row['value'], 'valuetype':row['valuetype']} for row in csv_reader}

    with open(settings_file, 'w', newline='') as csv_file:
      csv_file.write(header)
      for key in current_list:
        setting = key
        if(setting == setting_name and is_of_type(current_list[setting]['valuetype'], setting_value)):
          csv_file.write('\n' + setting + ',' + current_list[setting]['description'] + ',' + setting_value + ',' + current_list[setting]['valuetype'])
          await channel.send(f"Setting: **{setting_name}** changed from **{current_list[setting_name]['value']}** to **{setting_value}**")
        else:
          csv_file.write('\n' + setting + ',' + current_list[setting]['description'] + ',' + current_list[setting]['value'] + ',' + current_list[setting]['valuetype'])
  else:
    await channel.send('Setting not found')


def is_of_type(valuetype, value):
  """
  Checks if string can be considered a valuetype of bool or int"""
  if(valuetype == "bool"):
    if(value != 'True' and value != 'False'):
      return False
    else:
      return True
  if(valuetype == "int"):
    if(string.ascii_letters in value or string.punctuation in value):
      return False
    else:
      return True
  return True


@commands.command(name='settings')
async def showSettings(ctx, *args):
  """
Shows a list of settings or description of a setting

Parameters:
  optional: string

Output:
  Message: list of settings or help for a setting"""

  channel = ctx

  global setting_dictionary

  setting_found = False
  setting_name = None

  if(len(args) >= 1):
    setting_name = args[0]
    setting_found = setting_name in setting_dictionary

  if(not setting_found):
    settings_message = "Settings: "
    if(not setting_found and setting_name != None):
      settings_message = f"Setting '{setting_name}' was not found\n" + settings_message
    
    for key in setting_dictionary:
      settings_message += "**" + key + "**"
      settings_message += ", "

    settings_message = settings_message[:-2]

    await channel.send(settings_message)

  else:
    setting_string = f"Setting **{setting_name}** fields:\n```"
    setting_string += "Type: " + setting_dictionary[setting_name]['valuetype'] + ""
    setting_string += " | Value: " + setting_dictionary[setting_name]['value'] + ""
    setting_string += "\nDescription:\n"
    setting_string += setting_dictionary[setting_name]['description']
    setting_string += "```"
    await channel.send(setting_string)



async def setup(bot):
    global command_dictionary, setting_dictionary
    command_dictionary = await reloadCommandList(None)
    setting_dictionary = await load_settings(None)
    for key in command_dictionary:
      function_name = command_dictionary[key]
      try:
        bot.add_command(globals()[function_name])
      except:
        print(f"{function_name} was not found.")