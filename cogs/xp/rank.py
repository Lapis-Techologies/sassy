from typing import TYPE_CHECKING
from discord import Embed, app_commands, Interaction, User, Member
from discord.ext import commands
from utils.adduser import add


if TYPE_CHECKING:
    from main import Sassy


class Rank(commands.Cog):
    def __init__(self, bot: 'Sassy'):
        self.bot = bot

    @app_commands.command(name="rank", description="Check the your or another user's level")
    async def level(self, inter: Interaction, member: Member | User | None = None):
        if member is None:
            member = inter.user

        curs = await self.bot.user_db.find_one({"uid": member.id}, projection={"xp": 1, "level": 1})

        if curs is None:
            await add(bot=self.bot, member=member)
            embed = Embed(title=f"Level {member.name} ({member.id})")
            embed.add_field(name="Level", value="**0**")
            embed.add_field(name="XP", value="**0**")

            xp = 0
            level = 1

            xp_needed = 100 + (level - 1) * 50
            progress = min(10, int(1 + (xp * 10) / xp_needed))

            bar = "ERROR CALCULATING PROGRESS"
            if progress == 10:
                bar = "🟩" * 10
            elif progress == 9:
                bar = "🟩" * 9 + "🟨"
            elif progress <= 8:
                bar = "🟩" * progress + "🟨" + "🟥" * ((10 - progress) - 1)

            embed.add_field(name="XP Progress", value=f"**{xp}** > {bar} < **{xp_needed}**", inline=False)
        else:
            xp = curs["xp"]
            level = curs["level"]

            xp_needed = 100 + (level - 1) * 50
            progress = min(10, int(1 + (xp * 10) / xp_needed))

            bar = "ERROR CALCULATING PROGRESS"
            if progress == 10:
                bar = "🟩" * 10
            elif progress == 9:
                bar = "🟩" * 9 + "🟨"
            elif progress <= 8:
                bar = "🟩" * progress + "🟨" + "🟥" * ((10 - progress) - 1)

            embed = Embed(title=f"Level {member.name} ({member.id})")
            embed.add_field(name="Level", value=f"**{level}**")
            embed.add_field(name="XP", value=f"**{xp}**")
            embed.add_field(name="XP Progress", value=f"**{xp}** > {bar} < **{xp_needed}**", inline=False)

        await inter.response.send_message(embed=embed)


async def setup(bot):
    await bot.add_cog(Rank(bot))
