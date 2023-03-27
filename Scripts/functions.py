from discord.ext import commands
import re
import asyncio
import csv
import discord
from inspect import getsource
import string

command_file = 'command_list.csv'
admin_file = 'admins_list.csv'
settings_file = 'settings_list.csv'
message_file = 'message_list.csv'

command_dictionary = {}
setting_dictionary = {}
admin_ids = []

accept_emoji = '✅'
reject_emoji = '❎'

signup_role_name = 'Player'
signup_role = None
admin_role = 'Admin'


def check_if_admin():
    def predicate(ctx):
        for role in ctx.message.author.roles:
          if(role.name == 'Admin'):
            return True
        return False
    return commands.check(predicate)

def check_if_player():
    def predicate(ctx):
        for role in ctx.message.author.roles:
          if(role.name == 'Player'):
            return True
        return False
    return commands.check(predicate)


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
@check_if_player()
async def delayedPrint(ctx, delay: float, message: str):
  """
Prints text after delay in same message channel.

Parameters:
  float: delay in seconds
  str: string requires quotes

Output:
  Message: Send text as message after delay in seconds"""

  channel = ctx
  await asyncio.sleep(delay)
  await channel.send(message, reference=ctx.message)


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
@check_if_admin()
@commands.cooldown(1, 10, commands.BucketType.default)
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
@check_if_admin()
@commands.cooldown(1, 10, commands.BucketType.default)
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
@check_if_admin()
@commands.cooldown(1, 10, commands.BucketType.default)
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
@check_if_admin()
async def changeSetting(ctx, setting_name: str, setting_value: str):
  """
Takes settings name and value and changes it, if it exists.

Parameters:
  str: setting name
  str: setting value

Output:
  Message: Message that says what was changed to and from"""

  channel = ctx

  current_list = {}

  header = 'setting,description,value,valuetype'

  if(setting_name in setting_dictionary):
    
    if(not is_of_type(setting_dictionary[setting_name]['valuetype'], setting_value)):
      await channel.send('Setting is not correct type', reference=ctx.message)

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
    await channel.send('Setting not found', reference=ctx.message)


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
@check_if_admin()
@commands.cooldown(1, 10, commands.BucketType.default)
async def showSettings(ctx, *args):
  """
Shows a list of settings or description of a setting

Parameters:
  optional: string

Output:
  Message: list of settings or help for a setting"""

  channel = ctx

  global setting_dictionary

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

    await channel.send(settings_message, reference=ctx.message)

  else:
    setting_string = f"Setting **{setting_name}** fields:\n```"
    setting_string += "Type: " + setting_dictionary[setting_name]['valuetype'] + ""
    setting_string += " | Value: " + setting_dictionary[setting_name]['value'] + ""
    setting_string += "\nDescription:\n"
    setting_string += setting_dictionary[setting_name]['description']
    setting_string += "```"
    await channel.send(setting_string, reference=ctx.message)

def load_messages():
  """
Loads messages for events

Parameters:
  none

Return:
  list: list of messages"""

  message_list = []

  with open(message_file, mode='r') as csv_file:
      csv_reader = csv.DictReader(csv_file)
      message_list = {row['message_id']: {'message_type':row['message_type'], 'role':row['role']} for row in csv_reader}
  
  print("Messages loaded!")
  return message_list


async def setup(bot):
    global command_dictionary, setting_dictionary, admin_ids
    command_dictionary = await reloadCommandList(None)
    setting_dictionary = await load_settings(None)
    admin_ids = get_admin_ids()
    for key in command_dictionary:
      function_name = command_dictionary[key]
      try:
        bot.add_command(globals()[function_name])
      except:
        print(f"{function_name} was not found.")
    await bot.add_cog(Events(bot))


