import random
from discord.ext import commands
from discord import app_commands, Interaction
from typing import TYPE_CHECKING
from utils.checks import db_check


if TYPE_CHECKING:
    from main import Sassy


class Smoke(commands.Cog):
    def __init__(self, bot: "Sassy"):
        self.bot = bot
        self.user_db = self.bot.database["user"]

    @app_commands.command(name="smoke", description="Smoke a quick one with Lez.")
    @app_commands.checks.cooldown(1, 20, key=lambda i: (i.guild_id, i.user.id))
    @db_check()
    async def smoke(self, interaction: Interaction) -> None:
        user = interaction.user
        coins_found = random.randint(0, 5)
        curs = await self.user_db.find_one(
            {"uid": user.id}, projection={"choomah_coins": 1}
        )

        current = curs["choomah_coins"]
        new_bal = current + coins_found
        await self.user_db.update_one(
            {"uid": user.id}, {"$set": {"choomah_coins": new_bal}}
        )

        await interaction.response.send_message(
            f"You go smoking with Lez and the mates and find **{coins_found}** choomah coins! Your new balance is ***{new_bal}***"
        )


async def setup(bot):
    await bot.add_cog(Smoke(bot))
