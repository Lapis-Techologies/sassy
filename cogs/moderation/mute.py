import datetime
import discord
from uuid import uuid4
from typing import TYPE_CHECKING
from discord import app_commands, Interaction
from discord.ext import commands


if TYPE_CHECKING:
    from main import Sassy


class Mute(commands.Cog):
    def __init__(self, bot: "Sassy"):
        self.bot = bot

    @app_commands.command(name="mute", description="Mutes a specified user for a specified amount of time.")
    async def mute(self, inter: Interaction, user: discord.Member, days: int = 0, hours: int = 0, minutes: int = 0, reason: str = "No reason provided."):
        await inter.response.defer()

        invoker = inter.user

        if not invoker.get_role(self.bot.config['roles']['admin'].id):
            await inter.followup.send("You do not have permission to use this command!", ephemeral=True)
            return

        if user.get_role(self.bot.config['roles']['admin'].id):
            await inter.followup.send("You cannot mute an admin!", ephemeral=True)
            return
        elif user == invoker:
            await inter.followup.send("You cannot mute yourself!", ephemeral=True)
            return
        elif user.id == self.bot.user.id:
            await inter.followup.send("hehe you can't mute me mate!", ephemeral=True)
            return

        if user.is_timed_out():
            await inter.followup.send("This user is already muted!", ephemeral=True)
            return

        if days == 0 and hours == 0 and minutes == 0:
            await inter.followup.send("You must specify a time to mute the user for!", ephemeral=True)
            return

        time = (days * 86400) + (hours * 3600) + (minutes * 60)

        await user.timeout(
            datetime.datetime.now(datetime.UTC) + datetime.timedelta(seconds=time),
            reason=reason
        )

        await inter.followup.send(f"{user} has been muted for {days} days, {hours} hours, and {minutes} minutes for `{reason}`.", ephemeral=True)

        case_id = str(uuid4())

        curs = await self.bot.db.find_one({"uid": user.id}, projection={"logs": 1})

        if curs is None:
            await self.bot.db.insert_one({
                "uid": user.id,
                "choomah_coins": 0,
                "logs": [{
                    "case_id": case_id,
                    "action": "mute",
                    "reason": reason,
                    "moderator": invoker.id,
                    "timestamp": datetime.datetime.now(datetime.UTC)
                }]
            })
        else:
            await self.bot.db.update_one({"uid": user.id}, {
                "$push": {
                    "logs": {
                        "case_id": case_id,
                        "action": "mute",
                        "reason": reason,
                        "moderator": invoker.id,
                        "timestamp": datetime.datetime.now(datetime.UTC)
                    }
                }
            })


async def setup(bot: "Sassy"):
    await bot.add_cog(Mute(bot))
