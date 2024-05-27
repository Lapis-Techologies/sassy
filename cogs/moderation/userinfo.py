import discord
from typing import TYPE_CHECKING
from discord.ext import commands
from discord import app_commands, Interaction
from utils.IGNORE_adduser import add


if TYPE_CHECKING:
    from main import Sassy


class UserInfo(commands.Cog):
    def __init__(self, bot: 'Sassy'):
        self.bot = bot

    @app_commands.command(name="userinfo", description="View information about a specified user.")
    async def userinfo(self, inter: Interaction, member: discord.Member):
        await inter.response.defer()

        invoker = inter.user

        if not invoker.get_role(self.bot.config['roles']['admin'].id):
            await inter.followup.send("You do not have permission to use this command!", ephemeral=True)
            return

        embed = discord.Embed(
            title=f"User Information for {member} ({member.id})",
            color=discord.Color.green()
        )

        embed.set_thumbnail(url=member.avatar.url)

        curs = await self.bot.db.find_one({"uid": member.id}, projection={"logs": 1})

        if curs is None:
            await add(bot=self.bot, member=user)

            embed.add_field(name="Choomah Coins", value="0", inline=False)
            embed.add_field(name="Logs", value="No logs found for this user.", inline=False)

            await inter.followup.send(embed=embed, ephemeral=True)
            return

        embeds = [embed]

        fields = 0  # Discord embeds have a limit of 25 fields, so we need to keep track of how many fields we've added.
        logs = curs["logs"]

        if len(logs) == 0:
            embed.add_field(name="Choomah Coins", value="0", inline=False)
            embed.add_field(name="Logs", value="No logs found for this user.", inline=False)

            await inter.followup.send(embed=embed, ephemeral=True)
            return

        for log in logs:
            if fields == 25:
                embeds.append(embed)
                embed = discord.Embed(
                    title=f"User Information for {member} ({member.id}) - Continued",
                    color=discord.Color.green()
                )

                fields = 0

            embed.add_field(
                name=f"Case ID: {log['case_id']}",
                value=f"Action: {log['action']}\nReason: `{log['reason']}`\nModerator: <@{log['moderator']}>\nTimestamp: {log['timestamp'].date()}",
                inline=False
            )

            fields += 1

        await inter.followup.send(embeds=embeds, ephemeral=True)


async def setup(bot: 'Sassy'):
    await bot.add_cog(UserInfo(bot))
