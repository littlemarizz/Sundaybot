import nextcord as discord
import asyncio
import json
import sqlite3
import datetime
import chat_exporter
import io
import requests
from nextcord.ext import commands
from nextcord import File, ButtonStyle, Embed, Color, SelectOption
from nextcord.ui import Button, View, Select
from cogs.ticket_system import Ticket_System
from cogs.ticket_commands import Ticket_Command
from cogs.application import ApplicationView
from cogs.applications_commands import Application_Command
from nextcord import File, ButtonStyle, Embed, Color, SelectOption
from nextcord.ui import Button, View, Select

#This will get everything from the config.json file
with open("config.json", mode="r") as config_file:
    config = json.load(config_file)

BOT_TOKEN = config["token"]  #Your Bot Token from https://discord.dev
GUILD_ID = config["guild_id"] #Your Server ID aka Guild ID
CATEGORY_ID1 = config["category_id_1"] #Category 1 where the Bot should open the Ticket for the Ticket option 1
CATEGORY_ID2 = config["category_id_2"] #Category 2 where the Bot should open the Ticket for the Ticket option 2

#intents
intents = discord.Intents.all()
intents.typing = False
intents.presences = False
intents.message_content = True
intents.members = True

bot = commands.Bot(command_prefix=commands.when_mentioned, intents=discord.Intents.all())
BOT_TOKEN = "MTE1NTUyNTYzNzg4OTU5MzQ0Ng.GwDuqj.F7xT0EYbe19RtLdXTA8MxB5mW0_qsepOUB7kKo"

bot = commands.Bot(intents=intents.all())

bot = commands.Bot(command_prefix='.',
                   intents=discord.Intents.all(),
                   status=discord.Status.online,
                   activity=discord.Activity(type=discord.ActivityType.watching, name="over my family")
                   )

@bot.event
async def on_member_join(member):
    channel = bot.get_channel(1155554513898455050)
    embed=discord.Embed(
        title="<:SundayWings:1155593150446977044> <:Dot:1155593172437708911> <:Dot:1155593172437708911> Welcome to Sunday Mains!",
        description=f"{member.mention} Thank you for joining! We hope you have a wonderful time here! Do head on over to <#1155554547482230867> to verify, and <#1155554613051805756> to get roles.",
        color=0xc7ccea,
    )
    embed.set_image(url='https://media.discordapp.net/attachments/1155490739631951954/1155564049514381402/Untitled19_20230924181947.png')
    await channel.send(embed=embed)

@bot.event
async def on_ready():
    print(f'Bot Logged | {bot.user.name}')
    print("chicken chicken")

bot.add_cog(Ticket_System(bot))
bot.add_cog(Ticket_Command(bot))
bot.add_cog(Application_Command(bot))
bot.run(BOT_TOKEN)