import discord
from typing import TYPE_CHECKING
from discord.ext import commands
from discord import app_commands, Interaction
from utils.adduser import add as addd
from utils.log import log


if TYPE_CHECKING:
    from main import Sassy


class Add(commands.Cog):
    def __init__(self, bot: 'Sassy'):
        self.bot = bot

    @app_commands.command(name="add", description="Adds a user to the database.")
    async def add(self, inter: Interaction, user: discord.Member):
        await inter.response.defer()
        invoker = inter.user

        if not invoker.get_role(self.bot.config['roles']['admin'].id):
            await inter.response.send_message("You do not have permission to use this command!")
            return

        curs = await self.bot.db.find_one({"uid": user.id}, projection={"uid": 1})

        if curs is not None:
            message = "User already exists in the database!"
        else:
            await addd(bot=self.bot, member=user, logs=None)

            message = "User added to the database!"

        await inter.followup.send(message, ephemeral=True)

        await log(self.bot, inter, "Database Add", fields=[
            {"name": f"Moderator", "value": f"{invoker.mention} (`{invoker.id}`)", "inline": False},
            {"name": f"Member", "value": f"{user.mention} (`{user.id}`)", "inline": False}
        ])


async def setup(bot: 'Sassy'):
    await bot.add_cog(Add(bot))
