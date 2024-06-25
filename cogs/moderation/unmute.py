import discord
from typing import TYPE_CHECKING
from discord.ext import commands
from discord import app_commands, Interaction, User
from utils.log import log


if TYPE_CHECKING:
    from main import Sassy


class UnMute(commands.Cog):
    def __init__(self, bot: "Sassy"):
        self.bot = bot

    @app_commands.command(name="unmute", description="Unmute a user.")
    async def unmute(self, inter: Interaction, user: discord.Member):
        await inter.response.defer()

        invoker = inter.user

        if isinstance(invoker, User):
            return

        admin = await self.bot.config.get("roles", "admin")

        if not invoker.get_role(admin):
            await inter.followup.send("You do not have the required role to use this command!")
            return

        if not user.is_timed_out():
            await inter.followup.send("This user is not muted!")
            return

        await user.timeout(0)   # noqa  # 0 will untimeout the user

        await inter.followup.send(f"Unmuted {user}!")

        await log(self.bot, inter, "unmute")


async def setup(bot):
    await bot.add_cog(UnMute(bot))
