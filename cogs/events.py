import discord
from time import time
from random import randint
from typing import TYPE_CHECKING
from discord.ext import commands
from discord import app_commands, Interaction, Embed
from utils.adduser import add
from utils.log import log


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

        await add(bot=self.bot, member=member)

    @commands.Cog.listener()
    async def on_message(self, message: discord.Message):
        if message.author.bot:
            return

        curs = await self.bot.db.find_one({"uid": message.author.id}, projection={"xp": 1, "level": 1, "last_message": 1})

        if curs is None:
            await add(self.bot, message.author)

        last_message = curs["last_message"]

        if time() > last_message:
            last_message = time() + 8   # +8 seconds
        else:
            return

        xp = curs["xp"]
        xp += randint(5, 12)

        level = curs["level"]
        xp_needed = 100 + (level - 1) * 50

        if xp >= xp_needed:
            level += 1
            xp -= xp_needed
            xp_needed = 100 + (level - 1) * 50

            progress = min(10, int(1 + (xp * 10) / xp_needed))

            bar = "ERROR CALCULATING PROGRESS"
            if progress == 10:
                bar = "🟩" * 10
            elif progress == 9:
                bar = "🟩" * 9 + "🟨"
            elif progress <= 8:
                bar = "🟩" * progress + "🟨" + "🟥" * ((10 - progress) - 1)

            embed = Embed(title="Level Up!", description=f"Holy shit mate you leveled up to level **{level}**",
                          color=0x00FF00)

            embed.add_field(name="XP Progress", value=f"**{xp}** > {bar} < **{xp_needed}**")

            await message.channel.send(f"{message.author.mention}", embed=embed)

            for lvl, reward in self.bot.config["xp"]["rewards"].items():
                if level == int(lvl):
                    # User has earned a new reward!
                    await message.author.add_roles(reward)

        await self.bot.db.update_one({"uid": message.author.id}, {
            "$set": {
                "xp": xp,
                "level": level,
                "last_message": last_message
            }
        })

    @commands.Cog.listener()
    async def on_message_edit(self, before: discord.Message, after: discord.Message):
        if before.author.bot:
            return

        await log(self.bot, None, "edit", fields=[
            {"name": "User", "value": f"{before.author.mention} (`{before.author.id}`)", "inline": False},
            {"name": "Before", "value": f"```{before.content}```", "inline": False},
            {"name": "After", "value": f"```{after.content}```", "inline": False},
            {"name": "Jump Link", "value": after.jump_url, "inline": False}
        ])

    @commands.Cog.listener()
    async def on_message_delete(self, message: discord.Message):
        if message.author.bot:
            return

        await log(self.bot, None, "delete", fields=[
            {"name": "User", "value": f"{message.author.mention} (`{message.author.id}`)", "inline": False},
            {"name": "Content", "value": f"```{message.content}```", "inline": False},
        ])


async def setup(bot):
    await bot.add_cog(Events(bot))
