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

    async def checks(self, interaction: Interaction, user: discord.Member) -> bool:
        admin = interaction.guild.get_role(self.bot.config.get("guild", "roles", "admin"))
        invoker = interaction.user

        if isinstance(invoker, User):
            return False
        elif admin in user.roles:
            await interaction.followup.send("You cannot unmute an admin!", ephemeral=True)
            return False
        elif user == invoker:
            await interaction.followup.send("You cannot unmute yourself!", ephemeral=True)
            return False
        elif user.id == self.bot.user.id:
            await interaction.followup.send("hehe im not muted mate!", ephemeral=True)
            return False
        elif not user.is_timed_out():
            await interaction.followup.send("This user is not muted!")
            return False
        else:
            return True

    @app_commands.command(name="unmute", description="Unmute a user.")
    @app_commands.describe(
        user="The user to unmute.",
    )
    @db_check()
    @is_admin()
    async def unmute(self, interaction: Interaction, user: discord.Member):
        await interaction.response.defer()

        if not await self.checks(interaction, user):
            return

        await user.timeout(None)

        await interaction.followup.send(f"Unmuted {user}!")

        await log(self.bot, interaction, LogType.UNMUTE)


async def setup(bot):
    await bot.add_cog(UnMute(bot))
