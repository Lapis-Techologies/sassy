from typing import TYPE_CHECKING
from discord import app_commands, Interaction
from discord.ext import commands
from utils.checks import db_check


if TYPE_CHECKING:
    from main import Sassy


class Link(commands.Cog):
    def __init__(self, bot: "Sassy") -> None:
        self.bot = bot
    
    @app_commands.command(name="link", description="Get a link to any of the shows!")
    @app_commands.checks.cooldown(1, 15, key=lambda i: (i.guild_id, i.user.id))
    @db_check()
    async def link(self, interaction: Interaction) -> None:
        message = f"""Sure thing mate!
[The Big Lez Show](<https://www.youtube.com/playlist?list=PLGMC7oz7XpmCR1RWxqvFWvXVO_ry6FdHI>)
[Sassy The Sasquatch](<https://www.youtube.com/playlist?list=PLGMC7oz7XpmDMGrALMQiNXCi9p7aqkWbj>)
[The Donny & Clarence Show](<https://www.youtube.com/playlist?list=PLGMC7oz7XpmCtkIuJWW4vUECBrw5iEIqn>)
[Mike Nolan's Long Weekend](<https://www.youtube.com/playlist?list=PLGMC7oz7XpmDxKSc2PsvNP4duszbU37Z0>)
[The Mike Nolan Show](<https://www.youtube.com/playlist?list=PLGMC7oz7XpmAt04pBS1kmYhCYr_NY7aOa>)
[Behind The Scenes](<https://www.youtube.com/playlist?list=PLGMC7oz7XpmAdRT_hd258YabkvM0BTMC9>)
"""

        await interaction.response.send_message(message, ephemeral=True)


async def setup(bot):
    await bot.add_cog(Link(bot))
