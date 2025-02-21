import discord
from typing import TYPE_CHECKING
from discord.ext import commands
from discord import app_commands, Interaction, User
from utils.log import log, LogType
from utils.checks import db_check, is_admin


if TYPE_CHECKING:
    from main import Sassy


class UnMute(commands.Cog):
    def __init__(self, bot: "Sassy"):
        self.bot = bot

    async def checks(self, inter: Interaction, user: discord.Member) -> bool:
        admin = inter.guild.get_role(self.bot.config.get("guild", "roles", "admin"))
        invoker = inter.user

        if isinstance(invoker, User):
            return False
        elif admin in user.roles:
            await inter.followup.send("You cannot unmute an admin!", ephemeral=True)
            return False
        elif user == invoker:
            await inter.followup.send("You cannot unmute yourself!", ephemeral=True)
            return False
        elif user.id == self.bot.user.id:
            await inter.followup.send("hehe im not muted mate!", ephemeral=True)
            return False
        elif not user.is_timed_out():
            await inter.followup.send("This user is not muted!")
            return False
        else:
            return True

    @app_commands.command(name="unmute", description="Unmute a user.")
    @db_check()
    @is_admin()
    async def unmute(self, inter: Interaction, user: discord.Member):
        await inter.response.defer()

        if not await self.checks(inter, user):
            return

        await user.timeout(None)

        await inter.followup.send(f"Unmuted {user}!")

        await log(self.bot, inter, LogType.UNMUTE)


async def setup(bot):
    await bot.add_cog(UnMute(bot))