@commands.command(name='signuphere')
async def signupHere(ctx):
  """
Creates a message that enables signups on reaction.

Parameters:
  None

Output:
  Message: Message that will signup user on react"""

  channel = ctx

  current_list = {}

  with open(message_file, 'r', newline='') as csv_file:
    reader = csv.DictReader(csv_file)
    current_list = {row['message_id']: {'message_type':row['message_type'], 'role':row['role']} for row in reader}
  message_id = 0
  for row in current_list:
    if('signuphere' == current_list[row]['message_type']):
      message_id = int(row)
      break
  if(message_id):
    message_to_delete = await channel.fetch_message(message_id)
    await message_to_delete.delete()
    header = 'message_id,message_type,role'
    with open(message_file, 'w', newline='') as csv_file:
      csv_file.write(header)
      for key in current_list:
        if(key != str(message_id)):
          csv_file.write('\n' + key + ',' + current_list[key]['message_type'] + current_list[key]['role'])
  

  signup_message = (await channel.send(f'React {accept_emoji} to signup!\n\nReact {reject_emoji} or remove {accept_emoji} reaction to remove signup!', ))
  emoji_signup = accept_emoji
  emoji_remove_signup = reject_emoji
  await signup_message.add_reaction(emoji_signup)
  await signup_message.add_reaction(emoji_remove_signup)
  with open(message_file, 'a', newline='') as csv_file:
    csv_file.write('\n' + str(signup_message.id) + ',' + 'signuphere' + ',' + 'None')
    print("Signuphere message added!")

class Events(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_ready(self):
      print("Initializing")
      global signup_role
      async for guild in self.bot.fetch_guilds(limit=150):
        print(guild)
        guild_roles = guild.roles
        found_signup_role = False
        for role in guild_roles:
          print(role)
          if(role.name == signup_role):
            found_signup_role = True
            signup_role = role
            break
        if(not found_signup_role):
          signup_role = (await guild.create_role(name="Player"))

    @commands.Cog.listener()
    async def on_raw_reaction_add(self, payload):
      message_list = load_messages()
      for key in message_list.keys():
        message_id, emoji, guild, channel = self.common_variables(payload)
        if(str(message_id) == key and message_list[key]['message_type'] == 'signuphere'):
          user = payload.member
          username = payload.member.name

          if(emoji.name == accept_emoji):
            if(signup_role not in user.roles):
              await user.add_roles(signup_role)

              delete_message = f'{username} signed up!'
              print(delete_message)
              delay = 5
              await self.delete_after_delay(channel, delete_message, delay)

          elif(emoji.name == reject_emoji):
            user = payload.member
            await self.remove_accept_reject_reactions(message_id, channel, user)

            if(signup_role in user.roles):
              await user.remove_roles(signup_role)

              delete_message = f'{username} removed sign up!'
              print(delete_message)
              delay = 5
              await self.delete_after_delay(channel, delete_message, delay)

          else:
            user = payload.member
            await self.remove_accept_reject_reactions(message_id, channel, user)

    async def remove_accept_reject_reactions(self, message_id, channel, user):
        msg_remove_reactions = await channel.fetch_message(message_id)
        await msg_remove_reactions.remove_reaction(accept_emoji, user)
        await msg_remove_reactions.remove_reaction(reject_emoji, user)

    async def delete_after_delay(self, channel, delete_message, delay):
        delete_after = await channel.send(delete_message)
        await asyncio.sleep(delay)
        await delete_after.delete()
              
    @commands.Cog.listener()
    async def on_raw_reaction_remove(self, payload):
      message_list = load_messages()
      for key in message_list.keys():
        message_id, emoji, guild, channel = self.common_variables(payload)
        if(str(message_id) == key and message_list[key]['message_type'] == 'signuphere'):
          user_id = payload.user_id
          user = await guild.fetch_member(user_id)
          username = user.name

          if(emoji.name == accept_emoji):
            await self.remove_accept_reject_reactions(message_id, channel, user)

            if(signup_role in user.roles):
              
              await user.remove_roles(signup_role)

              delete_message = f'{username} removed sign up!'
              print(delete_message)
              delay = 5
              await self.delete_after_delay(channel, delete_message, delay)

    def common_variables(self, payload):
        message_id = payload.message_id
        guild_id = payload.guild_id
        channel_id = payload.channel_id
        emoji = payload.emoji
        guild = self.bot.get_guild(guild_id)
        channel = guild.get_channel(channel_id)
        return message_id,emoji,guild,channel

@delayedPrint.error
async def info_error(ctx, error):
    delete_after = await ctx.send(error)
    await asyncio.sleep(5)
    await delete_after.delete()