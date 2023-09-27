import nextcord as discord
from nextcord import Interaction, ui
from nextcord.ui import View, button, Modal, TextInput
import sqlite3

YN_TO_BOOL = {'Y': True, 'N': False}

ga_db_connection = sqlite3.connect('SundayGiveaways.db')
ga_cursor = ga_db_connection.cursor()

class UIDModal(Modal):
    def __init__(self, table: str):
        super().__init__(title="Provide the information below")
        self.uid = TextInput(
            label="StarRail UID",
            placeholder="000000000",
            min_length=9, max_length=9,
            style=discord.TextInputStyle.short)
        self.add_item(self.uid)
        self.table = table

    async def callback(self, ctx: Interaction):
        # store the UID along with the user's discord ID in the db
        print(self.table)
        ga_cursor.execute(f"INSERT INTO {self.table} (discord_id, hsr_uid, entries) VALUES (?, ?, 1)", (ctx.user.id, self.uid.value))
        ga_db_connection.commit()
        await ctx.response.send_message(f"**User's UID:** {self.uid.value}")

class GiveawayView(View):
    def __init__(self, bot = None, uid_required: str = None):
        self.bot = bot
        if uid_required:
            self.uid_required = YN_TO_BOOL[uid_required]
        super().__init__(timeout=None)

    @button(label="Join", style=discord.ButtonStyle.blurple)
    async def join(self, view: View, ctx: Interaction):
        if self.uid_required:
            modal = UIDModal(table=self.table)
            await ctx.response.send_modal(modal)
        else:
            await ctx.response.send_message("Joined")

    def giveaway_table(self, id):
        self.table = id

