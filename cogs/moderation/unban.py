import discord
from typing import TYPE_CHECKING
from discord.ext import commands
from discord import app_commands, Interaction, User
from utils.adduser import add
from utils.log import LogType, log
from utils.checks import db_check, is_admin


if TYPE_CHECKING:
    from main import Sassy


class UnBan(commands.Cog):
    def __init__(self, bot: "Sassy"):
        self.bot = bot

    async def checks(self, inter, user) -> bool:
        invoker = inter.user

        if not isinstance(user, User):
            await inter.followup.send("You cannot ban a member that isnt banned!")
            return False
        elif user == invoker:
            await inter.followup.send("You cant use this if youre banned!")
            return False
        elif user.id == self.bot.user.id:
            await inter.followup.send("Im not banned!")
            return False
        return True

    @app_commands.command(name="unban", description="Unban a user from the server.")
    @db_check()
    @is_admin()
    async def unban(
        self,
        inter: Interaction,
        user: discord.User,
        reason: str = "No reason provided.",
    ):
        await inter.response.defer()

        if not await self.checks(inter, user):
            return

        guild = self.bot.config.get("guild", "id")
        guild = self.bot.get_guild(guild)

        if guild is None:
            raise commands.GuildNotFound(
                f"Failed to find guild with id {self.bot.config.get('guild', 'id')}"
            )

        await guild.unban(user, reason=reason)
        await inter.followup.send(
            f"{user.mention} has been unbanned from the server!", ephemeral=True
        )

        curs = await self.bot.user_db.find_one({"uid": user.id}, projection={"logs": 1})

        if curs is None:
            await add(bot=self.bot, member=user)

        await log(self.bot, inter, LogType.UNBAN, reason)


async def setup(bot: "Sassy"):
    await bot.add_cog(UnBan(bot))
