import datetime
import discord
from uuid import uuid4
from typing import TYPE_CHECKING
from discord import app_commands, Interaction, User
from discord.ext import commands
from utils.log import log, LogType, Field
from utils.checks import db_check, is_admin


if TYPE_CHECKING:
    from main import Sassy


class Mute(commands.Cog):
    def __init__(self, bot: "Sassy"):
        self.bot = bot
        self.user_db = self.bot.database["user"]

    async def add_mute(
        self,
        interaction: Interaction,
        user: discord.Member,
        days: int,
        hours: int,
        minutes: int,
        reason: str = "No reason provided.",
    ) -> None:
        case_id = str(uuid4())
        invoker = interaction.user

        await self.user_db.update_one(
            {"uid": user.id},
            {
                "$push": {
                    "logs": {
                        "case_id": case_id,
                        "action": LogType.MUTE,
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
            LogType.MUTE,
            reason,
            [
                Field("Time", f"{days} Days, {hours} Hours, {minutes} Minutes", False),
                Field("Case ID", f"`{case_id}`", False),
            ],
        )

    async def checks(
        self,
        interaction: Interaction,
        user: discord.Member,
        days: int,
        hours: int,
        minutes: int,
    ) -> bool:
        admin = interaction.guild.get_role(self.bot.config.get("guild", "roles", "admin"))
        invoker = interaction.user
        # Discord strangely forces max timeout time to be 28 days ?
        total_time_seconds = (days * 86400) + (hours * 3600) + (minutes * 60)
        if isinstance(invoker, User):
            return False
        elif admin in user.roles:
            await interaction.followup.send("You cannot mute an admin!", ephemeral=True)
            return False
        elif user == invoker:
            await interaction.followup.send("You cannot mute yourself!", ephemeral=True)
            return False
        elif user.id == self.bot.user.id:
            await interaction.followup.send("hehe you can't mute me mate!", ephemeral=True)
            return False
        elif user.is_timed_out():
            await interaction.followup.send("This user is already muted!", ephemeral=True)
            return False
        elif days == 0 and hours == 0 and minutes == 0:
            await interaction.followup.send(
                "You must specify a time to mute the user for!", ephemeral=True
            )
            return False
        elif total_time_seconds > 2419200:  # 28 days in seconds
            await interaction.followup.send("Sorry, maximum mute time is 28 days!")
            return False
        else:
            return True

    @app_commands.command(
        name="mute",
        description="Mutes a specified user for a specified amount of time.",
    )
    @app_commands.describe(
        user="The user to mute.",
        days="How many days should the mute last? Default 0.",
        hours="How many hours should the mute last? Default 0.",
        minutes="How many minutes should the mute last? Default 0.",
        reason='The reason for the mute. Defaults to "No reason provided."',
    )
    @db_check()
    @is_admin()
    async def mute(
        self,
        interaction: Interaction,
        user: discord.Member,
        days: int = 0,
        hours: int = 0,
        minutes: int = 0,
        reason: str = "No reason provided.",
    ) -> None:
        await interaction.response.defer()

        time = (days * 86400) + (hours * 3600) + (minutes * 60)

        if not await self.checks(interaction, user, days, hours, minutes):
            return

        await user.timeout(
            datetime.datetime.now(datetime.UTC) + datetime.timedelta(seconds=time),
            reason=reason,
        )

        await interaction.followup.send(
            f"{user} has been muted for {days} days, {hours} hours, and {minutes} minutes for `{reason}`.",
            ephemeral=True,
        )
        await self.add_mute(interaction, user, days, hours, minutes, reason)


async def setup(bot: "Sassy"):
    await bot.add_cog(Mute(bot))
