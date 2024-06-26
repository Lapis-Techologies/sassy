from typing import TYPE_CHECKING
from discord import app_commands, Interaction
from discord.ext import commands
from utils.adduser import add


if TYPE_CHECKING:
    from main import Sassy


class Bal(commands.Cog):
    def __init__(self, bot: 'Sassy'):
        self.bot: 'Sassy' = bot

    @app_commands.command(name="bal", description="Check you balance")
    @app_commands.checks.cooldown(1, 15, key=lambda i: (i.guild_id, i.user.id))
    async def bal(self, inter: Interaction):
        user = inter.user

        curs = await self.bot.user_db.find_one({"uid": user.id}, projection={"choomah_coins": 1})

        if curs is None:
            await add(bot=self.bot, member=user)
            message = "You have **0** choomah coins!"
        else:
            balance = curs["choomah_coins"]
            message = f"You have **{balance}** choomah coins!"

        await inter.response.send_message(message)


async def setup(bot):
    await bot.add_cog(Bal(bot))
