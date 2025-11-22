import datetime
from typing import TYPE_CHECKING
from uuid import uuid4
from discord.ext import commands
from discord import Member, User, app_commands, Interaction
from utils.log import log, LogType, Field
from utils.checks import db_check, is_admin


if TYPE_CHECKING:
    from main import Sassy


class Purge(commands.Cog):
    def __init__(self, bot: "Sassy"):
        self.bot = bot
        self.user_db = self.bot.database["user"]

    async def add_purge(
        self, interaction: Interaction, reason: str, invoker: Member
    ) -> None:
        case_id = str(uuid4())

        await self.user_db.update_one(
            {"uid": invoker.id},
            {
                "$push": {
                    "logs": {
                        "case_id": case_id,
                        "action": LogType.PURGE,
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
            LogType.PURGE,
            reason,
            fields=[Field("Case ID", f"`{case_id}", False)],
        )

    @app_commands.command(name="purge", description="Delete mass amounts of messages.")
    @app_commands.checks.cooldown(1, 10, key=lambda i: (i.guild_id, i.user.id))
    @app_commands.describe(
        amount="The user to ban.",
        reason='The reason for the ban. Defaults to "No reason provided."',
    )
    @db_check()
    @is_admin()
    async def purge(
        self, interaction: Interaction, amount: int, reason: str = "No reason provided."
    ):
        await interaction.response.defer()
        invoker = interaction.user
        if isinstance(invoker, User):
            return

        await interaction.channel.purge(limit=amount or 100 if amount < 100 else amount)
        await interaction.channel.send(
            f"**{amount}** Messages have been purged", delete_after=5
        )
        await self.add_purge(interaction, reason, invoker)


async def setup(bot: "Sassy"):
    await bot.add_cog(Purge(bot))
