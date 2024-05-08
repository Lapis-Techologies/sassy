import datetime
import discord
from typing import TYPE_CHECKING
from uuid import uuid4
from discord.ext import commands
from discord import app_commands, Interaction


if TYPE_CHECKING:
    from main import Sassy


class RWarn(commands.Cog):
    def __init__(self, bot: 'Sassy'):
        self.bot = bot

    @app_commands.command(name="rwarn", description="Removes a warning from a suer.")
    async def rwarn(self, inter: Interaction, user: discord.Member, case_id: str):
        await inter.response.defer()
        invoker = inter.user

        if not invoker.get_role(self.bot.config['roles']['admin'].id):
            await inter.followup.send("You do not have permission to use this command!", emphemeral=True)
            return

        if user.get_role(self.bot.config['roles']['admin'].id):
            return

        if user == invoker:
            return

        if user.id == self.bot.user.id:
            return

        curs = await self.bot.db.find_one({"uid": user.id}, projection={"logs": 1})

        found = False

        if curs is None:
            await self.bot.db.insert_one({
                "uid": user.id,
                "choomah_coins": 0,
                "logs": [],
            })
        else:
            for log in curs["logs"]:
                if log["case_id"] == case_id:
                    found = True
                    await self.bot.db.update_one({"uid": user.id}, {
                        "$pull": {
                            "logs": {
                                "case_id": case_id
                            }
                        }
                    })
                    break

        if not found:
            await inter.followup.send("Case ID not found!", ephemeral=True)
            return

        await inter.followup.send("Warning removed!", ephemeral=True)


async def setup(bot: 'Sassy'):
    await bot.add_cog(RWarn(bot))
