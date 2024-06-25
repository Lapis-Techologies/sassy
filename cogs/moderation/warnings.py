import discord
from typing import TYPE_CHECKING
from discord.ext import commands
from discord import app_commands, Interaction, User
from utils.adduser import add


if TYPE_CHECKING:
    from main import Sassy


class Warnings(commands.Cog):
    def __init__(self, bot: "Sassy"):
        self.bot = bot

    @app_commands.command(name="warnings", description="Gets the warnings of a user.")
    async def warnings(self, inter: Interaction, user: discord.Member, case_id: str | None = None):
        await inter.response.defer()

        invoker = inter.user

        if isinstance(invoker, User):
            return

        admin = await self.bot.config.get("roles", "admin")

        if not invoker.get_role(admin):
            await inter.followup.send("You do not have permission to use this command!", ephemeral=True)
            return

        if case_id is not None:
            curs = await self.bot.user_db.find_one({"uid": user.id}, projection={"logs": 1})
            found = False

            if curs is None:
                await inter.followup.send("No warnings found for this user.", ephemeral=True)
                return

            for log in curs["logs"]:
                if log["case_id"] == case_id:
                    if log["action"] != "warn":
                        await inter.followup.send("This case ID is not a warning!", ephemeral=True)
                        return

                    embed = discord.Embed(
                        title=f"Warning for {user} ({user.id})",
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
                        value=log['timestamp'].date(),
                        inline=False
                    )

                    await inter.followup.send(embed=embed, ephemeral=True)
                    return

            if not found:
                await inter.followup.send("No warning found with that case ID.", ephemeral=True)
                return

        curs = await self.bot.user_db.find_one({"uid": user.id}, projection={"logs": 1})

        count = 0

        embed = discord.Embed(
            title=f"Warnings for {user} ({user.id})",
            color=discord.Color.red()
        )

        if curs is None:
            await add(bot=self.bot, member=user)
        else:
            for log in curs["logs"]:
                if log["action"] == "warn":
                    count += 1
                    embed.add_field(
                        name=f"Case ID: {log['case_id']}",
                        value=f"Reason: `{log['reason']}`",
                        inline=False
                    )

        embed.description = f"Total warnings: {count}"
        await inter.followup.send(embed=embed, ephemeral=True)


async def setup(bot: 'Sassy'):
    await bot.add_cog(Warnings(bot))
