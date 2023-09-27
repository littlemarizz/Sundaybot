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
from cogs.ticket_system import MyView

#This will get everything from the config.json file
with open("config.json", mode="r") as config_file:
    config = json.load(config_file)

TICKET_CHANNEL = config["ticket_channel_id"] #Ticket Channel where the Bot should send the SelectMenu + Embed
GUILD_ID = config["guild_id"] #Your Server ID aka Guild ID

LOG_CHANNEL = config["log_channel_id"] #Where the Bot should log everything
TIMEZONE = config["timezone"] #Timezone use https://en.wikipedia.org/wiki/List_of_tz_database_time_zones#List and use the Category 'Time zone abbreviation' for example: Europe = CET, America = EST so you put in EST or EST ...

#This will create and connect to the database
conn = sqlite3.connect('SundayTickets.db')
cur = conn.cursor()

#Create the table if it doesn't exist
cur.execute("""CREATE TABLE IF NOT EXISTS ticket
           (id INTEGER PRIMARY KEY AUTOINCREMENT, discord_name TEXT, discord_id INTEGER, ticket_created TIMESTAMP DEFAULT CURRENT_TIMESTAMP)""")
conn.commit()

class Ticket_Command(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_ready(self):
        print(f'Bot Loaded | ticket_commands.py ✅')

    @commands.Cog.listener()
    async def on_bot_shutdown():
        cur.close()
        conn.close()


    #Slash Command to show the Ticket Menu in the Ticket Channel only needs to be used once
    @slash_command(name="ticket")
    @has_permissions(administrator=True)
    async def ticket(self, ctx: Interaction):
        # self.channel = self.bot.get_channel(TICKET_CHANNEL)
        self.channel = ctx.channel
        embed = discord.Embed(title=f"<:SundayWings:1155593150446977044> <:Dot:1155593172437708911> <:Dot:1155593172437708911> <:Dot:1155593172437708911> Contact Staff",
                               color=0xc7ccea,
                               description=f"If you wish to make a ticket, please use the droplist below to contact Staff! We will be with you shortly! Random tickets made for fun will not be entertained.",
                               )
        embed.set_image(url='https://media.discordapp.net/attachments/1155490739631951954/1155629888158572695/Untitled23_20230925001931.png')
        embed.set_footer(text="If there are any issues with the bot, please contact littlemari")
        await self.channel.send(embed=embed, view=MyView(self.bot))
        await ctx.response.send_message("Ticket Menu was sent!", ephemeral=True)

    #Slash Command to add Members to the Ticket
    @slash_command(name="add", description="Add a Member to the Ticket")
    async def add(self, ctx: Interaction, member = SlashOption(discord.member, description="Which Member you want to add to the Ticket", required = True)):
        if "ticket-" in ctx.channel.name or "ticket-closed-" in ctx.channel.name:
            await ctx.channel.set_permissions(member, send_messages=True, read_messages=True, add_reactions=False,
                                                embed_links=True, attach_files=True, read_message_history=True,
                                                external_emojis=True)
            self.embed = discord.Embed(description=f'Added {member.mention} to this Ticket <#{ctx.channel.id}>! \n Use /remove to remove a User.', color=discord.colour.Color.green())
            await ctx.response.send_message(embed=self.embed)
        else:
            self.embed = discord.Embed(description=f'You can only use this command in a Ticket!', color=discord.colour.Color.red())
            await ctx.response.send_message(embed=self.embed)

    #Slash Command to remove Members from the Ticket
    @slash_command(name="remove", description="Remove a Member from the Ticket")
    async def remove(self, ctx: Interaction, member = SlashOption(discord.Member, description="Which Member you want to remove from the Ticket", required = True)):
        if "ticket-" in ctx.channel.name or "ticket-closed-" in ctx.channel.name:
            await ctx.channel.set_permissions(member, send_messages=False, read_messages=False, add_reactions=False,
                                                embed_links=False, attach_files=False, read_message_history=False,
                                                external_emojis=False)
            self.embed = discord.Embed(description=f'Removed {member.mention} from this Ticket <#{ctx.channel.id}>! \n Use /add to add a User.', color=discord.colour.Color.green())
            await ctx.response.send_message(embed=self.embed)
        else:
            self.embed = discord.Embed(description=f'You can only use this command in a Ticket!', color=discord.colour.Color.red())
            await ctx.response.send_message(embed=self.embed)

    @slash_command(name="delete", description="Delete the Ticket")
    async def delete_ticket(self, ctx: Interaction):
        guild = self.bot.get_guild(GUILD_ID)
        channel = self.bot.get_channel(LOG_CHANNEL)
        ticket_creator = int(ctx.channel.topic)

        cur.execute("DELETE FROM ticket WHERE discord_id=?", (ticket_creator,)) #Delete the Ticket from the Database
        conn.commit()

        #Create Transcript
        military_time: bool = True
        transcript = await chat_exporter.export(
            ctx.channel,
            limit=200,
            tz_info=TIMEZONE,
            military_time=military_time,
            bot=self.bot,
        )
        if transcript is None:
            return

        transcript_file = discord.File(
            io.BytesIO(transcript.encode()),
            filename=f"transcript-{ctx.channel.name}.html")
        transcript_file2 = discord.File(
            io.BytesIO(transcript.encode()),
            filename=f"transcript-{ctx.channel.name}.html")

        ticket_creator = Guild.get_member(ticket_creator)
        embed = discord.Embed(description=f'Ticket is deleting in 5 seconds.', color=0xff0000)
        transcript_info = discord.Embed(title=f"Ticket Deleting | {ctx.channel.name}", description=f"Ticket from: {ticket_creator.mention}\nTicket Name: {ctx.channel.name} \n Closed from: {ctx.author.mention}", color=discord.colour.Color.blue())

        await ctx.response.send_message(embed=embed)
        #Checks if the user has his DMs enabled/disabled
        try:
            await ticket_creator.send(embed=transcript_info, file=transcript_file)
        except:
            transcript_info.add_field(name="Error", value="Couldn't send the Transcript to the User because he has his DMs disabled!", inline=True)
        await channel.send(embed=transcript_info, file=transcript_file2)
        await asyncio.sleep(3)
        await ctx.channel.delete(reason="Ticket got Deleted!")