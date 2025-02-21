from typing import TYPE_CHECKING
from discord import app_commands, Interaction, Embed
from discord.ext import commands
from utils.checks import db_check


if TYPE_CHECKING:
    from main import Sassy


class Leaderboard(commands.Cog):
    def __init__(self, bot: 'Sassy'):
        self.bot = bot

    async def top(self, amount: int, search: str) -> Embed:
        curs = self.bot.user_db.aggregate([
            {"$sort": {search: -1}},
            {"$limit": amount},
            {"$project": {search: 1, "uid": 1}}
        ])

        embed = Embed(title=f"Leaderboard - {search.replace("_", " ").title()}", description=f"Top {amount} Users", color=0x00FF00)

        i = 1
        for entry in await curs.to_list(length=None):
            user = self.bot.get_user(entry["uid"])
            if user is None:
                continue

            value = entry[search]
            embed.add_field(name=f"{i}. {user.name}", value=f"{search.replace("_", " ").title()}: ***{value}***", inline=False)
            i += 1

        return embed

    @app_commands.command(name="leaderboard", description="Shows the top leaderboard for who has the most choomah coins")
    @app_commands.checks.cooldown(1, 15, key=lambda i: (i.guild_id, i.user.id))
    @db_check()
    async def leaderboard(self, inter: Interaction) -> None:
        choomah_coins = await self.top(10, "choomah_coins")
        levels = await self.top(10, "level")

        await inter.response.send_message(embeds=[choomah_coins, levels])


async def setup(bot):
    await bot.add_cog(Leaderboard(bot))
