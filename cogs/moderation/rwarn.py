import discord
from typing import TYPE_CHECKING
from discord.ext import commands
from discord import app_commands, Interaction, User
from utils.adduser import add
from utils.log import LogType, log, Field
from utils.checks import db_check, is_admin


if TYPE_CHECKING:
    from main import Sassy


class RWarn(commands.Cog):
    def __init__(self, bot: "Sassy"):
        self.bot = bot

    async def checks(self, inter, user, invoker) -> bool:
        admin = self.bot.config.get("guild", "roles", "admin")

        if admin in user.roles:
            await inter.follwup.send("You cannot remove warnings from admins!")
            return False
        elif user == invoker:
            await inter.followup.send("You cannot remove warnings from yourself!")
            return False
        elif user.id == self.bot.user.id:
            await inter.followup.send("hehe no")
            return False
        return True

    @app_commands.command(name="rwarn", description="Removes a warning from a user.")
    @db_check()
    @is_admin()
    async def rwarn(self, inter: Interaction, user: discord.Member, case_id: str):
        await inter.response.defer()
        invoker = inter.user

        if not await self.checks(inter, user, invoker):
            return
        elif isinstance(invoker, User):
            return

        curs = await self.bot.user_db.find_one({"uid": user.id}, projection={"logs": 1})

        if curs is None:
            await add(bot=self.bot, member=user)
            await inter.followup.send("Case ID not found!", ephemeral=True)
        else:
            await self.bot.user_db.update_one(
                {"uid": user.id}, {"$pull": {"logs": {"case_id": case_id}}}
            )
            await inter.followup.send("Removed Warning!")

        await log(
            self.bot,
            inter,
            LogType.REMOVE_WARN,
            fields=[Field("Case ID", f"`{case_id}`", False)],
        )


async def setup(bot: "Sassy"):
    await bot.add_cog(RWarn(bot))
