import discord
from typing import TYPE_CHECKING
from discord.ext import commands
from discord import app_commands, Interaction
from utils.checks import db_check, is_admin
from utils.log import LogType


if TYPE_CHECKING:
    from main import Sassy


class Warnings(commands.Cog):
    def __init__(self, bot: "Sassy"):
        self.bot = bot
        self.user_db = self.bot.database["user"]

    async def find_case_by_id(self, case_id, interaction, member):
        curs = await self.user_db.find_one(
            {"uid": member.id},
            projection={"logs": {"$elemMatch": {"case_id": case_id}}},
        )
        if curs is None:
            embed = discord.Embed(
                title="No Warnings Found",
                description=f"{member.mention} does not have any warnings on record!",
                color=0x00FF00,
            )
            await interaction.followup.send(embed=embed)
            return

        embed = discord.Embed(title=f"Warning Case for {member.name}")

        reason = curs["reason"]
        moderator = self.bot.get_user(curs["moderator"])

        embed.add_field(name="Case ID", value=f"`{case_id}`")
        embed.add_field(
            name="Moderator",
            value=moderator.mention
            if moderator is not None
            else f"<@{moderator}>  (`{moderator}`)",
        )
        embed.add_field(name="Reason", value=f"```{reason}```", inline=False)

        await interaction.followup.send(embed=embed)
        return

    async def find_warnings(self, member, interaction) -> None:
        pipeline = [
            {"$match": {"uid": member.id}},
            {
                "$project": {
                    "logs": {
                        "$filter": {
                            "input": "$logs",
                            "as": "log",
                            "cond": {"$eq": ["$$log.action", LogType.WARN.value]},
                        }
                    }
                }
            },
        ]
        users = await self.user_db.aggregate(pipeline)
        users = await users.to_list(None)
        cases = [log for user in users for log in user.get("logs", [])]

        if not cases:
            embed = discord.Embed(
                title="No Warnings Found",
                description=f"{member.mention} does not have any warnings on record!",
                color=0x00FF00,
            )
            await interaction.followup.send(embed=embed)
            return

        embed = discord.Embed(
            title=f"Warnings for {member} ({member.id})", color=0xFF0000
        )
        count = 0

        for log in cases:
            count += 1
            case_id = log["case_id"]
            reason = log["reason"]
            date = log["timestamp"]
            mod = log["moderator"]
            embed.add_field(
                name=f"Case ID: {case_id}",
                value=f"Reason: `{reason}`\nModerator: {mod}\nDate: {date}",
            )

        embed.set_footer(text=f"Total Mute Count: {count}")
        await interaction.followup.send(embed=embed)

    @app_commands.command(
        name="warnings", description="View all warnings for a specific user."
    )
    @db_check()
    @is_admin()
    async def warnings(
        self,
        interaction: Interaction,
        member: discord.Member,
        case_id: str | None = None,
    ) -> None:
        await interaction.response.defer()

        if case_id:
            await self.find_case_by_id(case_id, interaction, member)

        await self.find_warnings(member, interaction)


async def setup(bot: "Sassy"):
    await bot.add_cog(Warnings(bot))
