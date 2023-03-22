import re
import asyncio

async def printText(*arguments):
  """
  Prints everything after the command

  Parameters:
  tuple:
    channel: channel to send message in
    list: list for printing

  Output:
  Sends the text as a message
  """
  if(len(arguments) > 1):
    channel, arg_list = arguments

  arguments_as_string = ""
  for item in arg_list:
    arguments_as_string += item
    arguments_as_string += " "
  arguments_as_string = arguments_as_string[:-1]
  
  await channel.send(arguments_as_string)
  return True

async def delayedPrint(*arguments):
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
  print(arguments)
  if(len(arguments) > 1):
    channel, arg_list = arguments
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
    channel = arguments[0]
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