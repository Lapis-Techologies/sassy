import discord
from typing import TYPE_CHECKING
from discord.ext import commands
from discord import app_commands, Interaction


if TYPE_CHECKING:
    from main import Sassy


class Help(commands.Cog):
    def __init__(self, bot: "Sassy"):
        self.bot = bot

    @app_commands.command(name="help", description="Get help on a command.")
    @app_commands.checks.cooldown(1, 15, key=lambda i: (i.guild_id, i.user.id))
    async def help(self, inter: Interaction):
        await inter.response.defer()

        embed = discord.Embed(
            title="Help",
            description="Lists all of the commands.",
            color=discord.Color.blurple()
        )

        cmds = [com for com in self.bot.tree.walk_commands() if isinstance(com, app_commands.Command)]
        groups = [com for com in self.bot.tree.walk_commands() if isinstance(com, app_commands.Group)]

        for slash_command in cmds:
            embed.add_field(
                name=slash_command.name,
                value=slash_command.description if slash_command.description else "No description provided.",
                inline=False
            )

        embeds = [embed]

        for group_command in groups:
            emb = discord.Embed(
                title=group_command.name,
                description=group_command.description if group_command.description else "No description provided.",
                color=discord.Color.blurple()
            )

            for sub_command in group_command.commands:
                emb.add_field(
                    name=sub_command.name,
                    value=sub_command.description if sub_command.description else "No description provided.",
                    inline=False
                )
            embeds.append(emb)

        await inter.followup.send(embeds=embeds, ephemeral=True)


async def setup(bot: "Sassy"):
    await bot.add_cog(Help(bot))
