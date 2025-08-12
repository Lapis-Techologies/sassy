import discord
from re import compile
from time import time
from typing import TYPE_CHECKING
from discord.ext import commands
from discord import (
    RawReactionActionEvent,
    Message
)


if TYPE_CHECKING:
    from main import Sassy
# TODO: Refactor reaction_poll and reaction_role into one reaction handler,
#  create a command for creating reaction messages.

class ReactionPoll(commands.Cog):
    def __init__(self, bot: "Sassy"):
        self.bot = bot
        self.uuid4_regex = compile(
            r"^[0-9a-f]{8}-[0-9a-f]{4}-4[0-9a-f]{3}-[89ab][0-9a-f]{3}-[0-9a-f]{12}$"
        )
        self.polling_db = self.bot.database["polls"]

    async def handle_poll_reaction(
        self, payload: RawReactionActionEvent, message: Message
    ):
        embed = message.embeds[0]
        footer = embed.footer.text
        parts = footer.split(" | ")
        if len(parts) != 2:
            return
        uuid = parts[1].strip()

        if not self.uuid4_regex.match(uuid):
            return

        poll = await self.polling_db.find_one({"id": uuid})
        if poll is None:
            return

        end_date = int(poll["end_date"])
        finished = poll["finished"]
        current_time = time()
        if (current_time > end_date) or finished:
            return

        emoji_id = payload.emoji.id

        emojis = {
            int(emoji_id): idx
            for idx, (_, emoji_id) in enumerate(
                self.bot.config.get("commands", "poll").items()
            )
        }
        selected_option = emojis.get(emoji_id)

        if selected_option is None or selected_option >= len(poll["votes"]):
            return

        if payload.event_type == "REACTION_REMOVE":
            await self.polling_db.update_one(
                {"id": uuid}, {"$inc": {f"votes.{selected_option}": -1}}
            )
        else:
            await self.polling_db.update_one(
                {"id": uuid}, {"$inc": {f"votes.{selected_option}": 1}}
            )

    async def handle_reaction_event(self, payload: RawReactionActionEvent) -> None:
        guild = self.bot.get_guild(payload.guild_id)
        member = await guild.fetch_member(payload.user_id)

        if member.bot:
            return

        guild_id = payload.guild_id

        if guild_id is None:
            return  # Ignore DMs

        channel = self.bot.get_channel(payload.channel_id)
        message = await channel.fetch_message(payload.message_id)
        if message.embeds:
            await self.handle_poll_reaction(payload, message)
            return

    @commands.Cog.listener()
    async def on_raw_reaction_add(
        self, payload: discord.RawReactionActionEvent
    ) -> None:
        await self.handle_reaction_event(payload)

    @commands.Cog.listener()
    async def on_raw_reaction_remove(
        self, payload: discord.RawReactionActionEvent
    ) -> None:
        await self.handle_reaction_event(payload)


async def setup(bot):
    await bot.add_cog(ReactionPoll(bot))
