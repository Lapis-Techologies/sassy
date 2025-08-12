import datetime
import discord
from typing import TYPE_CHECKING
from uuid import uuid4
from discord.ext import commands
from discord import app_commands, Interaction, User
from utils.adduser import add
from utils.log import LogType, log, Field
from utils.checks import db_check, is_admin


if TYPE_CHECKING:
    from main import Sassy


class Warn(commands.Cog):
    def __init__(self, bot: "Sassy"):
        self.bot = bot
        self.user_db = self.bot.database["user"]

    async def checks(self, interaction, user) -> bool:
        admin = interaction.guild.get_role(self.bot.config.get("guild", "roles", "admin"))
        invoker = interaction.user

        if isinstance(invoker, User):
            return False
        elif admin in user.roles:
            await interaction.followup.send("You cannot warn an admin!", ephemeral=True)
            return False
        elif user == invoker:
            await interaction.followup.send("You cannot warn yourself!", ephemeral=True)
            return False
        elif user.id == self.bot.user.id:
            await interaction.followup.send("hehe you can't warn me mate!", ephemeral=True)
            return False
        return True

    async def add_warning(self, interaction, user, invoker, case_id, reason) -> None:
        curs = await self.user_db.find_one({"uid": user.id}, projection={"logs": 1})

        if curs is None:
            await add(
                bot=self.bot,
                member=user,
                logs=[
                    {
                        "case_id": case_id,
                        "action": LogType.WARN,
                        "reason": reason,
                        "moderator": invoker.id,
                        "timestamp": datetime.datetime.now(datetime.UTC),
                    }
                ],
            )
        else:
            await self.user_db.update_one(
                {"uid": user.id},
                {
                    "$push": {
                        "logs": {
                            "case_id": case_id,
                            "action": LogType.WARN,
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
            LogType.WARN,
            reason,
            [Field("Case ID", f"`{case_id}`", False)],
        )

    @app_commands.command(name="warn", description="Warns a user.")
    @app_commands.describe(
        user="The user to warn.", reason="The reason for the warning."
    )
    @db_check()
    @is_admin()
    async def warn(
        self,
        interaction: Interaction,
        user: discord.Member,
        reason: str = "No reason provided.",
    ):
        await interaction.response.defer()
        invoker = interaction.user

        if not await self.checks(interaction, user):
            return

        case_id = str(uuid4())

        await self.add_warning(interaction, user, invoker, case_id, reason)
        await interaction.followup.send(f"{user.mention} has been warned!", ephemeral=True)


async def setup(bot: "Sassy"):
    await bot.add_cog(Warn(bot))
