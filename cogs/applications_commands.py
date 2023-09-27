import nextcord as discord
import json
import chat_exporter
import io
import asyncio
import datetime
import sqlite3
from nextcord import *
from nextcord.ext import commands
from nextcord.ext.commands import has_permissions
from cogs.application import ApplicationView, NewApplicationView

#This will get everything from the config.json file
with open("config.json", mode="r") as config_file:
    config = json.load(config_file)


GUILD_ID = config["guild_id"] #Your Server ID aka Guild ID
TIMEZONE = config["timezone"] #Timezone use https://en.wikipedia.org/wiki/List_of_tz_database_time_zones#List and use the Category 'Time zone abbreviation' for example: Europe = CET, America = EST so you put in EST or EST ...

class Application_Command(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_ready(self):
        print(f'Bot Loaded | applications_commands.py ✅')

    @commands.Cog.listener()
    async def on_bot_shutdown():
        pass

    def applications_main_embed(self):
        """Use this function to generate the main Applications embed"""
        embed = discord.Embed(title=f"<:SundayWings:1155593150446977044> <:Dot:1155593172437708911> <:Dot:1155593172437708911> <:Dot:1155593172437708911> Staff Teams",
                            color=0xc7ccea,
                            description=f'Thank you for your interest in joining our Staff team! Below are our available positions!')
        embed.add_field(name="<:LavenderArrow:1155593160379080714> Ⅰ. Administrators", value="<@&1155490850189623316> are the main logistical team for the server, handling most of the backend work for the server, inclusive but not limited to server partnerships, bot development and handling tickets.", inline=False)
        embed.add_field(name="<:LavenderArrow:1155593160379080714> Ⅱ. Moderators", value="<@&1155501872820518983> are responsible for upholding server rules and to ensure the safety of the community. Answers tickets pertaining to server enquiries should any members encounter any difficulties.", inline=False)
        embed.add_field(name="<:LavenderArrow:1155593160379080714> Ⅲ. Art", value="<@&1155701958448005191> help to create assets related to Sunday for server usage, such as banners. emotes and icons, etc.", inline=False)
        embed.add_field(name="<:LavenderArrow:1155593160379080714> Ⅳ. Event", value="<@&1155702058847051776> are in charge of curating events to help keep the server engaged with activities. ", inline=False)
        embed.add_field(name="<:LavenderArrow:1155593160379080714> Ⅴ. Theorycrafting ", value="<@&1155702114610323577> curate information for Sunday in regards to his kit, ensuring we are up to date with whichever team he works best with.", inline=False)
        embed.add_field(name="<:LavenderArrow:1155593160379080714> Ⅵ. Media ", value="<@&1155702194390171708> help to update our other media extensions apart from the Discord server.", inline=False)
        embed.set_image(url='https://media.discordapp.net/attachments/1155490739631951954/1155629888158572695/Untitled23_20230925001931.png')
        embed.set_footer(text="If there are any issues with the bot, please contact littlemari")
        return embed


    @slash_command(name="application_setup")
    @has_permissions(administrator=True)
    async def application_setup(self, ctx: Interaction):
        """Slash Command to show the Application menu in the Application Channel only needs to be used once"""
        embed = self.applications_main_embed()
        msg = await ctx.channel.send(embed=embed, view=NewApplicationView())
        config['application_msg_id'] = msg.id
        await ctx.response.send_message("Applications embed sent", ephemeral=True)

        with open('config.json', 'w', encoding='utf-8') as config_file:
            json.dump(config, config_file, indent=4)

    @slash_command(name="application_update")
    @has_permissions(administrator=True)
    async def application_update(self, ctx: Interaction):
        """Make sure to use this command in the same channel as you used the `/application_setup` in"""
        self.channel = ctx.channel
        embed = self.applications_main_embed()
        msg = await self.channel.fetch_message(config['application_msg_id'])
        await msg.edit(embed=embed, view=NewApplicationView())
        await ctx.response.send_message("Application Menu was sent!", ephemeral=True)


