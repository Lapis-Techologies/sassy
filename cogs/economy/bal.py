from typing import TYPE_CHECKING
from discord import app_commands, Interaction
from discord.ext import commands
from utils.checks import db_check


if TYPE_CHECKING:
    from main import Sassy


class Bal(commands.Cog):
    def __init__(self, bot: "Sassy"):
        self.bot = bot
        self.user_database = self.bot.database["user"]

    @app_commands.command(name="bal", description="Check yer balance m8")
    @app_commands.checks.cooldown(1, 15, key=lambda i: (i.guild_id, i.user.id))
    @db_check()
    async def bal(self, inter: Interaction) -> None:
        """
        Check your balance
        """
        user = inter.user

        curs = await self.user_database.find_one(
            {"uid": user.id}, projection={"choomah_coins": 1}
        )

        await inter.response.send_message(
            f"You have **{curs['choomah_coins']}** choomah coins!"
        )


async def setup(bot):
    await bot.add_cog(Bal(bot))
