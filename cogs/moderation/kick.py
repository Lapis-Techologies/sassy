import datetime
import discord
from typing import TYPE_CHECKING
from uuid import uuid4
from discord.ext import commands
from discord import app_commands, Interaction, User
from utils.adduser import add
from utils.log import log


if TYPE_CHECKING:
    from main import Sassy


class Kick(commands.Cog):
    def __init__(self, bot: 'Sassy'):
        self.bot = bot

    @app_commands.command(name="kick", description="Kick a user from the server.")
    async def kick(self, inter: Interaction, user: discord.Member, reason: str = "No reason provided."):
        await inter.response.defer()
        invoker = inter.user

        if isinstance(invoker, User):
            return

        admin = await self.bot.config.get("roles", "admin")

        if not invoker.get_role(admin):
            await inter.response.send_message("You do not have permission to use this command!")
            return
        elif user.get_role(admin):
            await inter.followup.send("You cannot kick an admin!", ephemeral=True)
            return
        elif user == invoker:
            await inter.followup.send("You cannot kick yourself!", ephemeral=True)
            return
        elif user.id == self.bot.user.id:
            await inter.followup.send("hehe you can't kick me mate!", ephemeral=True)
            return

        await user.kick(reason=reason)
        await inter.followup.send(f"{user.mention} has been kicked from the server!", ephemeral=True)

        case_id = str(uuid4())

        curs = await self.bot.user_db.find_one({"uid": user.id}, projection={"logs": 1})

        if curs is None:
            await add(bot=self.bot, member=user, logs=[
                {
                    "case_id": case_id,
                    "action": "kick",
                    "reason": reason,
                    "moderator": invoker.id,
                    "timestamp": datetime.datetime.now(datetime.UTC)
                }
            ])
        else:
            await self.bot.user_db.update_one({"uid": user.id}, {
                "$push": {
                    "logs": {
                        "case_id": case_id,
                        "action": "kick",
                        "reason": reason,
                        "moderator": invoker.id,
                        "timestamp": datetime.datetime.now(datetime.UTC)
                    }
                }
            })

        await log(self.bot, inter, "kick", reason, [{"name": "Case ID", "value": f"`{case_id}`", "inline": False}])


async def setup(bot: 'Sassy'):
    await bot.add_cog(Kick(bot))
