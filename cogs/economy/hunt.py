import random
from typing import TYPE_CHECKING
from discord import Member, User, app_commands, Interaction
from discord.ext import commands
from utils.checks import db_check


if TYPE_CHECKING:
    from main import Sassy


class Hunt(commands.Cog):
    def __init__(self, bot: "Sassy"):
        self.bot: "Sassy" = bot
        self.user_db = self.bot.database["user"]

    def roll(self, range: int) -> int:
        return random.randint(-range, range)

    async def update(self, user: User | Member, offset: int) -> tuple[int, int]:
        curs = await self.user_db.find_one(
            {"uid": user.id}, projection={"choomah_coins": 1}
        )

        new_bal = curs["choomah_coins"] + offset
        if new_bal < 0:
            difference = curs["choomah_coins"]
        else:
            difference = offset
        new_bal = new_bal if new_bal >= 0 else 0

        await self.user_db.update_one(
            {"uid": user.id}, {"$set": {"choomah_coins": new_bal}}
        )

        return new_bal, difference

    @app_commands.command(
        name="hunt", description="Go hunting with sassy on choomah island"
    )
    @app_commands.checks.cooldown(1, 30, key=lambda i: (i.guild_id, i.user.id))
    @db_check()
    async def hunt(self, inter: Interaction) -> None:
        await inter.response.defer()

        user = inter.user

        offset = self.roll(15)
        new_bal, diff = await self.update(user, offset)

        if offset >= 0:
            message = (
                f"\\*You go to Choomah Island* You Found __**{diff}**__ Choomah Coins!"
            )
        else:
            message = f"\\*You go to Choomah Island* You Lost __**{abs(diff)}**__ Choomah Coins."

        await inter.followup.send(f"{message}\nYour balance is now **{new_bal}**.")


async def setup(bot):
    await bot.add_cog(Hunt(bot))
