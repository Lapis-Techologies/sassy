import datetime
import discord
from typing import TYPE_CHECKING
from uuid import uuid4
from discord.ext import commands
from discord import app_commands, Interaction
from utils.adduser import add
from utils.log import log


if TYPE_CHECKING:
    from main import Sassy


class Warn(commands.Cog):
    def __init__(self, bot: 'Sassy'):
        self.bot = bot

    @app_commands.command(name="warn", description="Warns a user.")
    async def warn(self, inter: Interaction, user: discord.Member, reason: str = "No reason provided."):
        await inter.response.defer()
        invoker = inter.user

        if not invoker.get_role(self.bot.config['roles']['admin'].id):
            await inter.followup.send("You do not have permission to use this command!", emphemeral=True)
            return

        if user.get_role(self.bot.config['roles']['admin'].id):
            await inter.followup.send("You cannot warn an admin!", ephemeral=True)
            return

        if user == invoker:
            await inter.followup.send("You cannot warn yourself!", ephemeral=True)
            return

        if user.id == self.bot.user.id:
            await inter.followup.send("hehe you can't warn me mate!", ephemeral=True)
            return

        case_id = str(uuid4())

        curs = await self.bot.user_db.find_one({"uid": user.id}, projection={"logs": 1})

        if curs is None:
            await add(
                bot=self.bot,
                member=user,
                logs=[
                    {
                        "case_id": case_id,
                        "action": "warn",
                        "reason": reason,
                        "moderator": invoker.id,
                        "timestamp": datetime.datetime.now(datetime.UTC)
                    }
                ]

            )
        else:
            await self.bot.user_db.update_one({"uid": user.id}, {
                "$push": {
                    "logs": {
                        "case_id": case_id,
                        "action": "warn",
                        "reason": reason,
                        "moderator": invoker.id,
                        "timestamp": datetime.datetime.now(datetime.UTC)
                    }
                }
            })

        await inter.followup.send(f"{user.mention} has been warned!", ephemeral=True)

        await log(self.bot, inter, "warn", reason=reason, fields=[{"name": "Case ID", "value": f"`{case_id}`", "inline": False}])


async def setup(bot: 'Sassy'):
    await bot.add_cog(Warn(bot))
