import discord
from typing import TYPE_CHECKING
from discord.ext import commands
from discord import app_commands, Interaction
from utils.adduser import add
from utils.checks import is_admin, db_check


if TYPE_CHECKING:
    from main import Sassy


class UserInfo(commands.Cog):
    def __init__(self, bot: "Sassy"):
        self.bot = bot
        self.user_db = self.bot.database["user"]

    def make_embeds(self, logs, member, embed) -> list[discord.Embed]:
        embeds = []

        for log in logs:
            if len(embed.fields) == 9:
                embeds.append(embed)
                embed = discord.Embed(
                    title=f"User Information for {member} ({member.id}) - Continued",
                    color=0x00FF00,
                )

            case_id = log["case_id"]
            action = log["action"]
            reason = log["reason"]
            moderator = log["moderator"]
            timestamp = log["timestamp"].date()

            embed.add_field(
                name=f"Case ID: {case_id}",
                value=f"Action: `{action}`\nReason: `{reason}`\nModerator: <@{moderator}>\nTimestamp: `{timestamp}`",
                inline=False,
            )

        if embed not in embeds:
            embeds.append(embed)

        return embeds

    @app_commands.command(
        name="userinfo", description="View information about a specified user."
    )
    @app_commands.describe(member="The member to get info about.")
    @db_check()
    @is_admin()
    async def userinfo(self, interaction: Interaction, member: discord.Member):
        await interaction.response.defer()

        embed = discord.Embed(
            title=f"User Information for {member} ({member.id})", color=0x00FF00
        )
        embed.set_thumbnail(
            url=member.avatar.url or member.default_avatar.url
        ) if member.avatar is not None else None

        curs = await self.user_db.find_one({"uid": member.id}, projection={"logs": 1})

        if curs is None:
            await add(bot=self.bot, member=member)

            embed.add_field(name="Choomah Coins", value="0", inline=False)
            embed.add_field(
                name="Logs", value="No logs found for this user.", inline=False
            )

            await interaction.followup.send(embed=embed)
            return

        logs = curs["logs"]
        if len(logs) == 0:
            embed.add_field(name="Choomah Coins", value="0", inline=False)
            embed.add_field(
                name="Logs", value="No logs found for this user.", inline=False
            )

            await interaction.followup.send(embed=embed)
            return

        embeds = self.make_embeds(logs, member, embed)

        for embed in embeds:
            await interaction.followup.send(embed=embed)


async def setup(bot: "Sassy"):
    await bot.add_cog(UserInfo(bot))
