import discord
import datetime
from typing import TYPE_CHECKING
from uuid import uuid4
from discord.ext import commands
from discord import User, app_commands, Interaction
from utils.log import log, LogType, Field
from utils.checks import db_check, is_admin


if TYPE_CHECKING:
    from main import Sassy


class Ban(commands.Cog):
    def __init__(self, bot: "Sassy"):
        self.bot = bot
        self.user_db = self.bot.database["user"]

    async def add_ban(self, inter, user, reason, invoker) -> None:
        case_id = str(uuid4())

        await self.user_db.update_one(
            {"uid": user.id},
            {
                "$push": {
                    "logs": {
                        "case_id": case_id,
                        "action": LogType.BAN,
                        "reason": reason,
                        "moderator": invoker.id,
                        "timestamp": datetime.datetime.now(datetime.UTC),
                    }
                }
            },
        )

        await log(
            self.bot,
            inter,
            LogType.BAN,
            reason,
            fields=[Field("Case ID", f"`{case_id}", False)],
        )

    async def check(self, inter, invoker, user) -> bool:
        admin = self.bot.config.get("guild", "roles", "admin")
        if isinstance(invoker, User):
            return False
        elif admin in user.roles:
            await inter.followup.send("You cannot ban an admin!", ephemeral=True)
            return False
        elif user == invoker:
            await inter.followup.send("You cannot ban yourself!", ephemeral=True)
            return False
        elif user.id == self.bot.user.id:
            await inter.followup.send("hehe you can't ban me mate!", ephemeral=True)
            return False
        return True

    @app_commands.command(name="ban", description="Ban a user from the server.")
    @app_commands.checks.cooldown(1, 5, key=lambda i: (i.guild_id, i.user.id))
    @db_check()
    @is_admin()
    async def ban(
        self,
        inter: Interaction,
        user: discord.Member,
        reason: str = "No reason provided.",
    ):
        await inter.response.defer()
        invoker = inter.user
        if not await self.check(inter, invoker, user):
            return

        await user.ban(reason=reason)
        await inter.followup.send(
            f"{user.mention} has been banned from the server!", ephemeral=True
        )
        await self.add_ban(inter, user, reason, invoker)


async def setup(bot: "Sassy"):
    await bot.add_cog(Ban(bot))
