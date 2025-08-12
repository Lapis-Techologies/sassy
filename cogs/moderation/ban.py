import discord
import datetime
from typing import TYPE_CHECKING
from uuid import uuid4
from discord.ext import commands
from discord import Member, User, app_commands, Interaction
from utils.log import log, LogType, Field
from utils.checks import db_check, is_admin


if TYPE_CHECKING:
    from main import Sassy


class Ban(commands.Cog):
    def __init__(self, bot: "Sassy"):
        self.bot = bot
        self.user_db = self.bot.database["user"]

    async def add_ban(self, interaction: Interaction, user: Member, reason: str,
                      invoker: Member) -> None:
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
            interaction,
            LogType.BAN,
            reason,
            fields=[Field("Case ID", f"`{case_id}", False)],
        )

    async def check(self, interaction: Interaction, invoker: Member, user: Member) \
            -> bool:
        admin = self.bot.config.get("guild", "roles", "admin")
        if isinstance(invoker, User):
            return False
        elif admin in user.roles:
            await interaction.followup.send("You cannot ban an admin!", ephemeral=True)
            return False
        elif user == invoker:
            await interaction.followup.send("You cannot ban yourself!", ephemeral=True)
            return False
        elif user.id == self.bot.user.id:
            await interaction.followup.send("hehe you can't ban me mate!", ephemeral=True)
            return False
        return True

    @app_commands.command(name="ban", description="Ban a user from the server.")
    @app_commands.checks.cooldown(1, 5, key=lambda i: (i.guild_id, i.user.id))
    @app_commands.describe(
        user="The user to ban.",
        reason='The reason for the ban. Defaults to "No reason provided."',
    )
    @db_check()
    @is_admin()
    async def ban(
        self,
        interaction: Interaction,
        user: Member,
        reason: str = "No reason provided.",
    ):
        await interaction.response.defer()
        invoker = interaction.user
        if not await self.check(interaction, invoker, user):
            return

        await user.ban(reason=reason)
        await interaction.followup.send(
            f"{user.mention} has been banned from the server!", ephemeral=True
        )
        await self.add_ban(interaction, user, reason, invoker)


async def setup(bot: "Sassy"):
    await bot.add_cog(Ban(bot))
