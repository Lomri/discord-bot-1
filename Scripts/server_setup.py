from discord.ext import commands
from functions import set_role

signup_role_name = 'Player'

class Setup_events(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_ready(self):

      print("Initializing")

      signup_role = None

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
          signup_role = (await guild.create_role(name=signup_role_name))

        #functions.py setting role there for use in functions
        set_role(signup_role)



async def setup(bot):
    #add events
    await bot.add_cog(Setup_events(bot))