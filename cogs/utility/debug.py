from typing import TYPE_CHECKING
from discord import app_commands, Interaction, Embed
from discord.ext import commands
from _stats import ProjectReader


if TYPE_CHECKING:
    from main import Sassy


class Debug(commands.Cog):
    def __init__(self, bot: 'Sassy'):
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
            '.env.example',
            '.venv',
            'dev',
            *self.bot.IGNORE_COMMANDS
        )


    @commands.is_owner()
    @app_commands.command(name="debug", description="Gives some general information about the bots status")
    async def debug(self, inter: Interaction):
        await inter.response.defer()
        if self.bot.user is None:
            return
        if self.bot.user.avatar is None:
            return
        
        embed = Embed(title="Debug", description="General Information about the bot's status", color=0x7799FF)

        name = self.bot.user.name
        id_ = self.bot.user.id
        version = self.bot.version
        guilds = len(self.bot.guilds)
        users = len(self.bot.users)
        cmds = len([com for com in self.bot.tree.walk_commands() if isinstance(com, app_commands.Command)])
        pfp = self.bot.user.avatar.url or self.bot.user.display_avatar.url or self.bot.user.default_avatar.url
        stats = ProjectReader(banned=self.banned).project_stats().replace('-', '')

        embed.add_field(name="Bot Name", value=name)
        embed.add_field(name="Bot ID", value=id_)
        embed.add_field(name="Bot Version", value=version)
        embed.add_field(name="Guilds", value=guilds)
        embed.add_field(name="Users", value=users)
        embed.add_field(name="Commands", value=cmds)
        embed.add_field(name="Stats", value=stats)
        embed.set_thumbnail(url=pfp) if pfp is not None else None

        await inter.followup.send(embed=embed, ephemeral=True)


async def setup(bot: 'Sassy'):
    await bot.add_cog(Debug(bot))
