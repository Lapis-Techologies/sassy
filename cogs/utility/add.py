import discord
from typing import TYPE_CHECKING
from discord.ext import commands
from discord import User, app_commands, Interaction
from utils.adduser import add as add_
from utils.log import Importancy, LogType, log, Field
from utils.checks import is_admin


if TYPE_CHECKING:
    from main import Sassy


class Add(commands.Cog):
    def __init__(self, bot: 'Sassy'):
        self.bot = bot

    @app_commands.command(name="add", description="Adds a user to the database.")
    @is_admin()
    async def add(self, inter: Interaction, user: discord.Member):
        await inter.response.defer()
        invoker = inter.user

        if isinstance(invoker, User):
            return

        curs = await self.bot.user_db.find_one({"uid": user.id}, projection={"uid": 1})

        if curs is not None:
            message = "User already exists in the database!"
        else:
            await add_(bot=self.bot, member=user, logs=None)

            await log(self.bot, inter, LogType.DATABASE_ADD, fields=[
                Field("Moderator", f"{invoker.mention} (`{invoker.id}`)", False),
                Field("Member", f"{user.mention} (`{user.id}`)", False)
            ], importancy=Importancy.LOW)

            message = "User added to the database!"

        await inter.followup.send(message, ephemeral=True)



async def setup(bot: 'Sassy'):
    await bot.add_cog(Add(bot))
