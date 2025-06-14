from typing import TYPE_CHECKING
from json import load
from discord import Embed, app_commands, Interaction
from discord.ext import commands
from utils.checks import db_check


if TYPE_CHECKING:
    from main import Sassy


class Rules(commands.Cog):
    def __init__(self, bot: "Sassy"):
        self.bot = bot

    @app_commands.command(name="rules", description="Post the rules")
    @app_commands.checks.cooldown(1, 40, key=lambda i: (i.guild_id, i.user.id))
    @db_check()
    async def ping(self, inter: Interaction):
        with open("./resources/rules.json", "r") as f:
            rules: list[dict[str, str]] = load(f)

        embed = Embed(title="Rules", color=0x17FF77)
        embed.set_thumbnail(
            url="https://cdn.discordapp.com/attachments/1254314000347435090/1254545696187482263/lez_6011.png?ex=6679e23a&is=667890ba&hm=4c4c774ac8750b3e4648fc5e0b18cd9c07d194732580d755695fa26fde4626ad&"
        )

        for i, entry in enumerate(rules):
            rule = next(iter(entry))
            details = entry[rule]
            embed.add_field(name=f"{i + 1}. {rule}", value=details, inline=False)

        await inter.response.send_message(embed=embed)


async def setup(bot: "Sassy"):
    await bot.add_cog(Rules(bot))
