import discord
from typing import TYPE_CHECKING
from discord.ext import commands
from discord import app_commands, Interaction
from utils.adduser import add
from utils.log import log


if TYPE_CHECKING:
    from main import Sassy


class UnBan(commands.Cog):
    def __init__(self, bot: 'Sassy'):
        self.bot = bot

    @app_commands.command(name="unban", description="UnBan a user from the server.")
    async def unban(self, inter: Interaction, user: discord.Member, reason: str = "No reason provided."):
        await inter.response.defer()
        invoker = inter.user

        if not invoker.get_role(self.bot.config['roles']['admin'].id):
            await inter.followup.send("You do not have permission to use this command!")
            return

        if user.get_role(self.bot.config['roles']['admin'].id):
            return

        if user == invoker:
            return

        if user.id == self.bot.user.id:
            return

        await self.bot.config["guild"].unban(user, reason=reason)
        await inter.followup.send(f"{user.mention} has been unbanned from the server!", ephemeral=True)

        curs = await self.bot.db.find_one({"uid": user.id}, projection={"logs": 1})

        if curs is None:
            await add(bot=self.bot, member=user)

        await log(self.bot, inter, "unban", reason)


async def setup(bot: 'Sassy'):
    await bot.add_cog(UnBan(bot))
