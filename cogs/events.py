import discord
from time import time
from typing import TYPE_CHECKING
from discord.ext import commands
from discord import app_commands, Interaction

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
        await self.bot.config["channels"]["welcome"].send(f"Whats goin on mate? You're druggo #{len(member.guild.members)}, fuckin skits mate")

        await self.bot.db.insert_one({
            "uid": member.id,
            "choomah_coins": 0,
            "logs": []
        })


async def setup(bot):
    await bot.add_cog(Events(bot))
