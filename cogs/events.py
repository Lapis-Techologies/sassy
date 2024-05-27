import discord
from time import time
from typing import TYPE_CHECKING
from discord.ext import commands
from discord import app_commands, Interaction
from utils.IGNORE_adduser import add


if TYPE_CHECKING:
    from main import Sassy


class Events(commands.Cog):
    def __init__(self, bot: "Sassy"):
        self.bot = bot
        self._old_tree_error = None

    def cog_load(self):
        tree = self.bot.tree
        self._old_tree_error = tree.on_error
        tree.on_error = self.on_slash_error

    def cog_unload(self):
        tree = self.bot.tree
        tree.on_error = self._old_tree_error

    async def on_slash_error(self, inter: Interaction, error: app_commands.AppCommandError):    # noqa
        if isinstance(error, app_commands.CommandNotFound):
            await inter.response.send_message("Command not found!")
        elif isinstance(error, app_commands.CommandOnCooldown):
            time_left = int(error.cooldown.get_retry_after())
            length = int(time()) + time_left
            formatted_time = f"<t:{length}:R>"
            await inter.response.send_message(f"Command is on cooldown! (Ends {formatted_time})")
        elif isinstance(error, app_commands.CheckFailure):
            await inter.response.send_message("You do not have permission to use this command!")
        else:
            await inter.response.send_message(f"An error occurred! {error}")

    @commands.Cog.listener()
    async def on_member_join(self, member: discord.Member):
        await self.bot.config["channels"]["welcome"].send(f"{member.mention} Whats goin on mate? You're druggo #{len(member.guild.members)}, fuckin skits mate")

        await add(bot=self.bot, member=member, xp=0, level=0,choomah_coins=0, logs=None)

    @commands.Cog.listener()
    async def on_message(self, message: discord.Message):
        if message.author.bot:
            return




async def setup(bot):
    await bot.add_cog(Events(bot))
