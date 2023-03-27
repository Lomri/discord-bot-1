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
    #checking if command invoker has role with name 'Admin'
    def predicate(ctx):
        for role in ctx.message.author.roles:
          if(role.name == 'Admin'):
            return True
        return False
    return commands.check(predicate)

def check_if_player():
    #checking if command invoker has role with name 'Player'
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
  await channel.send(message, reference=ctx.message) #reference means reply to message


def list_find_first_string(arguments: list):
  """
Accepts a list and builts it into a string, finds first text within quotes and returns that with remainings as list.

Parameters:
  text (string): Text.
  delay (float): Delay.

Return:
  str: string within quotes
  list: leftovers as a list"""

  #not really useful function anymore, discord.ext.command does things lot better

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
@commands.cooldown(1, 10, commands.BucketType.default) # limit, delay, buckettype.default means global cooldown
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
    #if channel given, output message
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
  #waits for reaction
  response_data = await client.wait_for('reaction_add')
  user = response_data[1]
  await channel.send(f'Hello {user.name}!')


@commands.command(name='changestatus')
@check_if_admin()
@commands.cooldown(1, 10, commands.BucketType.default) # limit, delay, buckettype.default means global cooldown
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
  #creates new activity that is starting with 'Playing ...'
  new_activity = discord.Game(name=status_message)
  print(new_status)
  print(status_message)
  #check if online or idle, then add status if it is.
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
    #new event to bot, deprecated manner of creating event. Don't use this.
    if(reaction.message.id == msg_remove_reactions.id):
      await msg_remove_reactions.remove_reaction(reaction, user)


@commands.command(name='loadsettings')
@check_if_admin()
@commands.cooldown(1, 10, commands.BucketType.default) # limit, delay, buckettype.default means global cooldown
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
    #setting found
    if(not is_of_type(setting_dictionary[setting_name]['valuetype'], setting_value)):
      #checking if input is valid type
      await channel.send('Setting is not correct type', reference=ctx.message)
    else:
      #read file
      with open(settings_file, 'r', newline='') as csv_file:
        csv_reader = csv.DictReader(csv_file)
        current_list = {row['setting']: {'description':row['description'], 'value':row['value'], 'valuetype':row['valuetype']} for row in csv_reader}

      with open(settings_file, 'w', newline='') as csv_file:
        #rewrite file
        csv_file.write(header)
        for key in current_list:
          setting = key
          if(setting == setting_name):
            #if setting name found, write new value
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
    #checking if it has anything else than digits, if has then return False, else True
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
  #if had arguments
  if(len(args) >= 1):
    setting_name = args[0]

  setting_found = setting_name in setting_dictionary
  #show settings list
  if(not setting_found):
    settings_message = "Settings: "
    if(not setting_found and setting_name != None):
      #invalid setting name used
      settings_message = f"Setting '{setting_name}' was not found\n" + settings_message
    
    for key in setting_dictionary:
      settings_message += "**" + key + "**"
      settings_message += ", "
    #remove ', ' from the end
    settings_message = settings_message[:-2]

    await channel.send(settings_message, reference=ctx.message)
  #specific setting display values
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

  #load messages from message_list.csv
  with open(message_file, mode='r') as csv_file:
      csv_reader = csv.DictReader(csv_file)
      message_list = {row['message_id']: {'message_type':row['message_type'], 'role':row['role']} for row in csv_reader}
  
  print("Messages loaded!")
  return message_list


async def setup(bot):
    #initial extension loading method
    global command_dictionary, setting_dictionary, admin_ids
    #file reading
    command_dictionary = await reloadCommandList(None)
    setting_dictionary = await load_settings(None)
    admin_ids = get_admin_ids()
    #add commands to bot
    for key in command_dictionary:
      function_name = command_dictionary[key]
      try:
        bot.add_command(globals()[function_name])
      except:
        print(f"{function_name} was not found.")
    #add events
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
  #write to file message_list messagetype signuphere, if it exists, replace it.
  with open(message_file, 'r', newline='') as csv_file:
    #read file
    reader = csv.DictReader(csv_file)
    current_list = {row['message_id']: {'message_type':row['message_type'], 'role':row['role']} for row in reader}
  message_id = 0
  for row in current_list:
    if('signuphere' == current_list[row]['message_type']):
      #find if message_type already exists and save it
      message_id = int(row)
      break
  if(message_id):
    #message type exists, remove it from the file by rewriting everything else
    message_to_delete = await channel.fetch_message(message_id)
    await message_to_delete.delete()
    header = 'message_id,message_type,role'
    with open(message_file, 'w', newline='') as csv_file:
      csv_file.write(header)
      for key in current_list:
        if(key != str(message_id)):
          csv_file.write('\n' + key + ',' + current_list[key]['message_type'] + current_list[key]['role'])
  
  #create signup message and add emotes to it for reaction
  signup_message = (await channel.send(f'React {accept_emoji} to signup!\n\nReact {reject_emoji} or remove {accept_emoji} reaction to remove signup!', ))
  emoji_signup = accept_emoji
  emoji_remove_signup = reject_emoji
  await signup_message.add_reaction(emoji_signup)
  await signup_message.add_reaction(emoji_remove_signup)
  with open(message_file, 'a', newline='') as csv_file:
    #add new signup message to file
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
        #Fetch all servers, add Player role if it's missing and add it to global variable
        print(guild)
        found_signup_role = False
        role_list = await guild.fetch_roles()
        for role in role_list:
          print(role)
          if(role.name == signup_role_name):
            #role found
            found_signup_role = True
            signup_role = role
            print("Player role found!")
            break
        if(not found_signup_role):
          #role not found
          print("Player role created!")
          signup_role = (await guild.create_role(name="Player"))

    @commands.Cog.listener()
    async def on_raw_reaction_add(self, payload):
      message_list = load_messages()
      for key in message_list.keys():
        message_id, emoji, guild, channel = self.common_variables(payload)
        if(str(message_id) == key and message_list[key]['message_type'] == 'signuphere'):
          #Messagetype signuphere. Add and remove sign_up role
          user = payload.member
          username = payload.member.name

          if(emoji.name == accept_emoji):
            #add role if missing
            if(signup_role not in user.roles):
              await user.add_roles(signup_role)

              delete_message = f'{username} signed up!'
              print(delete_message)
              delay = 5
              await self.delete_after_delay(channel, delete_message, delay)

          elif(emoji.name == reject_emoji):
            #add remove role if has it
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
          #message is sign_up message remove role if unchecking reaction and has it
          user_id = payload.user_id
          user = await guild.fetch_member(user_id)
          username = user.name

          if(emoji.name == accept_emoji):
            #player removing signup
            await self.remove_accept_reject_reactions(message_id, channel, user)

            if(signup_role in user.roles):
              #Remove sign_up role if has it
              await user.remove_roles(signup_role)

              delete_message = f'{username} removed sign up!'
              print(delete_message)
              delay = 5
              await self.delete_after_delay(channel, delete_message, delay)

    def common_variables(self, payload):
        #variables used in raw reaction events
        message_id = payload.message_id
        guild_id = payload.guild_id
        channel_id = payload.channel_id
        emoji = payload.emoji
        guild = self.bot.get_guild(guild_id)
        channel = guild.get_channel(channel_id)
        return message_id,emoji,guild,channel

@delayedPrint.error
async def info_error(ctx, error):
    #Error catching and delete message after
    delete_after = await ctx.send(error)
    await asyncio.sleep(5)
    await delete_after.delete()