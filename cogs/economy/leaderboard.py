from typing import TYPE_CHECKING
from discord import app_commands, Interaction, Embed
from discord.ext import commands
from utils.checks import db_check


if TYPE_CHECKING:
    from main import Sassy


class Leaderboard(commands.Cog):
    def __init__(self, bot: "Sassy"):
        self.bot = bot
        self.user_db = self.bot.database["user"]
        self.level_multiplier = float(self.bot.config.get("xp", "multipliers", "level"))
        self.choomah_coin_multiplier = float(
            self.bot.config.get("xp", "multipliers", "choomah_coins")
        )
        self.bumps_multiplier = float(self.bot.config.get("xp", "multipliers", "bumps"))

    async def top(self, amount: int) -> Embed:
        curs = await self.user_db.aggregate(
            [
                {
                    "$addFields": {
                        "overall_score": {
                            "$round": [
                                {
                                    "$add": [
                                        {
                                            "$multiply": [
                                                "$level",
                                                self.level_multiplier,
                                            ]
                                        },
                                        {
                                            "$multiply": [
                                                "$choomah_coins",
                                                self.choomah_coin_multiplier,
                                            ]
                                        },
                                        {
                                            "$multiply": [
                                                "$bumps",
                                                self.bumps_multiplier,
                                            ]
                                        },
                                    ]
                                },
                                2,
                            ]
                        }
                    }
                },
                {"$sort": {"overall_score": -1}},
                {"$limit": amount},
                {"$project": {"uid": 1, "overall_score": 1}},
            ]
        )
        embed = Embed(
            title="Leaderboard",
            description=f"Top {amount} Users",
            color=0x00FF00,
        )

        for i, entry in enumerate(await curs.to_list(length=None)):
            user = self.bot.get_user(entry["uid"])
            if user is None:
                continue

            embed.add_field(
                name=f"{i + 1}. {user.name}",
                value=f"Score: ***{round(float(entry['overall_score']), 2)}***",
                inline=False,
            )

        return embed

    @app_commands.command(
        name="leaderboard",
        description="Shows the top leaderboard for who has the most choomah coins",
    )
    @app_commands.checks.cooldown(1, 15, key=lambda i: (i.guild_id, i.user.id))
    @db_check()
    async def leaderboard(self, interaction: Interaction) -> None:
        embed = await self.top(10)
        await interaction.response.send_message(embed=embed)


async def setup(bot):
    await bot.add_cog(Leaderboard(bot))
