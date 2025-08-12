import discord
from typing import TYPE_CHECKING
from discord.ext import commands
from discord import (
    RawMemberRemoveEvent,
)
from utils.adduser import add
from utils.log import log, Importancy, LogType, Field


if TYPE_CHECKING:
    from main import Sassy


class Movement(commands.Cog):
    def __init__(self, bot: "Sassy"):
        self.bot = bot

    @commands.Cog.listener()
    async def on_member_join(self, member: discord.Member) -> None:
        welcome_channel = self.bot.get_channel(
            self.bot.config.get("guild", "channels", "welcome")
        )
        rules_channel = self.bot.get_channel(
            self.bot.config.get("guild", "channels", "rules")
        )
        reaction_role_channel = self.bot.get_channel(
            self.bot.config.get("guild", "channels", "reaction_role")
        )

        if welcome_channel is None or not isinstance(
            welcome_channel, discord.TextChannel
        ):
            await add(bot=self.bot, member=member)
            return

        await welcome_channel.send(
            f"{member.mention} Whats goin on mate? You're druggo #{member.guild.member_count}, fuckin skits mate. Check out the {rules_channel.mention} and select your favorite characcter in {reaction_role_channel.mention}!"
        )

        await add(bot=self.bot, member=member)
        await log(
            self.bot,
            None,
            LogType.JOIN,
            fields=[
                Field("User", member.name),
                Field("ID", member.id),
                Field("Mention", member.mention),
            ],
        )

    @commands.Cog.listener()
    async def on_raw_member_remove(self, payload: RawMemberRemoveEvent):
        welcome_channel = self.bot.get_channel(
            self.bot.config.get("guild", "channels", "welcome")
        )

        if welcome_channel is None or not isinstance(
            welcome_channel, discord.TextChannel
        ):
            await log(
                self.bot,
                None,
                LogType.ERROR,
                importancy=Importancy.HIGH,
                fields=[Field("Error", "Failed to get welcome channel!")],
            )

        server = self.bot.get_guild(payload.guild_id)
        await welcome_channel.send(
            f"**{payload.user.name}** left the server, they probably ate a trippa snippa. {server.member_count} druggos left"
        )


async def setup(bot):
    await bot.add_cog(Movement(bot))