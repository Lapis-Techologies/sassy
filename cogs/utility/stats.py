import os
from typing import TYPE_CHECKING
from discord.ext import commands
from discord import app_commands, Interaction, Embed
from _stats import ProjectReader


if TYPE_CHECKING:
    from main import Sassy


class Stats(commands.Cog):
    def __init__(self, bot: "Sassy"):
        self.bot = bot
        self.banned = (
            'venv',
            '.idea',
            '__pycache__',
            '_stats.py',
            '.gitignore',
            '.git',
            '.vscode',
            '.gitattributes',
            '.gitmodules',
            'LICENSE',
            'README.md',
            'config.json.example',
            '.env.example'
        )
        self.path = os.getcwd()

        self.pr = ProjectReader(banned=self.banned, path=self.path)

    @commands.is_owner()
    @app_commands.command(name="stats", description="Get stats the bot.")
    async def stats(self, inter: Interaction):
        await inter.response.defer()
        await inter.followup.send(f"```{self.pr.project_stats().replace('-', '')}```", ephemeral=True)

    @commands.is_owner()
    @app_commands.command(name="testxp")
    async def testxp(self, inter: Interaction, xp: int, level: int):
        xp_needed = int((4*(level**3))/5)
        if xp_needed == 0:
            xp_needed = 1
        progress = int(((xp - 0) / (xp_needed - 0)) * (10 - 1) + 1)

        bar = None
        if progress == 10:
            bar = "🟩" * 10
        elif progress == 9:
            bar = "🟩" * 9 + "🟨"
        elif progress <= 8:
            bar = "🟩" * progress + "🟨" + "🟥" * ((10 - progress) - 1)

        embed = Embed(title="Level Up!", description=f"Holy shit mate you leveled up to level **{level}**", color=0x00FF00)

        embed.add_field(name="XP Progress", value=f"**{xp}** > {bar} < **{xp_needed}**")

        await inter.response.send_message(f"```{xp_needed=}\n{progress=}```", embed=embed)


async def setup(bot: "Sassy"):
    await bot.add_cog(Stats(bot))
