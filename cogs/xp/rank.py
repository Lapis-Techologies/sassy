from typing import TYPE_CHECKING
from discord import Embed, Interaction, Member, app_commands
from discord.ext import commands
from utils.checks import db_check
from .xphandler import XPHandler


if TYPE_CHECKING:
    from main import Sassy


class Rank(commands.Cog):
    def __init__(self, bot: "Sassy") -> None:
        self.bot = bot
        self.user_db = self.bot.database["user"]

    @app_commands.command(
        name="rank", description="Check yours (or another person's) rank."
    )
    @db_check()
    async def rank(self, interaction: Interaction, member: Member) -> None:
        curs = await self.user_db.find_one(
            {"uid": member.id}, projection={"xp": 1, "level": 1, "bumps": 1}
        )
        xp = curs["xp"]
        level = curs["level"]
        bumps = curs["bumps"]
        new_xp = XPHandler.calculate_xp(level + 1)
        progress = XPHandler.calculate_progress(xp, new_xp)
        bar = XPHandler.make_bar(progress)

        embed = Embed(title=f"Rank - {member.name}", color=0x0077FF)
        embed.add_field(name="Rank", value=level)
        embed.add_field(name="XP", value=xp)
        embed.add_field(name="Bumps", value=bumps)
        embed.add_field(name="Progress", value=f"{xp} > {bar} < {new_xp}")

        await interaction.response.send_message(embed=embed)


async def setup(bot):
    await bot.add_cog(Rank(bot))
