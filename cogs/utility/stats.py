import os
from typing import TYPE_CHECKING
from discord.ext import commands
from discord import app_commands, Interaction
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


async def setup(bot: "Sassy"):
    await bot.add_cog(Stats(bot))
