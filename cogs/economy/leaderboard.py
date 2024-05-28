from typing import TYPE_CHECKING
from discord import app_commands, Interaction, Embed
from discord.ext import commands


if TYPE_CHECKING:
    from main import Sassy


class Leaderboard(commands.Cog):
    def __init__(self, bot: 'Sassy'):
        self.bot = bot

    @app_commands.command(name="leaderboard", description="Shows the top leaderboard for who has the most choomah coins")
    @app_commands.checks.cooldown(1, 15, key=lambda i: (i.guild_id, i.user.id))
    async def leaderboard(self, inter: Interaction):
        curs = self.bot.db.aggregate([
            {"$sort": {"choomah_coins": -1}},
            {"$limit": 10},
            {"$project": {"choomah_coins": 1, "uid": 1}}
        ])

        embed = Embed(title="Leaderboard - Choomah Coins", description="Top 10 Users - Choomah Coins", color=0x00FF00)

        i = 1

        for entry in await curs.to_list(length=None):
            user = self.bot.get_user(entry["uid"])
            if user is None:
                continue

            coins = entry["choomah_coins"]

            embed.add_field(name=f"{i}. {user.name}", value=f"Choomah Coins: ***{coins}***", inline=False)

            i += 1

        curs = self.bot.db.aggregate([
            {"$sort": {"level": -1}},
            {"$limit": 10},
            {"$project": {"level": 1, "uid": 1}}
        ])

        embed2 = Embed(title="Leaderboard - Levels", description="Top 10 Users - Levels")

        i = 1

        for entry in await curs.to_list(length=None):
            user = self.bot.get_user(entry["uid"])
            if user is None:
                continue

            level = entry["level"]

            embed2.add_field(name=f"{i}. {user.name}", value=f"Level: ***{level}***", inline=False)

            i += 1

        await inter.response.send_message(embeds=[embed, embed2])


async def setup(bot):
    await bot.add_cog(Leaderboard(bot))
