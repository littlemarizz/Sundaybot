import nextcord as discord
from nextcord import slash_command, Interaction, SlashOption, Client, Message
from nextcord.ext import commands, tasks
from nextcord.ext.commands import has_permissions
import sqlite3
import time
from random import SystemRandom
from cogs.giveaway_system import GiveawayView

ga_db_connection = sqlite3.connect('SundayGiveaways.db')
ga_cursor = ga_db_connection.cursor()

class Giveaway(commands.Cog):
    def __init__(self, bot):
        self.bot: Client = bot

    @commands.Cog.listener()
    async def on_ready(self):
        ga_cursor.execute("""CREATE TABLE IF NOT EXISTS giveaways (giveaway_id INTEGER, giveaway_name CHAR, prize TEXT, winners INTEGER, guild_id INTEGER, channel_id INTEGER, end_time INTEGER, ended INTEGER, uid_required TEXT, special_role_id INTEGER, special_role_entries INTEGER);""")

        ga_cursor.execute("""SELECT giveaway_id, winners, guild_id, channel_id, end_time FROM giveaways WHERE ended = 0""")
        self.active_giveaways = ga_cursor.fetchall()

        self.giveaway_task.start()
        print(f'Bot Loaded | giveaway.py ✅')

    @commands.Cog.listener()
    async def on_bot_shutdown(self):
        ga_cursor.close()
        ga_db_connection.close()

    @slash_command(name="giveaway", description="Create a giveaway.")
    @has_permissions(administrator=True)
    async def setup_giveaway(
        self,
        ctx: Interaction,
        name: str = SlashOption(name="name", description="What's the giveaway about", required=True),
        prize: str = SlashOption(name="prize", description="What's the prize for the Giveaway", required=True),
        input_time: str = SlashOption(name="time", description="How long will the giveaway be? (Eg: 30s, 10m, 2h, 7d)", required=True),
        winners: int = SlashOption(name="num_of_winners", description="How many users are gonna win the giveaway?", required=True),
        uid_requirement: str = SlashOption(name="uid_required", description="Do the users have to enter UID to enter the giveaway? (Y/N)", choices=["Y", "N"], required=True),
        channel_id: str = SlashOption(name="channel_id", description="Channel ID where you want to post the giveaway", required=False),
        special_role: str = SlashOption(name="special_role_id", description="If there is a role that would get extra entries for the giveaway", required=False),
        special_role_entries: int = SlashOption(name="special_role_entries", description="Number of entries that the users' with the role would get", required=False)
        ):
        if (not special_role and special_role_entries) or (special_role and not special_role_entries):
            return await ctx.response.send_message("Please enter both `special_role_id` and `special_role_entries`!", ephemeral=True)
        elif special_role:
            try:
                role = discord.utils.find(lambda r: r.id == int(special_role), ctx.channel.guild.roles)
            except (ValueError, TypeError):
                return await ctx.response.send_message("Please enter a valid `role`", ephemeral=True)

            if not role:
                return await ctx.response.send_message("Role not found! Please enter a valid `special_role_id`", ephemeral=True)
            else:
                GA_view = GiveawayView(bot=self.bot, uid_required=uid_requirement, special_role=role, special_role_entries=special_role_entries)
        else:
            GA_view = GiveawayView(bot=self.bot, uid_required=uid_requirement)

        timez = {"s": 1, "m": 60, "h": 3600, "d": 86400}
        try:
            time_in_seconds = int(input_time[:-1]) * timez[input_time[-1].lower()]
        except (KeyError, ValueError, TypeError):
            return await ctx.response.send_message("Please enter the `time` in the correct format. Eg: 10s / 20m / 3h / 3d ", ephemeral=True)

        ga_end_time = int(time_in_seconds + time.time())
        giveaway_embed = discord.Embed(title=f"{name.capitalize()} :tada:", description=f"✧ **Prize:** {prize} \n✧ **Number of Winners:** {winners} \n✧ **Giveaway ends:** <t:{ga_end_time}:R> \nClick the button below to join!")
        giveaway_embed.color = 0x81d182
        giveaway_embed.set_author(name=f"Giveaway hosted by {ctx.user.name}", icon_url=ctx.user.avatar.url)
        giveaway_embed.set_footer(text="Number of participants: 0")

        if channel_id:
            try:
                channel = discord.utils.find(lambda c: c.id == int(channel_id), ctx.guild.channels)
            except (ValueError, TypeError):
                return await ctx.response.send_message("Please enter a valid `channel_id`", ephemeral=True)

            if not channel:
                return await ctx.response.send_message("Channel not found! Please enter a valid `channel_id`", ephemeral=True)
            else:
                channelID = channel.id
                ga_msg = await channel.send(embed=giveaway_embed, view=GA_view)
        else:
            channelID = ctx.channel.id
            ga_msg: Message = await ctx.channel.send(embed=giveaway_embed, view=GA_view)

        giveaway_id = f"{ga_msg.id}"
        GA_view.giveaway_table(id=giveaway_id)
        GA_view.giveaway_message(embed=giveaway_embed, message=ga_msg)

        if special_role:
            ga_cursor.execute("INSERT INTO giveaways VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)", (giveaway_id, name, prize, winners, ctx.guild.id, channelID, ga_end_time, 0, uid_requirement, special_role, special_role_entries))
        else:
            ga_cursor.execute("INSERT INTO giveaways VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)", (giveaway_id, name, prize, winners, ctx.guild.id, channelID, ga_end_time, 0, uid_requirement, None, None))

        ga_cursor.execute(""f"CREATE TABLE ga_{giveaway_id} (id INTEGER PRIMARY KEY AUTOINCREMENT, discord_id INTEGER UNIQUE, hsr_uid INTEGER UNIQUE, entries INTEGER)""")
        ga_db_connection.commit()

        self.active_giveaways.append((giveaway_id, winners, ctx.guild.id, channelID, ga_end_time))

        await ctx.response.send_message(f"Done! Giveaway ID: {giveaway_id}", ephemeral=True)


    # @slash_command(name="manage_giveaway", description="Use this to manage an already existing giveaway.")
    # @has_permissions(administrator=True)
    # async def manage_giveaway(self, ctx: Interaction, id: str = SlashOption(
    #     name="id", description="The giveaway ID / message ID of the active giveaway.", required=True
    # )):
    #     # NEED TO WORK ON THIS
    #     giveaway_id = f"ga_{id}"
    #     giveaway_id = int(id)
    #     GA_manage_view = GiveawayManageView(self.bot)
    #     return

    @slash_command(name="update_giveaway", description="Use this to update an already existing giveaway.")
    @has_permissions(administrator=True)
    async def update_giveaway(self, ctx: Interaction, id: str = SlashOption(
        name="id", description="The giveaway ID / message ID of the active giveaway.", required=True
    )):
        try:
            ga_cursor.execute("SELECT channel_id, uid_required, special_role_id, special_role_entries FROM giveaways WHERE giveaway_id = ?", (id,))
            giveaway = ga_cursor.fetchone()
            channel_id, uid_required, special_role_id, special_role_entries = giveaway[0], giveaway[1], giveaway[2], giveaway[3]

            channel = await self.bot.fetch_channel(channel_id)
            message = await channel.fetch_message(id)

            updated_GA_view = GiveawayView(bot=self.bot, uid_required=uid_required, special_role=special_role_id, special_role_entries=special_role_entries)
            updated_GA_view.giveaway_table(id)
            updated_GA_view.giveaway_message(embed=message.embeds[0], message=message)

            await message.edit(view=updated_GA_view)

            await ctx.response.send_message("Updated the giveaway!", ephemeral=True)
        except:
            await ctx.response.send_message("An error occured! Please make sure you're entering the correct giveaway message ID.", ephemeral=True)


    @tasks.loop(seconds=2)
    async def giveaway_task(self):
        for giveaway in self.active_giveaways:
            giveaway_id, num_of_winners, guild_id, channel_id, end_time = giveaway[0], giveaway[1], giveaway[2], giveaway[3], giveaway[4]
            if time.time() >= end_time:
                # Ended
                winner_user_ids = self._get_winners(table=f"ga_{giveaway_id}", num_of_winners=num_of_winners)
                guild = await self.bot.fetch_guild(guild_id)
                winners = [await guild.fetch_member(winner) for winner in winner_user_ids]

                ga_cursor.execute("""UPDATE giveaways SET ended = 1 WHERE giveaway_id = ?""", (giveaway_id,))
                ga_db_connection.commit()

                if len(winners) > 1:
                    giveaway_ended = discord.Embed(title="Giveaway Ended :tada:", description=f"The winners are {', '.join([user.mention for user in winners])} !!!", color=0x81d182)
                else:
                    giveaway_ended = discord.Embed(title="Giveaway Ended :tada:", description=f"The winner is {', '.join([user.mention for user in winners])} !!!", color=0x81d182)

                self.active_giveaways.remove(giveaway)

                channel = await self.bot.fetch_channel(channel_id)
                giveaway_message = await channel.fetch_message(giveaway_id)
                await giveaway_message.edit(embed=giveaway_ended, view=None)

    def _get_winners(self, table: str, num_of_winners: int) -> list:
        random = SystemRandom()

        ga_cursor.execute(""f"SELECT discord_id, hsr_uid, entries FROM {table}""")
        results = ga_cursor.fetchall()

        user_pool, winners = [], []

        for result in results:
            user, entries = result[0], result[2]
            for _ in range(entries):
                user_pool.append(user)

        num = 0
        if user_pool:
            for user in user_pool:
                winners.append(random.choice(user_pool))
                user_pool.remove(user)
                num += 1
                if num == num_of_winners:
                    break

        return winners


