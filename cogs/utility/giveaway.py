from typing import TYPE_CHECKING
from discord import app_commands, Interaction, Embed
from discord.ext import commands
from utils.checks import db_check


if TYPE_CHECKING:
    from main import Sassy


class Giveaway(commands.Cog):
    def __init__(self, bot: "Sassy"):
        self.bot = bot
        self.giveaways = self.bot.database["giveaways"]
        self.MAX_PRIZE_LEN = 200

    @app_commands.command(
        name="giveaway",
        description="Create a giveaway with a variable amount of winners.",
    )
    @app_commands.describe(
        time="The amount of time, in minutes, the giveaway should last.",
        prize="The prize the winner(s) will receive.",
        winners="The amount of winners.",
    )
    @app_commands.checks.cooldown(1, 300, key=lambda i: (i.guild_id, i.user.id))
    @db_check()
    async def giveaway(self, interaction: Interaction, time: int, prize: str,
                       winners:
    int = 1):
        await interaction.response.defer()
        if winners <= 0:
            await interaction.followup.send(
                "You must have at least 1 winner.", ephemeral=True
            )
            return
        elif winners > 20:
            await interaction.followup.send(
                "You cannot have more than 20 winners.", ephemeral=True
            )
            return

        prize = self._block_mentions(self._clean_prize(prize))

        if time > 20160: # 2 weeks
            await interaction.followup.send("Sorry m8, Giveaways can only last "
                                            "up to "
                                            "2 week.")
            return

        seconds = time * 60

        end_date = interaction.created_at.timestamp() + seconds

        embed = Embed(
            title="Giveaway 🎊", description=f"{interaction.user.mention} has "
                                            f"created a new giveaway!",
            color=0x3399FF
        )
        embed.add_field(
            name="Prize",
            value=f"**{prize}**"
        )
        embed.add_field(
            name="Winners",
            value=f"**{winners}**"
        )

        message = await interaction.followup.send(
            f"This giveaway ends <t:{int(end_date)}:R>", embed=embed, wait=True
        )
        await message.add_reaction("🎉")

        giveaway_document = await self.giveaways.insert_one(
            {
                "creator": interaction.user.id,
                "winners": winners,
                "channel": interaction.channel_id,
                "message": message.id,
                "prize": prize,
                "end_date": end_date,
                "finished": False,  # Check for the bot to see if it has
                # finished it or not, see utils/tasks/giveaway_watcher.py
            }
        )

        self.bot.giveaway_watcher.watch_event(giveaway_document)

    def _clean_prize(self, prize: str) -> str:
        prize = prize.strip()
        if len(prize) > self.MAX_PRIZE_LEN:
            raise ValueError(
                f"Prize must be under {self.MAX_PRIZE_LEN} characters."
            )
        if "$" in prize or "." in prize:
            raise ValueError(
                "Question cannot contain '$' or '.' (MongoDB restriction)."
            )
        return prize

    @staticmethod
    def _block_mentions(text: str) -> str:
        return text.replace("@everyone", "[everyone]").replace("@here", "[here]")


async def setup(bot: "Sassy"):
    await bot.add_cog(Giveaway(bot))
