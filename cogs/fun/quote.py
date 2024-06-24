from typing import TYPE_CHECKING
from random import choice
from discord.ext import commands
from discord import app_commands, Interaction


if TYPE_CHECKING:
    from main import Sassy


class Quote(commands.Cog):
    def __init__(self, bot: 'Sassy'):
        self.bot = bot

    @app_commands.command(name="quote", description="You want some advice from me?")
    @app_commands.checks.cooldown(1, 10, key=lambda i: (i.guild_id, i.user.id))
    async def quote(self, inter: Interaction):
        with open("./resources/quote.txt", "r") as f:
            quotes = f.readlines()

        selected_quote = choice(quotes)

        await inter.response.send_message(selected_quote)


async def setup(bot: 'Sassy'):
    await bot.add_cog(Quote(bot))
