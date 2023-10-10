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

#This will get everything from the config.json file
with open("config.json", mode="r") as config_file:
    config = json.load(config_file)

GUILD_ID = config["guild_id"] #Your Server ID aka Guild ID
TICKET_CHANNEL = config["ticket_channel_id"] #Ticket Channel where the Bot should send the SelectMenu + Embed

CATEGORY_ID1 = config["category_id_1"] #Category 1 where the Bot should open the Ticket for the Ticket option 1
CATEGORY_ID2 = config["category_id_2"] #Category 2 where the Bot should open the Ticket for the Ticket option 2

TEAM_ROLE1 = config["team_role_id_1"] #Mod Team role id
TEAM_ROLE2 = config["team_role_id_2"] #Trial Mod Team role id
TEAM_ROLE3 = config["team_role_id_3"] #Admin Team role id

LOG_CHANNEL = config["log_channel_id"] #Where the Bot should log everything
TIMEZONE = config["timezone"] #Timezone use https://en.wikipedia.org/wiki/List_of_tz_database_time_zones#List and use the Category 'Time zone abbreviation' for example: Europe = CET, America = EST so you put in EST or EST ...

#This will create and connect to the database
conn = sqlite3.connect('SundayTickets.db')
cur = conn.cursor()

#Create the table if it doesn't exist
cur.execute("""CREATE TABLE IF NOT EXISTS ticket
           (id INTEGER PRIMARY KEY AUTOINCREMENT, discord_name TEXT, discord_id INTEGER, ticket_created TIMESTAMP DEFAULT CURRENT_TIMESTAMP)""")
conn.commit()

class Ticket_System(commands.Cog):

    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_ready(self):
        print(f'Bot Loaded | ticket_system.py ✅')
        self.bot.add_view(MyView(bot=self.bot))
        self.bot.add_view(CloseButton(bot=self.bot))
        self.bot.add_view(TicketOptions(bot=self.bot))

    #Closes the Connection to the Database when shutting down the Bot
    @commands.Cog.listener()
    async def on_bot_shutdown():
        cur.close()
        conn.close()

