def printText(*arguments):
    arguments_as_string = ""
    for list in arguments:
      for item in list:
        arguments_as_string += item
        arguments_as_string += " "
    arguments_as_string = arguments_as_string[:-1]
    return arguments_as_string

def find_first_string(arguments):
    if(arguments):
      arguments_as_string = "".join(arguments)
      match = re.search('"([^"]*)"', arguments_as_string)
      try:
        if(match):
            return match.group(1)
      except ValueError:
        return "No message to print"
    else:
        return "No message to print"