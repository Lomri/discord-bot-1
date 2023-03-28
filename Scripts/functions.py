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
tree = None


accept_emoji = '✅'
reject_emoji = '❎'
checkmark_emoji = '✓'
x_emoji = 'X'

#names used for finding names for roles, channels and categories
role_name_list = ['Player']
channel_name_list = ['default-channel']
category_name_list = ['Player Field']

signup_role = None

main_category = None

admin_role = 'Admin'

# limit, delay, buckettype.default means global cooldown
global_10_second_cooldown = commands.CooldownMapping.from_cooldown(1, 10, commands.BucketType.default)
global_5_second_cooldown = commands.CooldownMapping.from_cooldown(1, 5, commands.BucketType.default)

#converter expected variable type, description for that one parameter
message_parameter = commands.parameter(converter=str, description="Text as message to be printed back")
delay_in_seconds_float_parameter = commands.parameter(converter=float, description="Delay in seconds")

async def check_if_admin(ctx):
    #checking if command invoker has a role with name 'Admin'
    print("Checking if admin")

    # if user has a role called Admin or user id is in the admins_list.csv file, return true
    if(ctx.message.author.id in admin_ids):
      return True

    # if user has a role called Admin or user id is in the admins_list.csv file, return true
    if(ctx.message.author.id in admin_ids):
      return True
    
    for role in ctx.message.author.roles:
      if(role.name == 'Admin'):
        return True

async def check_if_bot_admin(ctx):
    #checking if command invoker has a role with name 'Admin'
    print("Checking if bot admin")

    for id in admin_ids:
      if(int(id) == ctx.author.id):
        print("Is bot admin")
        return True
      
    message = f"{ctx.author.name} is not a bot admin!"
    await delete_after_delay(ctx, message, 5)

    return False

async def check_if_player(ctx):
    #checking if command invoker has a role with name 'Player'
    print("Checking if player")

    for role in ctx.message.author.roles:
      if(role.name == 'Player'):
        return True
      
    message = f"{ctx.author.name} is not a player!"
    await delete_after_delay(ctx, message, 5)

    return False


@commands.command(name='sync', checks=[check_if_bot_admin])
async def synchronizeSlashCommands(ctx):
  await tree.sync()
  print("Tree synced")

@commands.hybrid_command(name='slash', with_app_command=True)
async def slashCommand(ctx: commands.Context):
  await ctx.send("SLAAAAAASH!")

@commands.command(name='print')
async def printText(ctx, *,  message = message_parameter):
  """
Bot prints the text given."""

  channel = ctx
  
  await channel.send(message)


@commands.command(name='dprint', checks=[check_if_admin])
async def delayedPrint(ctx, delay = delay_in_seconds_float_parameter, *, message = message_parameter):
  """
Bot prints the text given as reply after delay (in seconds)."""

  channel = ctx

  await asyncio.sleep(delay)
  await channel.send(message, reference=ctx.message) #reference to ctx.message means reply to message

@commands.command(name='reload', checks=[check_if_admin], cooldown=global_10_second_cooldown)
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


@commands.command(name='changestatus', checks=[check_if_admin], cooldown=global_10_second_cooldown)
async def change_status(ctx: commands.Context, status: str, *status_message: str) -> None:
  """
  Changes bot status to idle or online and adds text to "Playing ..." status.

  Parameters:
      ctx (commands.Context): The context of the command.
      status (str): The desired status of the bot. Either "idle" or "online".
      status_message (str): The message to display with the bot's status.

  Output:
      None. The bot status changes based on the input parameters.
  """
  bot = ctx.bot

  if status.lower() not in ["idle", "online"]:
    await ctx.send("Invalid status. Please enter 'idle' or 'online'.")
    return

  if not status_message:
    await ctx.send("Please enter a status message.")
    return

  # creates new activity that is starting with 'Playing ...'
  new_activity = discord.Game(name=' '.join(status_message))

  # check if online or idle, then add status if it is.
  if status.lower() == "idle":
    await bot.change_presence(status=discord.Status.idle, activity=new_activity)

  elif status.lower() == "online":
    await bot.change_presence(status=discord.Status.online, activity=new_activity)


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


@commands.command(name='loadsettings', checks=[check_if_admin], cooldown=global_10_second_cooldown)
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


@commands.command(name='changesetting', checks=[check_if_admin])
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
      raise ValueError(f"Given value {value} is not considered as 'bool'")
    
    else:
      return True
    
  if(valuetype == "int"):
    #checking if it has anything else than digits, if has then return False, else True
    if(string.ascii_letters in value or string.punctuation in value):
      raise ValueError(f"Given value {value} is not considered as 'int'")
    
    else:
      return True
    
  return True

@commands.command(name='settings', checks=[check_if_admin], cooldown=global_10_second_cooldown)
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
    global command_dictionary, setting_dictionary, admin_ids, tree

    #file reading
    command_dictionary = await reloadCommandList(None)
    setting_dictionary = await load_settings(None)

    admin_ids = get_admin_ids()

    tree = bot.tree

    #add commands to bot
    for key in command_dictionary:
      function_name = command_dictionary[key]

      try:
        bot.add_command(globals()[function_name])

      except:
        print(f"{function_name} was not found.")

    #add Cog.listeners from this module that are within Events
    await bot.add_cog(Events(bot))

    global settings

    #Make a Setting class with validate function as first parameter, second parameter is name of list and third parameter is list of names to find for
    roles = Setting(role_validate, "Roles", role_name_list)
    channels = Setting(channel_validate, "Channels", channel_name_list)
    categories = Setting(category_validate, "Categories", category_name_list)

    #adds to settings.list for easier iteration
    settings.add(roles)
    settings.add(channels)
    settings.add(categories)