class MyView(discord.ui.View):
    def __init__(self, bot):
        self.bot = bot
        super().__init__(timeout=None)

    @discord.ui.select(
        custom_id="support",
        placeholder="Please pick a ticket option",
        options=[
            discord.SelectOption(
                label="Partnership",  #Name of the 1 Select Menu Option
                description="Use this for Partnership requests",  #Description of the 1 Select Menu Option
                emoji="<:LavenderDot:1155593156641951916>",        #Emoji of the 1 Option  if you want a Custom Emoji read this  https://github.com/Simoneeeeeeee/Discord-Select-Menu-Ticket-Bot/tree/main#how-to-use-custom-emojis-from-your-discors-server-in-the-select-menu
                value="support1"   #Don't change this value otherwise the code will not work anymore!!!!
            ),
            discord.SelectOption(
                label="Moderation",  #Name of the 2 Select Menu Option
                description="Use this for any enquiries regarding the server", #Description of the 2 Select Menu Option
                emoji="<:WhiteDot:1155593166196588554>",        #Emoji of the 2 Option  if you want a Custom Emoji read this  https://github.com/Simoneeeeeeee/Discord-Select-Menu-Ticket-Bot/tree/main#how-to-use-custom-emojis-from-your-discors-server-in-the-select-menu
                value="support2"   #Don't change this value otherwise the code will not work anymore!!!!
            )
        ]
    )
    async def callback(self, select, interaction):
        if select.values[0] == "support1":
            if interaction.channel.id == TICKET_CHANNEL:
                guild = self.bot.get_guild(GUILD_ID)
                member_id = interaction.user.id
                member_name = interaction.user.name
                cur.execute("SELECT discord_id FROM ticket WHERE discord_id=?", (member_id,)) #Check if the User already has a Ticket open
                existing_ticket = cur.fetchone()
                if existing_ticket is None:
                    cur.execute("INSERT INTO ticket (discord_name, discord_id) VALUES (?, ?)", (member_name, member_id)) #If the User doesn't have a Ticket open it will insert the User into the Database and create a Ticket
                    conn.commit()
                    cur.execute("SELECT id FROM ticket WHERE discord_id=?", (member_id,)) #Get the Ticket Number from the Database
                    ticket_number = cur.fetchone()
                    category = self.bot.get_channel(CATEGORY_ID1)
                    ticket_channel = await guild.create_text_channel(f"{member_name}-ticket", category=category)

                    await ticket_channel.set_permissions(guild.get_role(TEAM_ROLE3), send_messages=True, read_messages=True, add_reactions=True, #Set the Permissions for the Staff Team
                                                        embed_links=True, attach_files=True, read_message_history=True,
                                                        external_emojis=True)
                    await ticket_channel.set_permissions(interaction.user, send_messages=True, read_messages=True, add_reactions=True, #Set the Permissions for the User
                                                        embed_links=True, attach_files=True, read_message_history=True,
                                                        external_emojis=True)
                    embed = discord.Embed(description=f'Welcome {interaction.user.mention},\n'
                                                       'Thank you for your interest in a partnership, do send us a link to your server and our staff will be with you shortly!',   #Ticket Welcome message
                                                    color=0xb9b6d3)
                    await ticket_channel.send("<@&1155490850189623316>", embed=embed, view=CloseButton(bot=self.bot))

                    embed = discord.Embed(description=f'📬 Ticket was Created! Look here --> {ticket_channel.mention}',
                                            color=0xA59ED2)
                    await interaction.response.send_message(embed=embed, ephemeral=True)
                    await asyncio.sleep(1)
                    embed = discord.Embed(title=f"<:SundayWings:1155593150446977044> <:Dot:1155593172437708911> <:Dot:1155593172437708911> <:Dot:1155593172437708911> Contact Staff",
                               color=0xc7ccea,
                               description=f"If you wish to make a ticket, please use the droplist below to contact Staff! We will be with you shortly! Random tickets made for fun will not be entertained.",
                               )
                    embed.set_image(url='https://media.discordapp.net/attachments/1155490739631951954/1155629888158572695/Untitled23_20230925001931.png')
                    embed.set_footer(text="If there are any issues with the bot, please contact littlemari")
                    await interaction.message.edit(embed=embed, view=MyView(bot=self.bot)) #This will reset the SelectMenu in the Ticket Channel
        if select.values[0] == "support2":
            if interaction.channel.id == TICKET_CHANNEL:
                guild = self.bot.get_guild(GUILD_ID)
                member_id = interaction.user.id
                member_name = interaction.user.name
                cur.execute("SELECT discord_id FROM ticket WHERE discord_id=?", (member_id,)) #Check if the User already has a Ticket open
                existing_ticket = cur.fetchone()
                if existing_ticket is None:
                    cur.execute("INSERT INTO ticket (discord_name, discord_id) VALUES (?, ?)", (member_name, member_id)) #If the User doesn't have a Ticket open it will insert the User into the Database and create a Ticket
                    conn.commit()
                    cur.execute("SELECT id FROM ticket WHERE discord_id=?", (member_id,)) #Get the Ticket Number from the Database
                    ticket_number = cur.fetchone()
                    category = self.bot.get_channel(CATEGORY_ID2)
                    ticket_channel = await guild.create_text_channel(f"{member_name}-ticket", category=category)

                    await ticket_channel.set_permissions(guild.get_role(TEAM_ROLE2), send_messages=True, read_messages=True, add_reactions=True, #Set the Permissions for the Staff Team
                                                        embed_links=True, attach_files=True, read_message_history=True,
                                                        external_emojis=True)
                    await ticket_channel.set_permissions(guild.get_role(TEAM_ROLE1), send_messages=True, read_messages=True, add_reactions=True, #Set the Permissions for the Staff Team
                                                        embed_links=True, attach_files=True, read_message_history=True,
                                                        external_emojis=True)
                    await ticket_channel.set_permissions(interaction.user, send_messages=True, read_messages=True, add_reactions=True, #Set the Permissions for the User
                                                        embed_links=True, attach_files=True, read_message_history=True,
                                                        external_emojis=True)
                    embed = discord.Embed(description=f'Welcome {interaction.user.mention},\n' #Ticket Welcome message
                                                       'please describe any enquiries you may have and our staff will be with you shortly!',
                                                    color=discord.colour.Color.blue())
                    await ticket_channel.send("@&1155501872820518983> <@&1155501929040986243>", embed=embed, view=CloseButton(bot=self.bot))

                    embed = discord.Embed(description=f'📬 Ticket was Created! Look here --> {ticket_channel.mention}',
                                            color=0xb9b6d3)
                    await interaction.response.send_message(embed=embed, ephemeral=True)
                    await asyncio.sleep(1)
                    embed = discord.Embed(title=f"<:SundayWings:1155593150446977044> <:Dot:1155593172437708911> <:Dot:1155593172437708911> <:Dot:1155593172437708911> Contact Staff",
                               color=0xc7ccea,
                               description=f"If you wish to make a ticket, please use the droplist below to contact Staff! We will be with you shortly! Random tickets made for fun will not be entertained.",
                               )
                    embed.set_image(url='https://media.discordapp.net/attachments/1155490739631951954/1155629888158572695/Untitled23_20230925001931.png')
                    embed.set_footer(text="If there are any issues with the bot, please contact littlemari")
                    await interaction.message.edit(embed=embed, view=MyView(bot=self.bot)) #This will reset the SelectMenu in the Ticket Channel
                    await asyncio.sleep(1)
        return

