import nextcord as discord
from nextcord import slash_command, Interaction, SlashOption, Client
from nextcord.ext import commands
from nextcord.ext.commands import has_permissions
import sqlite3
from cogs.giveaway_system import GiveawayView

ga_db_connection = sqlite3.connect('SundayGiveaways.db')
ga_cursor = ga_db_connection.cursor()

class Giveaway(commands.Cog):
    def __init__(self, bot):
        self.bot: Client = bot

    @commands.Cog.listener()
    async def on_ready(self):
        print(f'Bot Loaded | giveaway.py ✅')

    @commands.Cog.listener()
    async def on_bot_shutdown(self):
        ga_cursor.close()
        ga_db_connection.close()

    @slash_command(name="giveaway")
    @has_permissions(administrator=True)
    async def setup_giveaway(
        self,
        ctx: Interaction,
        name: str = SlashOption(name="name", description="What's the giveaway about", required=True),
        prize: str = SlashOption(name="prize", description="What's the prize for the Giveaway", required=True),
        time: str = SlashOption(name="time", description="How long will the giveaway be?", required=True),
        uid_requirement: str = SlashOption(name="uid_required", description="Do the users have to enter UID to enter the giveaway? (Y/N)", choices=["Y", "N"], required=True),
        channel_id: int = SlashOption(name="channel_id", description="Channel ID where you want to post the giveaway", required=False)
        ):
        em = discord.Embed(title=f"Giveaway - {name}", description=f"**Prize:** {prize} \nGiveaway ends in __. Click the button below to join!")
        GA_view = GiveawayView(bot=self.bot, uid_required=uid_requirement)
        if channel_id:
            channel = await self.bot.fetch_channel(channel_id)
            ga_msg = await channel.send(embed=em, view=GA_view)
        else:
            ga_msg = await ctx.channel.send(embed=em, view=GA_view)

        giveaway_id = f"giveaway_{ga_msg.id}"
        GA_view.giveaway_table(id=giveaway_id)

        ga_cursor.execute(""f"CREATE TABLE {giveaway_id} (id INTEGER PRIMARY KEY AUTOINCREMENT, discord_id INTEGER, hsr_uid INTEGER, entries INTEGER)""")
        ga_db_connection.commit()

        await ctx.response.send_message(f"Done, Giveaway ID: {giveaway_id}", ephemeral=True)