@commands.command(name='validatesetup', checks=[check_if_admin], cooldown=global_10_second_cooldown)
async def validateServerSetup(ctx):
  #Checks Settings class for settings to validate, settings that are None are printed with X rest are with ✓
  global settings

  new_list = []

  string = '```Settings validation:\n'

  #iterate all roles channels and categories to check if they are set up
  for setting in settings.list:

    #validate() for each setting to check if value is found
    new_list = await setting.validate(ctx)
    string += str(setting)

    string += ':\n'
    for row in new_list:
      #get name of item and value that is found item value
      name, value = row

      #item name
      string += '  '
      string += name

      #if item was found show checkmark_emoji, else x_emoji
      string += '  '
      if(value != None):
        string += checkmark_emoji

      else:
        string += x_emoji

      string += '\n'

    string += '\n'

  string += '```'

  await ctx.send(string)


async def category_validate(ctx, category_check_list: list) -> discord.CategoryChannel:
  category_list = ctx.guild.categories

  return_list = []

  for category in category_check_list:
    value = None
    for item in category_list:
      if(category == item.name):
        value = item

    return_list.append((category, value))


  return return_list


async def channel_validate(ctx, channel_check_list: list) -> discord.CategoryChannel:
  channel_list = ctx.guild.categories

  return_list = []

  for channel in channel_check_list:
    value = None
    for item in channel_list:
      if(channel == item.name):
        value = item

    return_list.append((channel, value))


  return return_list


async def role_validate(ctx, roles_check_list: list) -> discord.Role:
  role_list = await ctx.guild.fetch_roles()

  return_list = []

  for role in roles_check_list:
    value = None
    for item in role_list:
      if(role == item.name):
        value = item

    return_list.append((role, value))


  return return_list

#class to make setting have validation function and return value after validation
class Setting:
  def __init__(self, validation_function, list_name, name: list) -> None:
    self.validation_function = validation_function
    self.__list_name = list_name
    self.__name = name

  async def validate(self, ctx):
    new_list = await self.validation_function(ctx, self.__name)

    return new_list
  
  def __str__(self) -> str:
    return self.__list_name
  
#class for making a list of settings to run .validate() on each setting
class Settings:
  def __init__(self) -> None:
    self.list = []

  def add(self, setting: Setting):
    self.list.append(setting)

settings = Settings()

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

#setting role from server_setup.py finds roles by names in on_ready and gives to functions.py for use
def set_role(role):
  global signup_role

  signup_role = role


#setting main category from server_setup.py finds categories in on_ready and give main category to functions.py for use
def set_main_category(category):
  global main_category

  main_category = category


class Events(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

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
              delay = 5

              print(delete_message)

              await self.delete_after_delay(channel, delete_message, delay)

          elif(emoji.name == reject_emoji):
            #add remove role if has it
            user = payload.member

            await self.remove_accept_reject_reactions(message_id, channel, user)

            if(signup_role in user.roles):
              await user.remove_roles(signup_role)

              delete_message = f'{username} removed sign up!'
              delay = 5

              print(delete_message)

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
              delay = 5

              print(delete_message)

              await self.delete_after_delay(channel, delete_message, delay)

    @commands.Cog.listener()
    async def on_command_error(self, ctx, error):
        #Error handler, prints error to user referring to message error was found

        #error is tuple, convert to list incase multiple errors come
        error_list = list(error.args)
        
        #initialize error message
        space_count = 0
        error_message = f'```'

        #loop for errors
        for error in error_list:
          error_sectioned = error.split(": ")

          #split sections for easier readability
          for section in error_sectioned:
            error_message += ' ' * space_count + section + ':'
            error_message += '\n'
            space_count += 4

        #remove \n and : from the end
        error_message = error_message[:-2]
        error_message += '```'

        #make a message to notify user about errors and catch the message for delete later
        delete_after = await ctx.send(error_message, reference=ctx.message)

        await asyncio.sleep(10)
        await delete_after.delete()

    def common_variables(self, payload):
        #variables used in raw reaction events

        message_id = payload.message_id
        guild_id = payload.guild_id
        channel_id = payload.channel_id
        emoji = payload.emoji

        guild = self.bot.get_guild(guild_id)
        channel = guild.get_channel(channel_id)

        return message_id,emoji,guild,channel

#sends a message to a channel and deletes it after the delay
async def delete_after_delay(channel: discord.abc.Messageable, delete_message: str, delay: float):
    delete_after = await channel.send(delete_message)

    await asyncio.sleep(delay)
    await delete_after.delete()

# Bot command to change the topic of the channel
@commands.command(name='topic', checks=[check_if_admin], cooldown=global_5_second_cooldown)
async def command_change_channel_topic(ctx, *, topic):
    """
    Change the topic of the channel
    
    Usage: !topic <topic>
    
    Example: !topic This is a new topic"""
    
    await ctx.channel.edit(topic=topic)

# Function to change the topic for the channel
# Can be used as a part of a command or a task
async def change_channel_topic(channel, topic):
    await channel.edit(topic=topic)