#First Button for the Ticket
class CloseButton(discord.ui.View):
    def __init__(self, bot):
        self.bot = bot
        super().__init__(timeout=None)

    @discord.ui.button(label="Close Ticket 🎫", style = discord.ButtonStyle.blurple, custom_id="close")
    async def close(self, button: discord.ui.Button, interaction: discord.Interaction):
        guild = self.bot.get_guild(GUILD_ID)
        member_id = interaction.user.id
        member_name = interaction.user.name
        cur.execute("SELECT id FROM ticket WHERE discord_id=?", (member_id,))  # Get the Ticket Number from the Database
        ticket_number = cur.fetchone()
        ticket_creator = guild.get_member(member_id)

        embed = discord.Embed(title="Ticket Closed 🎫", description="Press Reopen to open the Ticket again or Delete to delete the Ticket!", color=0x9288c7)
        await interaction.channel.set_permissions(ticket_creator, send_messages=False, read_messages=False, add_reactions=False,
                                                        embed_links=False, attach_files=False, read_message_history=False, #Set the Permissions for the User if the Ticket is closed
                                                        external_emojis=False)
        await interaction.channel.edit(name=f"ticket-closed-{member_name}")
        await interaction.response.send_message(embed=embed, view=TicketOptions(bot=self.bot)) #This will show the User the TicketOptions View
        button.disabled = True
        await interaction.message.edit(view=self)


#Buttons to reopen or delete the Ticket
class TicketOptions(discord.ui.View):
    def __init__(self, bot):
        self.bot = bot
        super().__init__(timeout=None)

    @discord.ui.button(label="Reopen Ticket 🎫", style = discord.ButtonStyle.green, custom_id="reopen")
    async def reopen_button(self, button: discord.ui.Button, interaction: discord.Interaction):
        guild = self.bot.get_guild(GUILD_ID)
        member_id = interaction.user.id
        member_name = interaction.user.name
        cur.execute("SELECT id FROM ticket WHERE discord_id=?", (member_id,)) #Get the Ticket Number from the Database
        ticket_number = cur.fetchone()
        embed = discord.Embed(title="Ticket Reopened 🎫", description="Press `Delete Ticket` to delete the Ticket!", color=0x9288c7) #The Embed for the Ticket Channel when it got reopened
        ticket_creator = guild.get_member(member_id)
        await interaction.channel.set_permissions(ticket_creator, send_messages=True, read_messages=True, add_reactions=False,
                                                        embed_links=True, attach_files=True, read_message_history=True, #Set the Permissions for the User if the Ticket is reopened
                                                        external_emojis=False)
        await interaction.channel.edit(name=f"{member_name}-ticket") #Edit the Ticket Channel Name again
        await interaction.response.send_message(embed=embed)

    @discord.ui.button(label="Delete Ticket 🎫", style = discord.ButtonStyle.red, custom_id="delete")
    async def delete_button(self, button: discord.ui.Button, interaction: discord.Interaction):
        guild = self.bot.get_guild(GUILD_ID)
        channel = self.bot.get_channel(LOG_CHANNEL)
        member_id = interaction.user.id

        cur.execute("DELETE FROM ticket WHERE discord_id=?", (member_id,)) #Delete the Ticket from the Database
        conn.commit()

        #Creating the Transcript
        military_time: bool = True
        transcript = await chat_exporter.export(
            interaction.channel,
            limit=200,
            tz_info=TIMEZONE,
            military_time=military_time,
            bot=self.bot,
        )
        if transcript is None:
            return

        transcript_file = discord.File(
            io.BytesIO(transcript.encode()),
            filename=f"transcript-{interaction.channel.name}.html")
        transcript_file2 = discord.File(
            io.BytesIO(transcript.encode()),
            filename=f"transcript-{interaction.channel.name}.html")

        ticket_creator = guild.get_member(member_id)
        embed = discord.Embed(description=f'Ticket is deleting in 5 seconds.', color=0xd5d7ee)
        transcript_info = discord.Embed(title=f"Ticket Deleting | {interaction.channel.name}", description=f"Ticket from: {ticket_creator.mention}\nTicket Name: {interaction.channel.name} \n Closed from: {interaction.user.mention}", color=0x9b93cc)

        await interaction.response.send_message(embed=embed)
        #checks if user has dms disabled
        try:
            await ticket_creator.send(embed=transcript_info, file=transcript_file)
        except:
            transcript_info.add_field(name="Error", value="Couldn't send the Transcript to the User because he has his DMs disabled!", inline=True)
        await channel.send(embed=transcript_info, file=transcript_file2)
        await asyncio.sleep(3)
        await interaction.channel.delete(reason="Ticket got Deleted!")
