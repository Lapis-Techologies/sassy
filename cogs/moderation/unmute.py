import discord
from typing import TYPE_CHECKING
from discord.ext import commands
from discord import app_commands, Interaction


if TYPE_CHECKING:
    from main import Sassy


class UnMute(commands.Cog):
    def __init__(self, bot: "Sassy"):
        self.bot = bot

    @app_commands.command(name="unmute", description="Unmute a user.")
    async def unmute(self, inter: Interaction, user: discord.Member):
        await inter.response.defer()

        invoker = inter.user

        if not invoker.get_role(self.bot.config["roles"]["admin"].id):
            await inter.followup.send("You do not have the required role to use this command!")
            return

        if not user.is_timed_out():
            await inter.followup.send("This user is not muted!")
            return

        await user.timeout(0)

        await inter.followup.send(f"Unmuted {user}!")


async def setup(bot):
    await bot.add_cog(UnMute(bot))
