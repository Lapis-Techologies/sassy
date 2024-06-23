from typing import TYPE_CHECKING
from discord import app_commands, Interaction
from discord.ext import commands


if TYPE_CHECKING:
    from main import Sassy


class Fail(commands.Cog):
    def __init__(self, bot: "Sassy"):
        self.bot = bot

    @app_commands.command(name="fail", description="A command that always fails on purpose. Raises Exception.")
    @app_commands.checks.cooldown(1, 15, key=lambda i: (i.guild_id, i.user.id))
    async def fail(self, inter: Interaction, *, opt: str):
        raise Exception(f"Failed successfully. opt={opt}")


async def setup(bot: 'Sassy'):
    await bot.add_cog(Fail(bot))
