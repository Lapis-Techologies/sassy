import datetime
import discord
from typing import TYPE_CHECKING
from uuid import uuid4
from discord.ext import commands
from discord import app_commands, Interaction, User
from utils.log import log, LogType, Field
from utils.checks import db_check, is_admin


if TYPE_CHECKING:
    from main import Sassy


class Kick(commands.Cog):
    def __init__(self, bot: 'Sassy'):
        self.bot = bot

    async def add_kick(self, inter, invoker, user, reason) -> None:
        case_id = str(uuid4())
        await self.bot.user_db.update_one({"uid": user.id}, {
            "$push": {
                "logs": {
                    "case_id": case_id,
                    "action": LogType.KICK,
                    "reason": reason,
                    "moderator": invoker.id,
                    "timestamp": datetime.datetime.now(datetime.UTC)
                }
            }
        })

        await log(self.bot, inter, LogType.KICK, reason, [Field("Case ID", f"`{case_id}`", False)])

    async def check(self, interaction, invoker, user) -> bool:
        admin = self.bot.config.get("guild", "roles", "admin")
        if admin in user.roles:
            await interaction.followup.send("You cannot kick an admin!", ephemeral=True)
            return False
        elif user == invoker:
            await interaction.followup.send("You cannot kick yourself!", ephemeral=True)
            return False
        elif user.id == self.bot.user.id:
            await interaction.followup.send("hehe you can't kick me mate!", ephemeral=True)
            return False
        return True

    @app_commands.command(name="kick", description="Kick a user from the server.")
    @db_check()
    @is_admin()
    async def kick(self, inter: Interaction, user: discord.Member, reason: str = "No reason provided."):
        await inter.response.defer()
        invoker = inter.user

        if not await self.check(inter, invoker, user):
            return
        elif isinstance(invoker, User):
            return

        await user.kick(reason=reason)
        await inter.followup.send(f"hehe, got em. (banned {user.mention})", ephemeral=True)
        await self.add_kick(inter, invoker, user, reason)


async def setup(bot: 'Sassy'):
    await bot.add_cog(Kick(bot))
