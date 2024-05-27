import discord
import datetime
from typing import TYPE_CHECKING
from uuid import uuid4
from discord.ext import commands
from discord import app_commands, Interaction
from utils.IGNORE_adduser import add


if TYPE_CHECKING:
    from main import Sassy


class Ban(commands.Cog):
    def __init__(self, bot: 'Sassy'):
        self.bot = bot

    @app_commands.command(name="ban", description="Ban a user from the server.")
    async def ban(self, inter: Interaction, user: discord.Member, reason: str = "No reason provided."):
        await inter.response.defer()
        invoker = inter.user

        if not invoker.get_role(self.bot.config['roles']['admin'].id):
            await inter.followup.send("You do not have permission to use this command!")
            return
        elif user.get_role(self.bot.config['roles']['admin'].id):
            await inter.followup.send("You cannot ban an admin!", ephemeral=True)
            return
        elif user == invoker:
            await inter.followup.send("You cannot ban yourself!", ephemeral=True)
            return
        elif user.id == self.bot.user.id:
            await inter.followup.send("hehe you can't ban me mate!", ephemeral=True)
            return

        await user.ban(reason=reason)
        await inter.followup.send(f"{user.mention} has been banned from the server!", ephemeral=True)

        case_id = str(uuid4())

        curs = await self.bot.db.find_one({"uid": user.id}, projection={"logs": 1})

        if curs is None:
            await add(bot=self.bot, member=user, xp=0, level=0, choomah_coins=0, logs=[
                {
                    "case_id": case_id,
                    "action": "ban",
                    "reason": reason,
                    "moderator": invoker.id,
                    "timestamp": datetime.datetime.now(datetime.UTC)
                }
            ])
        else:
            await self.bot.db.update_one({"uid": user.id}, {
                "$push": {
                    "logs": {
                        "case_id": case_id,
                        "action": "ban",
                        "reason": reason,
                        "moderator": invoker.id,
                        "timestamp": datetime.datetime.now(datetime.UTC)
                    }
                }
            })


async def setup(bot: 'Sassy'):
    await bot.add_cog(Ban(bot))
