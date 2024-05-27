import discord
from typing import TYPE_CHECKING
from discord.ext import commands
from discord import app_commands, Interaction


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
            self.bot.db.insert_one({
                "uid": user.id,
                "choomah_coins": 0,
                "logs": []
            })

            message = "User added to the database!"

        await inter.followup.send(message, ephemeral=True)


async def setup(bot: 'Sassy'):
    await bot.add_cog(Add(bot))
