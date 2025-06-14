from typing import TYPE_CHECKING
from discord import app_commands, Interaction
from discord.ext import commands
from utils.checks import db_check, is_admin


if TYPE_CHECKING:
    from main import Sassy


class Fail(commands.Cog):
    def __init__(self, bot: "Sassy"):
        self.bot = bot

    @app_commands.command(
        name="fail",
        description="A command that always fails on purpose. Raises either Exception, OSError, or TypeError.",
    )
    @app_commands.checks.cooldown(1, 15, key=lambda i: (i.guild_id, i.user.id))
    @db_check()
    @is_admin()
    async def fail(
        self, interaction: Interaction, message: str = "Failed Successfully."
    ):
        admin = interaction.guild.get_role(
            self.bot.config.get("guild", "roles", "admin")
        )

        if admin not in interaction.user.roles:
            await interaction.response.send_message("You do not have permission!")
            return

        await interaction.response.send_message("Send Exception!")
        raise Exception(message)


async def setup(bot: "Sassy"):
    await bot.add_cog(Fail(bot))
