from discord.ext import commands
import discord
from functions import set_role
from functions import set_main_category

signup_role_name = 'Player'
player_field_category_name = 'Player Field'

class Setup_events(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_ready(self):

      print("Initializing")

      async for guild in self.bot.fetch_guilds(limit=150):
        #Fetch all servers, add Player role if it's missing and add it to global variable

        print(guild)

        signup_role = None
        main_category = None

        role_list = await guild.fetch_roles()
        category_list = guild.categories

        for role in role_list:
          print(role)
          if(role.name == signup_role_name):
            #role found

            signup_role = role

            print("Player role found!")
            break

        #functions.py setting role there for use in functions
        set_role(signup_role)
        
        for category in category_list:
          #Checks for categories and if main category exists
          print(category)

          if(category.name == player_field_category_name):
            #category found

            main_category = category

            print("Main category found!")
            break

        #functions.py setting main category there for use in functions
        set_main_category(main_category)



async def setup(bot):
    #add events
    await bot.add_cog(Setup_events(bot))