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
        self.user_db = self.bot.database["user"]

    async def checks(self, interaction, user) -> bool:
        invoker = interaction.user

        if not isinstance(user, User):
            await interaction.followup.send("You cannot ban a member that isnt banned!")
            return False
        elif user == invoker:
            await interaction.followup.send("You cant use this if youre banned!")
            return False
        elif user.id == self.bot.user.id:
            await interaction.followup.send("Im not banned!")
            return False
        return True

    @app_commands.command(name="unban", description="Unban a user from the server.")
    @app_commands.describe(
        user="The user to unban.", reason="The reason for unbanning them."
    )
    @db_check()
    @is_admin()
    async def unban(
        self,
        interaction: Interaction,
        user: discord.User,
        reason: str = "No reason provided.",
    ):
        await interaction.response.defer()

        if not await self.checks(interaction, user):
            return

        guild = self.bot.config.get("guild", "id")
        guild = self.bot.get_guild(guild)

        if guild is None:
            raise commands.GuildNotFound(
                f"Failed to find guild with id {self.bot.config.get('guild', 'id')}"
            )

        await guild.unban(user, reason=reason)
        await interaction.followup.send(
            f"{user.mention} has been unbanned from the server!", ephemeral=True
        )

        curs = await self.user_db.find_one({"uid": user.id}, projection={"logs": 1})

        if curs is None:
            await add(bot=self.bot, member=user)

        await log(self.bot, interaction, LogType.UNBAN, reason)


async def setup(bot: "Sassy"):
    await bot.add_cog(UnBan(bot))
