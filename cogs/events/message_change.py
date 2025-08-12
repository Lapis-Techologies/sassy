import discord
from typing import TYPE_CHECKING
from discord.ext import commands
from discord import RawMessageUpdateEvent
from utils.log import log, LogType, Field


if TYPE_CHECKING:
    from main import Sassy


class Messages(commands.Cog):
    def __init__(self, bot: "Sassy"):
        self.bot = bot

    @commands.Cog.listener()
    async def on_raw_message_edit(self, payload: RawMessageUpdateEvent) -> None:
        before = payload.cached_message
        after = payload.message
        if before is None:
            before = "UNABLE TO CACHE MESSAGE"
        if after.author.bot:
            return
        # Ignore discord content servers
        elif before.content == after.content:
            return

        await log(
            self.bot,
            None,
            LogType.MESSAGE_EDIT,
            fields=[
                Field("User", f"{after.author.mention}", False),
                Field(
                    "Before",
                    f"```{before.content}```" if before.content else "_ _",  # Nothing
                    False,
                ),
                Field("After", f"```{after.content}```", False),
                Field("Jump Link", after.jump_url, False),
            ],
        )

    @commands.Cog.listener()
    async def on_raw_message_delete(
        self, payload: discord.RawMessageDeleteEvent
    ) -> None:
        if payload.cached_message.author.bot:
            return
        elif isinstance(
            payload.cached_message.channel, (discord.DMChannel, discord.GroupChannel)
        ):
            return

        await log(
            self.bot,
            None,
            LogType.MESSAGE_DELETE,
            fields=[
                Field(
                    "User",
                    f"{payload.cached_message.author.mention} (`{payload.cached_message.author.id}`)",
                    False,
                ),
                Field(
                    "Content",
                    f"```{payload.cached_message.content}```"
                    if payload.cached_message.content
                    else "!!No Content.!!",
                    False,
                ),
                Field("Channel", payload.cached_message.channel.jump_url, False),
            ],
        )


async def setup(bot):
    await bot.add_cog(Messages(bot))
