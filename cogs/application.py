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
from nextcord import File, ButtonStyle, Embed, Color, SelectOption
from nextcord.ui import Button, View, Select

#This will get everything from the config.json file
with open("config.json", mode="r") as config_file:
    config = json.load(config_file)

# This is actually not needed
# class Staff_Applications(commands.Cog):
#     def __init__(self, bot):
#         self.bot = bot

#     @commands.Cog.listener()
#     async def on_ready(self):
#         print(f'Ur Mom Loaded | Staff_Applications.py ✅')

class ApplicationView(View):
    """The old select menu view"""
    def __init__(self, bot):
        self.bot = bot
        super().__init__(timeout=None)

    @discord.ui.select(
        custom_id="application",
        placeholder="Please select a staff position",
        options=[
            discord.SelectOption(
                label="Moderator Application",  #Name of the 1 Select Menu Option
                value="a1"   #Don't change this value otherwise the code will not work anymore!!!!
            ),
            discord.SelectOption(
                label="Art Staff Application",  #Name of the 2 Select Menu Option
                value="a2"   #Don't change this value otherwise the code will not work anymore!!!!
            ),
            discord.SelectOption(
                label="Event Staff Application",  #Name of the 3 Select Menu Option
                value="a3"   #Don't change this value otherwise the code will not work anymore!!!!
            ),
            discord.SelectOption(
                label="TC Staff Application",  #Name of the 4 Select Menu Option
                value="a4"   #Don't change this value otherwise the code will not work anymore!!!!
            ),
            discord.SelectOption(
                label="Media Staff Application",  #Name of the 5 Select Menu Option
                value="a5"   #Don't change this value otherwise the code will not work anymore!!!!
            )
        ]
    )
    async def callback(self, select: Select, interaction: Interaction):
        if select.values[0] == "a1":
            embed = discord.Embed(description=f'Please click on the link to locate our Moderator Applications --> https://forms.gle/Go9tJzJZe4wY11q97',
                    color=0xc7ccea)

        if select.values[0] == "a2":
            embed = discord.Embed(description=f'Please click on the link to locate our Art Staff Applications --> https://forms.gle/Hipe1TZDZTC7acSs7',
                    color=0xc7ccea)

        if select.values[0] == "a3":
            embed = discord.Embed(description=f'Please click on the link to locate our Event Staff Applications --> https://forms.gle/2amzNKjmV9RS5WMW8',
                    color=0xc7ccea)

        if select.values[0] == "a4":
            embed = discord.Embed(description=f'Please click on the link to locate our TC Staff Applications --> https://forms.gle/iAFKFhsRB3ZcDLMF9',
                    color=0xc7ccea)

        if select.values[0] == "a5":
            embed = discord.Embed(description=f'Please click on the link to locate our Media Staff Applications --> https://forms.gle/7QeugyZUT88QKQXY9',
                    color=0xc7ccea)
        embed.set_image(url='https://media.discordapp.net/attachments/1155490739631951954/1155629888158572695/Untitled23_20230925001931.png')
        embed.set_footer(text="If there are any issues with the bot, please contact littlemari")
        await interaction.message.edit(embed=embed, view=ApplicationView(bot=self.bot)) #This will reset the SelectMenu in the Ticket Channel
        await asyncio.sleep(1)

class NewApplicationView(View):
    """The new view with buttons"""
    def __init__(self):
        super().__init__(timeout=None)

    @discord.ui.button(label="Moderator", style=discord.ButtonStyle.blurple)
    async def mod(self, view,  interaction: Interaction):
        embed = discord.Embed(description=f'Please click on the link to locate our Moderator Applications --> https://forms.gle/Go9tJzJZe4wY11q97',
                    color=0xc7ccea)
        await interaction.response.send_message(embed=embed, ephemeral=True)

    @discord.ui.button(label="Art", style=discord.ButtonStyle.blurple)
    async def art(self, view, interaction: Interaction):
        embed = discord.Embed(description=f'Please click on the link to locate our Art Staff Applications --> https://forms.gle/Hipe1TZDZTC7acSs7',
                    color=0xc7ccea)
        await interaction.response.send_message(embed=embed, ephemeral=True)

    @discord.ui.button(label="Event", style=discord.ButtonStyle.blurple)
    async def event(self, view, interaction: Interaction):
        embed = discord.Embed(description=f'Please click on the link to locate our Event Staff Applications --> https://forms.gle/2amzNKjmV9RS5WMW8',
                    color=0xc7ccea)
        await interaction.response.send_message(embed=embed, ephemeral=True)

    @discord.ui.button(label="Theorycrafting", style=discord.ButtonStyle.blurple)
    async def tc(self, view, interaction: Interaction):
        embed = discord.Embed(description=f'Please click on the link to locate our TC Staff Applications --> https://forms.gle/iAFKFhsRB3ZcDLMF9',
                    color=0xc7ccea)
        await interaction.response.send_message(embed=embed, ephemeral=True)

    @discord.ui.button(label="Media", style=discord.ButtonStyle.blurple)
    async def media(self, view, interaction: Interaction):
        embed = discord.Embed(description=f'Please click on the link to locate our Media Staff Applications --> https://forms.gle/7QeugyZUT88QKQXY9',
                    color=0xc7ccea)
        await interaction.response.send_message(embed=embed, ephemeral=True)


