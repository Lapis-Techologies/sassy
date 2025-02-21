from typing import TYPE_CHECKING
from discord import app_commands, Interaction
from discord.ext import commands
from utils.checks import db_check


if TYPE_CHECKING:
    from main import Sassy


class Ping(commands.Cog):
    def __init__(self, bot: "Sassy"):
        self.bot = bot

    @app_commands.command(name="ping", description="Get the latency of the bot.")
    @app_commands.checks.cooldown(1, 15, key=lambda i: (i.guild_id, i.user.id))
    @db_check()
    async def ping(self, inter: Interaction):
        await inter.response.send_message(f"Pong! {round(self.bot.latency * 1000)}ms")


async def setup(bot: 'Sassy'):
    await bot.add_cog(Ping(bot))
