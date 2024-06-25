import discord
from typing import TYPE_CHECKING
from discord.ext import commands
from discord import app_commands, Interaction, User
from utils.adduser import add


if TYPE_CHECKING:
    from main import Sassy


class Mutes(commands.Cog):
    def __init__(self, bot: "Sassy"):
        self.bot = bot

    @app_commands.command(name="mutes", description="View all mutes for a specified user.")
    async def mutes(self, inter: Interaction, member: discord.Member, case_id: str | None = None):
        await inter.response.defer()

        invoker = inter.user

        if isinstance(invoker, User):
            return

        admin = await self.bot.config.get("roles", "admin")

        if not invoker.get_role(admin):
            await inter.followup.send("You do not have permission to use this command!", ephemeral=True)
            return

        curs = None

        if case_id is not None:
            curs = await self.bot.user_db.find_one({"uid": member.id}, projection={"logs": 1})

        if curs is None:
            await inter.followup.send("No mutes found for this user.", ephemeral=True)
            return

        for log in curs["logs"]:
            if log["case_id"] == case_id:
                if log["action"] != "mute":
                    await inter.followup.send("This case ID is not a mute!", ephemeral=True)
                    return

                embed = discord.Embed(
                    title=f"Mute for {member} ({member.id})",
                    color=discord.Color.red()
                )

                embed.add_field(
                    name="Reason",
                    value=f"`{log['reason']}`",
                    inline=False
                )

                embed.add_field(
                    name="Moderator",
                    value=f"<@{log['moderator']}>",
                    inline=False
                )

                embed.add_field(
                    name="Case ID",
                    value=log["case_id"],
                    inline=False
                )

                embed.add_field(
                    name="Date",
                    value=log["timestamp"],
                    inline=False
                )

                await inter.followup.send(embed=embed, ephemeral=True)
                return

            await inter.followup.send("No mutes found for this user.", ephemeral=True)
            return

        curs = await self.bot.user_db.find_one({"uid": member.id}, projection={"logs": 1})

        if curs is None:
            await inter.followup.send("No mutes found for this user.", ephemeral=True)

            await add(bot=self.bot, member=member)

            return

        embed = discord.Embed(
            title=f"Mutes for {member} ({member.id})",
            color=discord.Color.red()
        )

        count = 0

        for log in curs["logs"]:
            if log["action"] == "mute":
                count += 1

                embed.add_field(
                    name=f"Case ID: {log['case_id']}",
                    value=f"Reason: `{log['reason']}`\nModerator: <@{log['moderator']}>\nDate: {log['timestamp']}",
                    inline=False
                )

        if count == 0:
            await inter.followup.send("No mutes found for this user.", ephemeral=True)
            return

        embed.description = f"Total Mutes: {count}"

        await inter.followup.send(embed=embed, ephemeral=True)


async def setup(bot: "Sassy"):
    await bot.add_cog(Mutes(bot))
