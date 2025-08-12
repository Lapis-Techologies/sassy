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
        self.user_db = self.bot.database["user"]

    async def checks(self, interaction, user, invoker) -> bool:
        admin = self.bot.config.get("guild", "roles", "admin")

        if admin in user.roles:
            await interaction.follwup.send("You cannot remove warnings from admins!")
            return False
        elif user == invoker:
            await interaction.followup.send("You cannot remove warnings from yourself!")
            return False
        elif user.id == self.bot.user.id:
            await interaction.followup.send("hehe no")
            return False
        return True

    @app_commands.command(name="rwarn", description="Removes a warning from a user.")
    @app_commands.describe(
        user="The user to remove the warning from.", case_id="The warning case id."
    )
    @db_check()
    @is_admin()
    async def rwarn(self, interaction: Interaction, user: discord.Member, case_id: str):
        await interaction.response.defer()
        invoker = interaction.user

        if not await self.checks(interaction, user, invoker):
            return
        elif isinstance(invoker, User):
            return

        curs = await self.user_db.find_one({"uid": user.id}, projection={"logs": 1})

        if curs is None:
            await add(bot=self.bot, member=user)
            await interaction.followup.send("Case ID not found!", ephemeral=True)
        else:
            await self.user_db.update_one(
                {"uid": user.id}, {"$pull": {"logs": {"case_id": case_id}}}
            )
            await interaction.followup.send("Removed Warning!")

        await log(
            self.bot,
            interaction,
            LogType.REMOVE_WARN,
            fields=[Field("Case ID", f"`{case_id}`", False)],
        )


async def setup(bot: "Sassy"):
    await bot.add_cog(RWarn(bot))
