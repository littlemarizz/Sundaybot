from typing import Any, Coroutine
import nextcord as discord
from nextcord import Interaction, ui, Role
from nextcord.ui import View, button, Modal, TextInput, Button
import sqlite3

YN_TO_BOOL = {'Y': True, 'N': False}

ga_db_connection = sqlite3.connect('SundayGiveaways.db')
ga_cursor = ga_db_connection.cursor()

class UIDModal(Modal):
    def __init__(self, table: str, role_details: tuple):
        super().__init__(title="Provide the information below")
        self.uid = TextInput(
            label="StarRail UID",
            placeholder="000000000",
            min_length=9, max_length=9,
            style=discord.TextInputStyle.short)
        self.add_item(self.uid)
        self.table = table
        self.role: Role = role_details[0]
        self.role_entries: int = role_details[1]

    async def callback(self, ctx: Interaction):
        # store the UID along with the user's discord ID in the db
        try:
            if self.role in ctx.user.roles:
                ga_cursor.execute(f"INSERT INTO {self.table} (discord_id, hsr_uid, entries) VALUES (?, ?, ?)", (ctx.user.id, self.uid.value, self.role_entries))
            else:
                ga_cursor.execute(f"INSERT INTO {self.table} (discord_id, hsr_uid, entries) VALUES (?, ?, 1)", (ctx.user.id, self.uid.value))
            ga_db_connection.commit()
            await ctx.response.send_message("Joined!", ephemeral=True)
        except sqlite3.IntegrityError:
            return await ctx.response.send_message(f"You have already participated in the giveaway!", ephemeral=True)

class GiveawayView(View):
    def __init__(self, bot = None, uid_required: str = None, special_role: Role = None, special_role_entries: int = None):
        self.bot = bot
        if uid_required:
            self.uid_required = YN_TO_BOOL[uid_required]
        self.special_role = special_role
        self.special_role_entries = special_role_entries
        super().__init__(timeout=None)

    @button(label="Join", style=discord.ButtonStyle.green)
    async def join(self, view: View, ctx: Interaction):
        # first we need to find out if the user has the booster role
        if self.uid_required:
            modal = UIDModal(table=self.table, role_details=(self.special_role, self.special_role_entries))
            await ctx.response.send_modal(modal)
        else:
            try:
                if self.special_role in ctx.user.roles:
                    ga_cursor.execute(f"INSERT INTO {self.table} (discord_id, hsr_uid, entries) VALUES (?, ?, ?)", (ctx.user.id, None, self.special_role_entries))
                else:
                    ga_cursor.execute(f"INSERT INTO {self.table} (discord_id, hsr_uid, entries) VALUES (?, ?, 1)", (ctx.user.id, None))
                ga_db_connection.commit()
                await ctx.response.send_message("Joined!", ephemeral=True)
            except sqlite3.IntegrityError:
                return await ctx.response.send_message("You've already joined this Giveaway!", ephemeral=True)

        ga_cursor.execute(f"SELECT COUNT(*) FROM {self.table}")
        result = ga_cursor.fetchone()
        participants = result[0]

        self.embed.set_footer(text=f"Number of participants: {participants}")
        await self.msg.edit(embed=self.embed)

    def giveaway_table(self, id):
        if id[:2] == "ga":
            self.table = id
        else:
            self.table = f"ga_{id}"

    def giveaway_message(self, embed: discord.Embed, message: discord.Message):
        self.embed = embed
        self.msg = message


# class GiveawayManageView(View):
#     def __init__(self, bot):
#         self.bot = bot
#         super().__init__(timeout=None)
